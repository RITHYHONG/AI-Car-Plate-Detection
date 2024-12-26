import cv2
import numpy as np
from app.models import get_detector, get_ocr_model
from app.utils.preprocess import preprocess_image
from app.utils.ticket import generate_ticket
from app.database.models import Detection, db
from datetime import datetime
import logging
import os

class Camera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.detector = get_detector()
        self.ocr = get_ocr_model()
        
        # Ensure logging directory exists
        log_dir = 'app/logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=os.path.join(log_dir, 'detection.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None
        
        # Process frame
        processed_frame = self._process_frame(frame)
        
        # Convert to JPEG
        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()
    
    def _process_frame(self, frame):
        # Detect license plates
        detections = self.detector.detect(frame)
        
        for detection in detections:
            x, y, w, h = detection['box']
            # Crop and process license plate region
            plate_img = frame[y:y+h, x:x+w]
            processed_plate = preprocess_image(plate_img)
            
            # Perform OCR
            plate_text = self.ocr.read_text(processed_plate)
            
            if plate_text:
                # Draw detection on frame
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, plate_text, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                # Log detection
                self._log_detection(plate_text, frame[y:y+h, x:x+w])
        
        return frame
    
    def _log_detection(self, plate_text, plate_img):
        try:
            # Generate ticket
            ticket_id = generate_ticket(plate_text)
            
            # Save to database
            detection = Detection(
                plate_number=plate_text,
                ticket_id=ticket_id,
                timestamp=datetime.utcnow()
            )
            db.session.add(detection)
            db.session.commit()
            
            # Log to file
            logging.info(f"Detected plate: {plate_text}, Ticket ID: {ticket_id}")
            
            # Save plate image
            img_path = f"app/static/uploads/{ticket_id}.jpg"
            cv2.imwrite(img_path, plate_img)
            
        except Exception as e:
            logging.error(f"Error logging detection: {str(e)}")
            db.session.rollback()
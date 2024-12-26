from flask import current_app
from app.models.ocr import OCR
import cv2

_detector = None
_ocr = None

def get_detector():
    global _detector
    if _detector is None:
        # Initialize OpenCV cascade classifier
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')
        
        class Detector:
            def detect(self, image):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                plates = cascade.detectMultiScale(gray, 1.1, 4)
                
                detections = []
                for (x, y, w, h) in plates:
                    detections.append({
                        'box': (x, y, w, h),
                        'confidence': 1.0  # Placeholder confidence
                    })
                return detections
        
        _detector = Detector()
    return _detector

def get_ocr_model():
    global _ocr
    if _ocr is None:
        _ocr = OCR()
    return _ocr
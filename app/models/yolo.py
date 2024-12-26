import cv2
import numpy as np
from flask import current_app
import logging

class YOLO:
    def __init__(self):
        try:
            cascade_file = current_app.config['CASCADE_FILE']
            self.detector = cv2.CascadeClassifier(cascade_file)
            if self.detector.empty():
                raise Exception("Error loading cascade classifier")
            self.confidence_threshold = current_app.config['DETECTION_CONFIDENCE_THRESHOLD']
        except Exception as e:
            logging.error(f"Error loading detector: {str(e)}")
            raise

    def detect(self, image):
        try:
            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect license plates
            plates = self.detector.detectMultiScale(gray, 
                                                  scaleFactor=1.1,
                                                  minNeighbors=5,
                                                  minSize=(30, 30))
            
            # Convert detections to standard format
            boxes = []
            for (x, y, w, h) in plates:
                boxes.append({
                    'box': [x, y, w, h],
                    'confidence': 1.0  # Cascade classifier doesn't provide confidence
                })
            
            return boxes
            
        except Exception as e:
            logging.error(f"Error during detection: {str(e)}")
            return []

    def draw_detections(self, image, detections):
        for detection in detections:
            x, y, w, h = detection['box']
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return image
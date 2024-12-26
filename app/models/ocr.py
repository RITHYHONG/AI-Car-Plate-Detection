import pytesseract
import cv2
import numpy as np
import logging
from flask import current_app

class OCR:
    def __init__(self):
        # Configure Tesseract path
        pytesseract.pytesseract.tesseract_cmd = current_app.config['TESSERACT_CMD']
        
        # OCR configuration
        self.config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    def preprocess_image(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        dilation = cv2.dilate(thresh, kernel, iterations=1)
        
        # Apply erosion to remove noise
        erosion = cv2.erode(dilation, kernel, iterations=1)
        
        return erosion
    
    def read_text(self, image):
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_image, config=self.config)
            
            # Clean the text
            cleaned_text = self.clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            logging.error(f"OCR Error: {str(e)}")
            return None
    
    def clean_text(self, text):
        # Remove unwanted characters and whitespace
        cleaned = ''.join(c for c in text if c.isalnum())
        return cleaned.upper()
    
    def validate_plate(self, text):
        """
        Validate if the detected text matches license plate patterns
        Returns (is_valid, confidence)
        """
        if not text:
            return False, 0.0
            
        # Basic validation rules (customize based on your needs)
        min_length = 5
        max_length = 10
        
        if len(text) < min_length or len(text) > max_length:
            return False, 0.0
            
        # Calculate confidence based on length and character types
        length_score = min(1.0, len(text) / max_length)
        char_score = sum(1 for c in text if c.isalnum()) / len(text)
        
        confidence = (length_score + char_score) / 2
        
        return confidence > 0.7, confidence
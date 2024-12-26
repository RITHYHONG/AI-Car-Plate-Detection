import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os
from flask import current_app
import uuid

def preprocess_image(image):
    """
    Preprocess image for better OCR results
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply gaussian blur
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    
    # Apply threshold to get black and white image
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    return opening

def save_uploaded_file(file):
    """
    Save uploaded file with secure filename
    """
    filename = secure_filename(file.filename)
    # Add UUID to filename to ensure uniqueness
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Create upload folder if it doesn't exist
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    return filepath

def is_valid_image(filepath):
    """
    Check if file is a valid image
    """
    try:
        img = cv2.imread(filepath)
        return img is not None
    except:
        return False

def resize_image(image, max_size=800):
    """
    Resize image while maintaining aspect ratio
    """
    height, width = image.shape[:2]
    
    if height > max_size or width > max_size:
        if height > width:
            ratio = max_size / height
        else:
            ratio = max_size / width
            
        new_size = (int(width * ratio), int(height * ratio))
        resized = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        return resized
        
    return image
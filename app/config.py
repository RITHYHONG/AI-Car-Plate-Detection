import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Ensure these paths exist
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    LOG_FOLDER = os.path.join(BASE_DIR, 'logs')
    
    # Create folders if they don't exist
    for folder in [UPLOAD_FOLDER, LOG_FOLDER]:
        os.makedirs(folder, exist_ok=True)
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Detection model config
    MODEL_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'weights')
    CASCADE_FILE = os.path.join(MODEL_PATH, 'haarcascade_license_plate.xml')
    DETECTION_CONFIDENCE_THRESHOLD = 0.5
    
    # OCR config
    TESSERACT_CMD = 'tesseract'  # Update this path for Windows
    
    # Logging config
    LOG_FILE = os.path.join(LOG_FOLDER, 'app.log')
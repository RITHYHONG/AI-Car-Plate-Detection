from flask import Blueprint

# Create blueprint for detection routes
detection_bp = Blueprint('detection', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.routes import detection
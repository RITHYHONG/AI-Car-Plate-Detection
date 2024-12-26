from flask import Flask
from app.database.models import db
from app.routes import detection_bp
import os
import logging

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object('app.config.Config')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(detection_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Ensure instance and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info('License Plate Detection System startup')

    return app
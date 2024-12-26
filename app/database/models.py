from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ticket_id = db.Column(db.String(50), unique=True, nullable=False)
    confidence = db.Column(db.Float)
    image_path = db.Column(db.String(200))
    processed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'timestamp': self.timestamp.isoformat(),
            'ticket_id': self.ticket_id,
            'confidence': self.confidence,
            'image_path': self.image_path,
            'processed': self.processed
        }

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(50), unique=True, nullable=False)
    detection_id = db.Column(db.Integer, db.ForeignKey('detection.id'), nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    printed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'detection_id': self.detection_id,
            'generated_at': self.generated_at.isoformat(),
            'printed': self.printed
        }
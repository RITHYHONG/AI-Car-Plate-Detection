import cv2
import os
import json
from datetime import datetime
from flask import current_app

class DataCollector:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = os.path.join(current_app.config['BASE_DIR'], 'training_data')
            
        self.base_path = base_path
        self.images_path = os.path.join(base_path, 'images')
        self.labels_path = os.path.join(base_path, 'labels')
        self.metadata_file = os.path.join(base_path, 'metadata.json')
        
        # Create directories if they don't exist
        os.makedirs(self.images_path, exist_ok=True)
        os.makedirs(self.labels_path, exist_ok=True)
        
        # Load or create metadata
        self.metadata = self._load_metadata()
    
    def save_training_sample(self, image, plate_text, bbox, confidence=1.0):
        """Save a new training sample with its annotation"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f'plate_{timestamp}.jpg'
            label_filename = f'plate_{timestamp}.txt'
            
            # Save image
            image_path = os.path.join(self.images_path, image_filename)
            cv2.imwrite(image_path, image)
            
            # Save label
            label_path = os.path.join(self.labels_path, label_filename)
            with open(label_path, 'w') as f:
                f.write(f'{plate_text}\n')
                f.write(f'{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n')
            
            # Update metadata
            self.metadata['samples'].append({
                'image': image_filename,
                'label': label_filename,
                'plate_text': plate_text,
                'confidence': confidence,
                'timestamp': timestamp
            })
            self._save_metadata()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error saving training sample: {str(e)}")
            return False
    
    def _load_metadata(self):
        """Load or create metadata file"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {'samples': [], 'last_updated': None}
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            self.metadata['last_updated'] = datetime.now().isoformat()
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            current_app.logger.error(f"Error saving metadata: {str(e)}")

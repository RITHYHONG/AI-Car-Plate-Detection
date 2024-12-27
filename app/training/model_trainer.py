import cv2
import numpy as np
from sklearn.model_selection import train_test_split
import os
import json

class ModelTrainer:
    def __init__(self, data_path='training_data'):
        self.data_path = data_path
        self.cascade = cv2.CascadeClassifier()
    
    def prepare_training_data(self):
        """Prepare positive and negative samples for training"""
        pos_dir = os.path.join(self.data_path, 'positive')
        neg_dir = os.path.join(self.data_path, 'negative')
        
        # Create description files
        self._create_description_files(pos_dir, neg_dir)
        
        return {
            'pos': len(os.listdir(pos_dir)),
            'neg': len(os.listdir(neg_dir))
        }
    
    def train(self, num_stages=10):
        """Train the cascade classifier"""
        params = {
            'numPos': 1000,  # Number of positive samples
            'numNeg': 2000,  # Number of negative samples
            'numStages': num_stages,
            'minHitRate': 0.995,
            'maxFalseAlarmRate': 0.5,
            'weightTrimRate': 0.95,
            'maxDepth': 1,
            'maxWeakCount': 100
        }
        
        # Train cascade
        print("Training cascade classifier...")
        cv2.traincascade(
            data='cascade',
            vec='positives.vec',
            bg='negatives.txt',
            numPos=params['numPos'],
            numNeg=params['numNeg'],
            numStages=params['numStages'],
            minHitRate=params['minHitRate'],
            maxFalseAlarmRate=params['maxFalseAlarmRate'],
            weightTrimRate=params['weightTrimRate'],
            maxDepth=params['maxDepth'],
            maxWeakCount=params['maxWeakCount']
        )
        
        print("Training complete!")
    
    def validate(self, test_images_dir):
        """Validate the trained model"""
        results = {
            'total': 0,
            'detected': 0,
            'false_positives': 0
        }
        
        # Load the trained cascade classifier
        cascade = cv2.CascadeClassifier('cascade/cascade.xml')
        
        # Test on validation images
        for image_file in os.listdir(test_images_dir):
            image_path = os.path.join(test_images_dir, image_file)
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect plates
            plates = cascade.detectMultiScale(gray, 1.1, 4)
            
            results['total'] += 1
            if len(plates) > 0:
                results['detected'] += 1
        
        return results

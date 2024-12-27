import cv2
import numpy as np
from imgaug import augmenters as iaa

class DataAugmentor:
    def __init__(self):
        self.augmenter = iaa.Sequential([
            iaa.Sometimes(0.5, iaa.GaussianBlur(sigma=(0, 0.5))),
            iaa.Sometimes(0.5, iaa.AdditiveGaussianNoise(scale=(0, 0.05*255))),
            iaa.Sometimes(0.5, iaa.Affine(
                scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
                translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
                rotate=(-5, 5),
                shear=(-5, 5)
            )),
            iaa.Sometimes(0.5, iaa.Multiply((0.8, 1.2))),
            iaa.Sometimes(0.5, iaa.LinearContrast((0.75, 1.5)))
        ])
    
    def augment(self, image, bboxes):
        """Augment an image and its bounding boxes"""
        # Augment images and bounding boxes
        image_aug, bboxes_aug = self.augmenter(
            images=[image],
            bounding_boxes=[bboxes]
        )
        
        return image_aug[0], bboxes_aug[0]
    
    def generate_augmented_samples(self, image, bbox, num_samples=5):
        """Generate multiple augmented samples from one image"""
        augmented_samples = []
        
        for _ in range(num_samples):
            aug_image, aug_bbox = self.augment(image, bbox)
            augmented_samples.append((aug_image, aug_bbox))
        
        return augmented_samples

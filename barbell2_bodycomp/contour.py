import cv2
import pydicom
import numpy as np
import matplotlib.pyplot as plt

if __name__ != '__main__':
    from barbell2_bodycomp.utils import apply_window


class AbdominalCircumferenceCalculator:

    def __init__(self):
        self.input_files = None
        self.circumference_values = {}

    @staticmethod
    def calculate_circumference(image, pixel_spacing):
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            return 0
        longest_contour = max(contours, key=cv2.contourArea)
        circumference_mm = 0
        for i in range(len(longest_contour) - 1):
            pt1 = longest_contour[i+0][0]
            pt2 = longest_contour[i+1][0]
            dx = (pt2[0] - pt1[0]) * pixel_spacing[0]
            dy = (pt2[1] - pt1[1]) * pixel_spacing[1]
            distance = np.sqrt(dx**2 + dy**2)
            circumference_mm += distance
        return circumference_mm    

    def get_normalized_image(self, p):
        image = p.pixel_array
        window = (400, 50)
        image = p.RescaleSlope * image + p.RescaleIntercept
        image = apply_window(image, window)
        return image

    def execute(self):
        self.circumference_values = {}
        for f in self.input_files:
            p = pydicom.dcmread(f)
            image = self.get_normalized_image(p)            
            if image.dtype != np.uint8:
                image = ((image - np.min(image)) / (np.max(image) - np.min(image)) * 255).astype('uint8')
            circumference_mm = self.calculate_circumference(image, p.PixelSpacing)
            self.circumference_values[f] = circumference_mm
        return self.circumference_values


class AbdominalCircumferenceEstimator:
    """ Class that takes L3 image as input and estimates the abdominal circumference in cm's
    even if the abdomen is partially occluded or clipped by a FOV that is too small. This
    can easily happen with obese patients. 
    Estimator takes an optional contour estimation model that is able to exclude the arms in
    the image (if present) and only output the abdomen
    """
    def __init__(self):
        self.input_files = None
        self.input_target_labels = None
        self.circumference_estimation_model = None
        self.circumference_estimation_model_params = None

    def add_random_occlusion(image, rectangle_width):
        if rectangle_width == 0:
            rectangle_width = 1
        image[:, :rectangle_width] = 0
        image[:, -rectangle_width:] = 0    
        return image

    def train(self):
        """ Takes set of occluded L3 images with ground-truth circumferences (target labels) and trains
        a model that can predict circumference from a new L3 image. The training process automatically 
        splits the data into a training and test set.
        """
        return []

    def validate(self):
        """ Takes input files and target labels and validates the circumference estimation model."""
        pass

    def execute(self):
        """ Does nothing for now but will be using the trained circumference estimation model to 
        predict the abdominal circumference of the given input files. 
        """
        pass


if __name__ == '__main__':
    from utils import apply_window
    calculator = AbdominalCircumferenceCalculator()
    calculator.input_files = ['/Users/Ralph/Desktop/nicole_squashed_output/HBP-MUMC-001-L3pre-no-phi.dcm']
    circumference_values = calculator.execute()
    import json
    print(json.dumps(circumference_values, indent=4))
#     estimator = AbdominalCircumFerenceEstimator()
#     estimator.input_files = []
#     estimator.input_target_labels = []
#     model = estimator.train()
#     print(model)

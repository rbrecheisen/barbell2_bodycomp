import cv2
import pydicom
import numpy as np
import matplotlib.pyplot as plt


def apply_window(pix, window):
    result = (pix - window[1] + 0.5 * window[0])/window[0]
    result[result < 0] = 0
    result[result > 1] = 1
    return result


def calculate_circumference(image, pixel_size_mm):
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    if len(image.shape) > 2:
        raise ValueError('image must be 2D')
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) == 0:
        return 0
    longest_contour = max(contours, key=cv2.contourArea)
    circumference_pixel = cv2.arcLength(longest_contour, True)
    circumference_mm = circumference_pixel * pixel_size_mm
    return circumference_mm


def normalize_image(p):
    image = p.pixel_array
    window = (400, 50)
    image = p.RescaleSlope * image + p.RescaleIntercept
    image = apply_window(image, window)
    # image_8bit = ((image - np.min(image)) / (np.max(image) - np.min(image)) * 255).astype(np.int8)
    return image


# image = cv2.imread('/Users/Ralph/Desktop/nicole_squashed_output/HBP-MUMC-001-L3pre-no-phi.dcm.png', cv2.IMREAD_GRAYSCALE)
# pixel_size_mm = 1
# circumference_mm = calculate_circumference(image, pixel_size_mm)
# print(f"Circumference: {circumference_mm:.2f} mm")


def create_image(width, height, circle_radius, rectangle_width):
    if rectangle_width == 0:
        rectangle_width = 1
    img = np.zeros((height, width))
    circle_center = (width // 2, height // 2)
    y, x = np.ogrid[-circle_center[1]:height - circle_center[1], -circle_center[0]:width - circle_center[0]]
    mask = x*x + y*y <= circle_radius*circle_radius
    img[mask] = 255
    img[:, :rectangle_width] = 0
    img[:, -rectangle_width:] = 0    
    return img


def add_occluding_bars(image, rectangle_width):
    if rectangle_width == 0:
        rectangle_width = 1
    image[:, :rectangle_width] = 0
    image[:, -rectangle_width:] = 0    
    return image


def test_circumference_calculation():
    width = 500
    height = 500
    circle_radius = 200
    rectangle_width = 100
    pixel_size_mm = 1
    p = pydicom.dcmread('/Users/Ralph/Desktop/nicole_squashed_output/HBP-MUMC-001-L3pre-no-phi.dcm')
    img = normalize_image(p)
    img = add_occluding_bars(img, rectangle_width)
    # img = create_image(width, height, circle_radius, rectangle_width)
    circumference_mm = calculate_circumference(img, pixel_size_mm)
    print(f"Circumference: {circumference_mm:.2f} mm")
    plt.imshow(img, cmap='gray')
    plt.axis('off')
    plt.show()


class AbdominalCircumFerenceEstimator:
    """ Class that takes L3 image as input and estimates the abdominal circumference in cm's
    even if the abdomen is partially occluded or clipped by a FOV that is too small. This
    can easily happen with obese patients. 
    Estimator takes an optional contour estimation model that is able to exclude the arms in
    the image (if present) and only output the abdomen
    """
    def __init__(self):
        self.input_files = None
        self.input_target_labels = None
        self.contour_model = None
        self.contour_model_params = None
        self.circumference_estimation_model = None
        self.circumference_estimation_model_params = None

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


# if __name__ == '__main__':
test_circumference_calculation()
#     estimator = AbdominalCircumFerenceEstimator()
#     estimator.input_files = []
#     estimator.input_target_labels = []
#     model = estimator.train()
#     print(model)

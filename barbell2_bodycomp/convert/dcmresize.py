####
# Author: Abhimanyu Anand
# Date: 13 September 2023
# email: a.abhimanyuanand@student.maastrichtuniversity.nl
# Description: This script resizes a DICOM image while preserving aspect ratio and padding with zeros.
# Usage: python dcmresize.py
#      Make sure to change the paths and the target size in the main function at the end of the script.
####

import pydicom
from pydicom.dataset import FileMetaDataset
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

from barbell2_bodycomp.utils import create_fake_dicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
from skimage.transform import resize

def resize_dicom(input_path, output_path, target_size):
    """
    Resize a DICOM image while preserving aspect ratio and padding with zeros.
    
    Args:
        input_path (str): Path to the input DICOM file.
        output_path (str): Path to the output DICOM file.
        target_size (tuple): Desired size as (width, height).
    """
    # Load the DICOM file
    dicom_data = pydicom.dcmread(input_path)
    p_new = dicom_data
    
    # Extract pixel data and convert it to a NumPy array
    pixel_data = dicom_data.pixel_array

    # Calculate the desired aspect ratio
    aspect_ratio = dicom_data.Columns / dicom_data.Rows
    
    # Determine the scaling factor to maintain aspect ratio
    target_width, target_height = target_size
    if target_width / aspect_ratio <= target_height:
        new_width = int(target_width)
        new_height = int(target_width / aspect_ratio)
    else:
        new_width = int(target_height * aspect_ratio)
        new_height = int(target_height)

    # Resize the image using PIL
    img = Image.fromarray(pixel_data)
    img = img.resize((new_width, new_height))
    
    # Create a new NumPy array for the resized image
    resized_pixel_data = np.zeros([target_height, target_width], dtype=np.uint16)
    
    # Copy the resized image into the center of the new NumPy array
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    resized_pixel_data[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = np.array(img)

    # Update DICOM metadata for the resized image
    p_new.Rows = target_height
    p_new.Columns = target_width
    p_new.PixelData = resized_pixel_data.tobytes()

    p_new.save_as(output_path)

if __name__ == "__main__":
    input_path = "/Users/abhimanyu/Maastricht/Internship/non-square_dicom_files/CONSORT_C250-no-phi_raw.dcm"  # Replace with the path to your input DICOM file
    output_path = "/Users/abhimanyu/Maastricht/Internship/non-square_dicom_files/resized/CONSORT_C250-no-phi_raw.dcm"  # Replace with the desired output path
    target_size = (512, 512)  # Replace with your desired target size

    resize_dicom(input_path, output_path, target_size)

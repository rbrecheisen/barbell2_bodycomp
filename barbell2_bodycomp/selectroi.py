import os
import shutil
import logging

logger = logging.getLogger(__name__)


class RoiSelector:

    VERTEBRAE_T3 = 'vertebrae_T3.nii.gz'
    VERTEBRAE_T4 = 'vertebrae_T4.nii.gz'
    VERTEBRAE_L2 = 'vertebrae_L2.nii.gz'
    VERTEBRAE_L3 = 'vertebrae_L3.nii.gz'
    VERTEBRAE_L4 = 'vertebrae_L4.nii.gz'
    FACE = 'face.nii.gz'
    DUODENUM = 'duodenum.nii.gz'
    HIP_LEFT = 'hip_left.nii.gz'
    HIP_RIGHT= 'hip_right.nii.gz'
    KIDNEY_LEFT = 'kidney_left.nii.gz'
    KIDNEY_RIGHT = 'kidney_right.nii.gz'
    AUTOCHTON_LEFT = 'autochthon_left.nii.gz'
    AUTOCHTON_RIGHT = 'autochthon_right.nii.gz'
    ADRENAL_GLAND_LEFT = 'adrenal_gland_left.nii.gz'
    ADRENAL_GLAND_RIGHT = 'adrenal_gland_right.nii.gz'
    RIB_LEFT_12 = 'rib_left_12.nii.gz'
    RIB_RIGHT_12 = 'rib_right_12.nii.gz'
    LIVER = 'liver.nii.gz'

    def __init__(self):
        self.input_directory = None
        self.output_directory = None
        self.roi = RoiSelector.VERTEBRAE_L3
        self.overwrite = True
        self.output_file = None

    @staticmethod
    def exists(f):
        return os.path.isfile(f)

    def execute(self):
        logger.info('Running RoiSelector...')
        if self.input_directory is None:
            logger.error('Input directory not specified')
            return None
        if self.roi is None:
            logger.error('ROI not specified')
            return None
        if self.output_directory is None:
            logger.error('Output directory not specified')
            return None
        self.output_file = os.path.join(self.output_directory, self.roi)
        if not self.overwrite and self.exists(self.output_file):
            logger.info('Overwrite = False and output file already exists, skipping')
            return self.output_file
        os.makedirs(self.output_directory, exist_ok=True)
        shutil.copy(os.path.join(self.input_directory, self.roi), self.output_directory)
        return self.output_file

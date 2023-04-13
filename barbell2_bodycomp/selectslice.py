import os
import logging
import pydicom
import nibabel
import numpy as np

logger = logging.getLogger(__name__)


class SliceSelector:

    ALL = 0
    MEDIAN = 1
    IQR_25_50_75 = 2
    TOP = 3
    BOTTOM = 4

    def __init__(self):
        self.input_roi = None
        self.input_volume = None
        self.input_dicom_directory = None
        self.mode = SliceSelector.MEDIAN
        self.output_files = None

    @staticmethod
    def has_duplicate_objects(roi):
        # TODO: Implement this!
        return False

    @staticmethod
    def get_min_max_slice_idx(roi):
        roi_data = roi.get_fdata()
        nr_slices = roi_data.shape[2]
        i_min = -1
        for i in range(nr_slices):
            slice = roi_data[:,:,i]
            if 1 in np.unique(slice):
                i_min = i
                break
        i_max = -1
        for i in range(nr_slices):
            slice = roi_data[:,:,nr_slices-i-1]
            if 1 in np.unique(slice):
                i_max = nr_slices - i
                break
        return i_min, i_max

    @staticmethod
    def get_z_coord_patient_position(i, volume):
        M = volume.affine[:3, :3]
        abc = volume.affine[:3, 3]
        return (M.dot([0, 0, i]) + abc)[2]

    def get_min_max_z_coord_patient_position(self, i_min, i_max, volume):
        z_min = self.get_z_coord_patient_position(i_min, volume)
        z_max = self.get_z_coord_patient_position(i_max, volume)
        return z_min, z_max

    @staticmethod
    def get_dicom_z(file_path):
        p = pydicom.dcmread(file_path, stop_before_pixels=True)
        return p.ImagePositionPatient[2]

    def get_dicom_images_between(self, z_min, z_max, dicom_directory):
        z_coords = {}
        for f in os.listdir(dicom_directory):
            f_path = os.path.join(dicom_directory, f)
            z = self.get_dicom_z(f_path)
            z_coords[z] = f_path
        z_min_nearest = min(list(z_coords.keys()), key=lambda x:abs(x - z_min))
        z_max_nearest = min(list(z_coords.keys()), key=lambda x:abs(x - z_max))
        file_paths = []
        for z in z_coords.keys():
            if z_min_nearest <= z <= z_max_nearest:
                file_paths.append(z_coords[z])
        return file_paths

    def execute(self):
        logger.info('Running SliceSelector...')
        if self.input_roi is None:
            logger.error('Input ROI not specified')
            return None
        if self.input_volume is None:
            logger.error('Input NIFTI volume not specified')
            return None
        if self.input_dicom_directory is None:
            logger.error('Input DICOM directory not specified')
            return None
        if self.mode is None:
            logger.error('Mode not specified')
            return None
        roi = nibabel.load(self.input_roi)
        if self.has_duplicate_objects(roi):
            logger.error('ROI has duplicate objects')
            return None
        i_min, i_max = self.get_min_max_slice_idx(roi)
        volume = nibabel.load(self.input_volume)
        z_min, z_max = self.get_min_max_z_coord_patient_position(i_min, i_max, volume)
        self.output_files = []
        if self.mode == SliceSelector.ALL or self.mode == SliceSelector.TOP or self.mode == SliceSelector.BOTTOM:
            self.output_files = self.get_dicom_images_between(z_min, z_max, self.input_dicom_directory)
            if self.mode == SliceSelector.TOP:
                self.output_files = [self.output_files[0]]
            elif self.mode == SliceSelector.BOTTOM:
                self.output_files = [self.output_files[-1]]
            else:
                logger.error('Unknown mode {}'.format(self.mode))
                self.output_files = []
        elif self.mode == SliceSelector.MEDIAN:
            z_median = z_min + np.abs(z_max - z_min) * 0.50
            self.output_files = self.get_dicom_images_between(z_median, z_median, self.input_dicom_directory)
        elif self.mode == SliceSelector.IQR_25_50_75:
            z_25 = z_min + np.abs(z_max - z_min) * 0.25
            self.output_files.extend(self.get_dicom_images_between(z_25, z_25, self.input_dicom_directory))
            z_50 = z_min + np.abs(z_max - z_min) * 0.50
            self.output_files.extend(self.get_dicom_images_between(z_50, z_50, self.input_dicom_directory))
            z_75 = z_min + np.abs(z_max - z_min) * 0.75
            self.output_files.extend(self.get_dicom_images_between(z_75, z_75, self.input_dicom_directory))
        elif isinstance(self.mode, float):
            z = z_min + self.mode * (z_max - z_min)
            self.output_files = self.get_dicom_images_between(z, z, self.input_dicom_directory)
        else:
            logger.error(f'Unknown mode: {self.mode}')
        return self.output_files

    def get_dicom_image_at_instance_number(self, instance_number):
        for f in os.listdir(self.input_dicom_directory):
            f_path = os.path.join(self.input_dicom_directory, f)
            p = pydicom.dcmread(f_path, stop_before_pixels=True)
            if p.InstanceNumber == instance_number:
                return f_path
        return None


if __name__ == '__main__':
    def main():
        selector = SliceSelector()
        selector.input_roi = os.path.join(os.environ['HOME'], 'data/surfdrive/dropbox/segmentations/vertebrae_L3.nii.gz')
        selector.input_volume = os.path.join(os.environ['HOME'], 'data/surfdrive/dropbox/nifti/al.nii.gz')
        selector.input_dicom_directory = os.path.join(os.environ['HOME'], 'data/surfdrive/dropbox/dicom')
        # selector.mode = SliceSelector.ALL
        selector.mode = 0.68
        file_paths = selector.execute()
        import shutil
        shutil.copyfile(file_paths[0], os.path.join(os.environ['HOME'], 'data/surfdrive/dropbox/L3.dcm'))
    main()

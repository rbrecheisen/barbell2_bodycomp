import os
import logging
import numpy as np
import nibabel as nib

logger = logging.getLogger(__name__)


class NumpyToNifti:

    def __init__(self):
        self.input_file_or_array_obj = None
        self.output_file = None
        self.version = 2

    def execute(self):
        if isinstance(self.input_file_or_array_obj, str):
            self.input_file_or_array_obj = np.load(self.input_file_or_array_obj)
        if self.version == 1:
            self.nifti_obj = nib.Nifti1Image(self.input_file_or_array_obj, affine=np.eye(4))
        elif self.version == 2:
            self.nifti_obj = nib.Nifti2Image(self.input_file_or_array_obj, affine=np.eye(4))
        else:
            raise RuntimeError(f'Unknown NIFTI version {self.version}')
        nib.save(self.nifti_obj, self.output_file)
        return self.output_file
    

if __name__ == '__main__':
    n2n = NumpyToNifti()
    n2n.input_file_or_array_obj = np.array([[1., 2.], [3., 4.]])
    n2n.output_file = 'numpy.nii.gz'
    n2n.execute()

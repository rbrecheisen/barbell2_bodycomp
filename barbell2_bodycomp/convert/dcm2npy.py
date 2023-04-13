import pydicom

from barbell2_bodycomp.utils import apply_window


class Dicom2Numpy:

    def __init__(self, dcm_file_path_or_obj):        
        self.dcm_file_path_or_obj = dcm_file_path_or_obj
        self.npy_array = None
        self.window = None
        self.normalize_enabled = True

    def set_window(self, window):
        self.window = window

    def set_normalize_enabled(self, normalize_enabled):
        """ Moves CT pixel values from e.g., (-1000, 1000) to (0, 2000)"""
        self.normalize_enabled = normalize_enabled

    def is_normalize_enabled(self):
        return self.normalize_enabled

    def execute(self):
        self.npy_array = None
        if isinstance(self.dcm_file_path_or_obj, str):
            p = pydicom.dcmread(self.dcm_file_path_or_obj)
        else:
            p = self.dcm_file_path_or_obj
        pixels = p.pixel_array
        self.npy_array = pixels.reshape(p.Rows, p.Columns)
        if self.is_normalize_enabled():
            b = p.RescaleIntercept
            m = p.RescaleSlope
            self.npy_array = m * self.npy_array + b
        if self.window is not None:
            self.npy_array = apply_window(self.npy_array, self.window)
        return self.npy_array


# x = '/Volumes/SEAGATE_RALPH/data/hpb/metabolicimaging/bodycomposition/data/neuro_mumc/Sandra/DCM_TAG_LIJST/19001.dcm'
# p = pydicom.dcmread(x, force=True)
# p.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'
# n = Dicom2Numpy(p)
# print(n.execute().shape)

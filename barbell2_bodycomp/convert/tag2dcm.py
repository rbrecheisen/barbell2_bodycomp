import os
import pydicom
import logging

from barbell2_bodycomp.utils import create_fake_dicom
from barbell2_bodycomp.convert.tag2npy import Tag2Numpy


class Tag2Dicom:

    def __init__(self, tag_file_path, dcm_file_path_or_obj, logger=None):
        self.tag_file_path = tag_file_path
        self.dcm_file_path_or_obj = dcm_file_path_or_obj
        self.output_dir = '..'
        self.tag_dcm_file_name = None
        self.tag_dcm_file_path = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def execute(self):
        if isinstance(self.dcm_file_path_or_obj, str):
            p = pydicom.dcmread(self.dcm_file_path_or_obj)
        else:
            p = self.dcm_file_path_or_obj
        t2n = Tag2Numpy(self.tag_file_path, (p.Rows, p.Columns))
        pixels_tag = t2n.execute()
        p_new = create_fake_dicom(pixels_tag, p)
        self.tag_dcm_file_name = os.path.split(self.tag_file_path)[1] + '.dcm'
        self.tag_dcm_file_path = os.path.join(self.output_dir, self.tag_dcm_file_name)
        p_new.save_as(self.tag_dcm_file_path)

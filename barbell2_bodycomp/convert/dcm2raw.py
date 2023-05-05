import logging
import pydicom

logger = logging.getLogger(__name__)


class DicomToRaw:

    def __init__(self):
        self.input_file = None
        self.save_to_file = False
        self.output_directory = None
        self.output_file = None

    def execute(self):
        if self.input_file is None:
            logger.error('Input file is None')
            return None
        if self.save_to_file and self.output_directory is None:
            logger.error('Output directory cannot be None if save_to_file=True')
            return None
        if isinstance(self.input_file, str):
            p = pydicom.dcmread(self.input_file)
        else:
            p = self.input_file
        if p.file_meta.TransferSyntaxUID.is_compressed:
            p.decompress()
        if self.save_to_file:
            p.save_as(output_dicom_file_path)
        



if __name__ == '__main__':
    def main():
        d2r = DicomToRaw()
        d2r.input_file = ''
    main()

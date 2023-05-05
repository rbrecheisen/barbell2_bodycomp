import logging
import pydicom

logger = logging.getLogger(__name__)


class DicomToRaw:

    def __init__(self):
        self.input_file_or_obj = None
        self.save_to_file = False
        self.output_file = None

    def execute(self):
        if self.input_file_or_obj is None:
            logger.error('Input file is None')
            return None
        if self.save_to_file and self.output_file is None:
            logger.error('Output file cannot be None if save_to_file=True')
            return None
        if isinstance(self.input_file_or_obj, str):
            p = pydicom.dcmread(self.input_file_or_obj)
        else:
            p = self.input_file_or_obj
        if p.file_meta.TransferSyntaxUID.is_compressed:
            p.decompress()
        if self.save_to_file:
            p.save_as(self.output_file)
            return self.output_file
        else:
            return p


if __name__ == '__main__':
    def main():
        d2r = DicomToRaw()
        d2r.input_file_or_obj = ''
    main()

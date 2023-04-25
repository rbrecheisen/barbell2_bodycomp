import os
import pydicom


class DicomToRaw:

    def __init__(self):
        self.input_file = None        
        self.output_directory = None

    def execute(self):
        if isinstance(self.input_file, str):
            p = pydicom.dcmread(self.input_file)
        else:
            p = self.input_file
        if p.file_meta.TransferSyntaxUID.is_compressed:
            p.decompress()
        # p.save_as(output_dicom_file_path)
        



if __name__ == '__main__':
    def main():
        d2r = DicomToRaw()
        d2r.input_file = ''
    main()

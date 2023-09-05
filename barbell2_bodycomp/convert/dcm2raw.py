import os
import argparse
import logging
import pydicom

from barbell2_bodycomp.utils import is_dicom_file

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


def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_dir', help='Input directory')
    parser.add_argument('--out_dir', help='Output directory')
    parser.add_argument('--in_file', help='Input file name')
    parser.add_argument('--out_file', help='Output file name (overwrite otherwise)')
    args = parser.parse_args()
    # if input directory specified
    # check if output directory also specified
    # if not, throw error
    # else, iterate through DICOM files, convert to *_raw.dcm in output directory
    if args.in_dir is not None:
        if args.out_dir is not None:
            if args.in_dir != args.out_dir:
                os.makedirs(args.out_dir, exist_ok=False)
                for f in os.listdir(args.in_dir):
                    f_path = os.path.join(args.in_dir, f)
                    if is_dicom_file(f_path):
                        print(f_path)
            else:
                raise RuntimeError('in_dir cannot be equal to out_dir')
        else:
            raise RuntimeError('out_dir cannot be empty if in_dir is not empty')
    elif args.in_file is not None:
        if args.out_file is not None:
            if args.in_file != args.out_file:
                print(args)
            else:
                raise RuntimeError('in_file cannot be equal to out_file')
        else:
            raise RuntimeError('out_file cannot be empty if in_file is not empty')
    else:
        raise RuntimeError('no arguments provided')
    

if __name__ == '__main__':
    main()

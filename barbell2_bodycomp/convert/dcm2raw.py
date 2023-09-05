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
    # run it
    if args.in_dir is not None:
        if args.out_dir is not None:
            if args.in_dir != args.out_dir:
                os.makedirs(args.out_dir, exist_ok=False)
                for f in os.listdir(args.in_dir):
                    f_path = os.path.join(args.in_dir, f)
                    if is_dicom_file(f_path):
                        out_filename = os.path.split(f_path)[1]  # gives me filename
                        if out_filename.endswith('.dcm'):
                            out_filename = os.path.splitext(out_filename)[0] + '_raw.dcm'
                        else:
                            out_filename = out_filename + '_raw.dcm'
                        out_filepath = os.path.join(args.out_dir, out_filename)
                        d2r = DicomToRaw()
                        d2r.input_file_or_obj = f_path
                        d2r.output_file = out_filepath
                        d2r.save_to_file = True
                        d2r.execute()
                        print(f'saved to {out_filepath}')
            else:
                raise RuntimeError('in_dir cannot be equal to out_dir')
        else:
            raise RuntimeError('out_dir cannot be empty if in_dir is not empty')
    elif args.in_file is not None:
        if args.out_file is not None:
            if args.in_file != args.out_file:
                d2r = DicomToRaw()
                d2r.input_file_or_obj = args.in_file
                d2r.output_file = args.out_file
                d2r.save_to_file = True
                d2r.execute()
                print(f'saved to {args.out_file}')
            else:
                raise RuntimeError('in_file cannot be equal to out_file')
        else:
            raise RuntimeError('out_file cannot be empty if in_file is not empty')
    else:
        raise RuntimeError('no arguments provided')
    

if __name__ == '__main__':
    main()

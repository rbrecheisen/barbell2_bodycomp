import os
import argparse
import logging
import numpy as np
import nibabel as nib

# logger = logging.getLogger(__name__)


class NumpyToNifti:

    def __init__(self, logger=None):
        self.input_file_or_array_obj = None
        self.flip_and_rotate = True
        self.output_file = None
        self.affine_transform = np.eye(4)
        self.version = 1
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def execute(self):
        if isinstance(self.input_file_or_array_obj, str):
            self.input_file_or_array_obj = np.load(self.input_file_or_array_obj)
        if self.flip_and_rotate:
            self.input_file_or_array_obj = np.flip(self.input_file_or_array_obj, axis=0)
            self.input_file_or_array_obj = np.rot90(self.input_file_or_array_obj, k=1, axes=(0, 1))
        if self.version == 1:
            self.nifti_obj = nib.Nifti1Image(self.input_file_or_array_obj, affine=self.affine_transform)
        elif self.version == 2:
            self.nifti_obj = nib.Nifti2Image(self.input_file_or_array_obj, affine=self.affine_transform)
        else:
            raise RuntimeError(f'Unknown NIFTI version {self.version}')
        nib.save(self.nifti_obj, self.output_file)
        return self.output_file
    

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_dir', help='Input directory')
    parser.add_argument('--out_dir', help='Output directory')
    parser.add_argument('--in_file', help='Input file name')
    parser.add_argument('--out_file', help='Output file name (must be different)')
    parser.add_argument('--nifti_version', help='NIFTI version (default: 1)', default=1, type=int)
    parser.add_argument('--flip_rotate', help='Flip and rotate image (default: yes)', default='yes')
    args = parser.parse_args()
    if args.in_dir is not None:
        if args.out_dir is not None:
            if args.in_dir != args.out_dir:
                os.makedirs(args.out_dir, exist_ok=False)
                for f in os.listdir(args.in_dir):
                    if f.endswith('.npy'):
                        f_path = os.path.join(args.in_dir, f)
                        out_filename = os.path.split(f_path)[1]
                        out_filename = os.path.splitext(out_filename)[0] + '.nii.gz'
                        out_filepath = os.path.join(args.out_dir, out_filename)
                        n2n = NumpyToNifti()
                        n2n.input_file_or_array_obj = f_path
                        n2n.output_file = out_filepath
                        n2n.version = args.nifti_version
                        n2n.flip_and_rotate = True if args.flip_rotate == 'yes' else False
                        n2n.execute()
                        print(f'save to {out_filepath}')
            else:
                raise RuntimeError('in_dir cannot be equal to out_dir')
        else:
            raise RuntimeError('out_dir cannot be empty if in_dir is not empty')
    elif args.in_file is not None:
        if args.out_file is not None:
            if args.in_file.endswith('.npy') and args.in_file != args.out_file:
                n2n = NumpyToNifti()
                n2n.input_file_or_array_obj = args.in_file
                n2n.output_file = args.out_file
                n2n.version = args.nifti_version
                n2n.flip_and_rotate = True if args.flip_rotate == 'yes' else False
                n2n.execute()
                print(f'save to {out_filepath}')
            else:
                raise RuntimeError('in_file cannot be equal to out_file')
        else:
            raise RuntimeError('out_file cannot be empty if in_file is not empty')
    else:
        raise RuntimeError('no arguments provided')


if __name__ == '__main__':
    main()

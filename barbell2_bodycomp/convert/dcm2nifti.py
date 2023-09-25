import os
import logging
import subprocess


class DicomToNifti:

    def __init__(self, logger=None):
        try:
            subprocess.call(['dcm2niix'])
        except FileNotFoundError:
            print(
                'dcm2niix is not installed! Please install it using the following command:\n'
                'curl -fLO https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_mac.zip'
            )
        self.input_directory = None
        self.output_file = None
        self.overwrite = True
        self.cmd = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    @staticmethod
    def exists(f):
        return os.path.isfile(f)

    def execute(self, verbose=False):
        self.logger.info('Running DicomToNifti...')
        if self.input_directory is None:
            self.logger.error('Input directory not specified')
            return None
        if self.output_file is None:
            self.logger.error('Output file not specified')
            return None
        if not self.overwrite and self.exists(self.output_file):
            self.logger.info('Overwrite = False and output file already exists')
            return self.output_file
        if self.exists(self.output_file):
            self.logger.warn('Output file already exists, deleting it')
            file_base = os.path.splitext(self.output_file)[0]
            os.system('rm {}*'.format(file_base))
        items = os.path.split(self.output_file)
        output_file_name = items[1]
        if output_file_name.endswith('.nii.gz'):
            output_file_name = output_file_name[:-7]
        elif output_file_name.endswith('.nii'):
            output_file_name = output_file_name[:-4]
        else:
            self.logger.error('Output file must have extension .nii.gz or .nii')
            return None
        output_file_dir = items[0]
        os.makedirs(output_file_dir, exist_ok=True)
        self.cmd = f'dcm2niix -m y -z y -f {output_file_name} -o {output_file_dir} {self.input_directory}'
        if verbose:
            self.logger.info(f'{self.cmd}')
        os.system(self.cmd)
        return self.output_file


if __name__ == '__main__':
    def main():
        pass
    main()

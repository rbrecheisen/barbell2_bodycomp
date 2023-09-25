import os
import logging


class TotalSegmentator:

    def __init__(self, logger=None):
        self.input_file = None
        self.output_directory = None
        self.fast = False
        self.statistics = False
        # self.radiomics = False
        self.overwrite = True
        self.cmd = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    @staticmethod
    def is_empty(directory):
        return len(os.listdir(directory)) == 0

    def execute(self):
        self.logger.info('Running TotalSegmentator...')
        if self.input_file is None:
            self.logger.error('Input NIFTI file not specified')
            return None
        if self.output_directory is None:
            self.logger.error('Output directory not specified')
            return None
        if not self.overwrite and not self.is_empty(self.output_directory):
            self.logger.info('Overwrite = False and output directory not empty, so skipping')
            return self.output_directory
        fast = ''
        if self.fast:
            fast = '--fast'
        statistics = ''
        if self.statistics:
            statistics = '--statistics'
        radiomics = ''
        # if self.radiomics:
        #     radiomics = '--radiomics'
        self.cmd = 'TotalSegmentator {} {} {} -i {} -o {}'.format(
            statistics, 
            radiomics,
            fast,
            self.input_file,
            self.output_directory,
        )
        self.logger.info(f'Running command: {self.cmd}')
        os.system(self.cmd)
        return self.output_directory


if __name__ == '__main__':
    def main():
        pass
    main()

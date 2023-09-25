import os
import logging
import pydicom
import numpy as np
import pandas as pd

from barbell2_bodycomp.utils import calculate_area, calculate_mean_radiation_attenuation, get_pixels


class BodyCompositionCalculator:

    MUSCLE = 1
    VAT = 5
    SAT = 7

    def __init__(self, logger=None):
        self.input_files = None                 # L3 images
        self.input_segmentation_files = None    # Segmentations calculated using MuscleFatSegmentator
        self.heights = None                     # (Optional) dictionary containing heights for each L3 image
        self.output_metrics = None              # Dictionary containing output metrics for each L3 image
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    @staticmethod
    def load_dicom(f_path):
        p = pydicom.dcmread(f_path)
        pixel_spacing = p.PixelSpacing
        pixels = get_pixels(p, normalize=True)
        return pixels, pixel_spacing

    @staticmethod
    def load_segmentation(f_path):
        return np.load(f_path)

    def execute(self):
        # TODO: If heights are provided, output index values!!!
        self.logger.info('Running BodyCompositionCalculator...')
        if self.input_files is None:
            self.logger.error('Input files not specified')
            return None
        if self.input_segmentation_files is None:
            self.logger.error('Input segmentation files not specified')
            return None
        # Check that we're not dealing with probability maps
        if self.input_segmentation_files[0].endswith('.seg.prob.npy'):
            self.logger.error('Cannot handle *.seg.prob.npy files')
            return None
        # Check that for each input file we have a matching segmentation file
        file_pairs = []
        for input_file in self.input_files:
            input_file_name = os.path.split(input_file)[1]
            found = False
            for input_segmentation_file in self.input_segmentation_files:
                input_segmentation_file_name = os.path.split(input_segmentation_file)[1]
                if input_file_name + '.seg.npy' == input_segmentation_file_name:
                    file_pairs.append((input_file, input_segmentation_file))
                    found = True
                    break
            if not found:
                self.logger.warn(f'Input file {input_file_name} missing corresponding segmentation file')
        # Work with found file pairs
        self.output_metrics = {}
        for file_pair in file_pairs:
            image, pixel_spacing = self.load_dicom(file_pair[0])
            segmentations = self.load_segmentation(file_pair[1])
            self.output_metrics[file_pair[0]] = {}
            self.output_metrics[file_pair[0]] = {
                'muscle_area': calculate_area(segmentations, BodyCompositionCalculator.MUSCLE, pixel_spacing),
                'vat_area': calculate_area(segmentations, BodyCompositionCalculator.VAT, pixel_spacing),
                'sat_area': calculate_area(segmentations, BodyCompositionCalculator.SAT, pixel_spacing),
                'muscle_ra': calculate_mean_radiation_attenuation(image, segmentations, BodyCompositionCalculator.MUSCLE),
                'vat_ra': calculate_mean_radiation_attenuation(image, segmentations, BodyCompositionCalculator.VAT),
                'sat_ra': calculate_mean_radiation_attenuation(image, segmentations, BodyCompositionCalculator.SAT),
            }
            self.logger.info(f'{file_pair[0]}:')
            self.logger.info(' - muscle_area: {}'.format(self.output_metrics[file_pair[0]]['muscle_area']))
            self.logger.info(' - vat_area: {}'.format(self.output_metrics[file_pair[0]]['vat_area']))
            self.logger.info(' - sat_area: {}'.format(self.output_metrics[file_pair[0]]['sat_area']))
            self.logger.info(' - muscle_ra: {}'.format(self.output_metrics[file_pair[0]]['muscle_ra']))
            self.logger.info(' - vat_ra: {}'.format(self.output_metrics[file_pair[0]]['vat_ra']))
            self.logger.info(' - sat_ra: {}'.format(self.output_metrics[file_pair[0]]['sat_ra']))
        return self.output_metrics
    
    def as_df(self):
        if self.output_metrics is None:
            return None
        data = {'file': [], 'muscle_area': [], 'vat_area': [], 'sat_area': [], 'muscle_ra': [], 'vat_ra': [], 'sat_ra': []}
        for k in self.output_metrics.keys():
            data['file'].append(k)
            data['muscle_area'].append(self.output_metrics[k]['muscle_area'])
            data['vat_area'].append(self.output_metrics[k]['vat_area'])
            data['sat_area'].append(self.output_metrics[k]['sat_area'])
            data['muscle_ra'].append(self.output_metrics[k]['muscle_ra'])
            data['vat_ra'].append(self.output_metrics[k]['vat_ra'])
            data['sat_ra'].append(self.output_metrics[k]['sat_ra'])
        return pd.DataFrame(data=data)


if __name__ == '__main__':
    def main():
        calculator = BodyCompositionCalculator()
        calculator.input_files = ['/mnt/localscratch/cds/rbrecheisen/raw/pancreas-demo-1/1.dcm']
        calculator.input_segmentation_files = ['/tmp/barbell2/bodycomp/seg.py/1.dcm.seg.npy']
        output_metrics = calculator.execute()
        for k in output_metrics.keys():
            print(f'{k}: {output_metrics[k]}')
    main()

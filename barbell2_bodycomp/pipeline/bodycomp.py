import os
import shutil
import argparse

from barbell2_bodycomp.convert import DicomToNifti
from barbell2_bodycomp import TotalSegmentator, RoiSelector, SliceSelector, MuscleFatSegmentator, BodyCompositionCalculator


class BodyCompositionPipeline:

    """
    Purpose of this component is to easily run the whole body composition pipeline from 
    beginning to end. Under the hood, the components handling the different steps are
    executed in sequence.

    TODO: If output already exists, skip it unless overwrite=True
    """

    def __init__(self, 
                 input_directory, 
                 output_directory, 
                 mode=MuscleFatSegmentator.ARGMAX,
                 steps=[
                    'dicom2nifti',
                    'totalsegmentator',
                    'selectroi',
                    'selectslice',
                    'l3seg',
                    'calculate',
                 ],
                 model_files=None, 
                 ):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.model_files = model_files
        if self.model_files is None:
            self.model_files = self.load_cached_model_files()
        self.steps = steps
        self.mode = mode

    def load_cached_model_files(self):
        model_files = None
        for location in ['/tmp', '/tmp/mosamatic', '/mnt/localscratch/cds/rbrecheisen/models/v2']:
            if os.path.isdir(location):
                if 'model.zip' in os.listdir(location) and 'contour_model.zip' in os.listdir(location) and 'params.json' in os.listdir(location):
                    print(f'found model files in {location}')
                    model_files = [
                        os.path.join(location, 'model.zip'),
                        os.path.join(location, 'contour_model.zip'),
                        os.path.join(location, 'params.json'),
                    ]
                    break
        if model_files is None:
            raise RuntimeError('could not find model files (searched /tmp, /tmp/mosamatic, /mnt/localscratch/cds/rbrecheisen/models/v2)')
        return model_files

    def execute(self):
        os.makedirs(self.output_directory, exist_ok=False)
        if 'dicom2nifti' in self.steps:
            # convert dicoms to nifti
            d2n = DicomToNifti()
            d2n.input_directory = self.input_directory
            d2n.output_file = os.path.join(self.output_directory, 'file.nii.gz')
            nifti_file = d2n.execute()
            if 'totalsegmentator' in self.steps:
                # run total segmentator to obtain l3 vertebra
                totalseg = TotalSegmentator()
                totalseg.input_file = nifti_file
                totalseg.output_directory = os.path.join(self.output_directory, 'totalseg')
                totalseg.fast = True
                output_dir = totalseg.execute()
                if 'selectroi' in self.steps:
                    # select l3 vertebra roi
                    selector = RoiSelector()
                    selector.input_directory = output_dir
                    selector.output_directory = os.path.join(self.output_directory, 'roi')
                    selector.roi = RoiSelector.VERTEBRAE_L3
                    roi_file = selector.execute()
                    if 'selectslice' in self.steps:
                        # select l3 slice
                        selector = SliceSelector()
                        selector.input_dicom_directory = self.input_directory
                        selector.input_roi = roi_file
                        selector.input_volume = nifti_file
                        selector.mode = SliceSelector.MEDIAN
                        l3_file = selector.execute()[0]
                        shutil.copy(l3_file, self.output_directory)
                        if 'l3seg' in self.steps:
                            # run l3 through muscle/fat segmentation
                            segmentator = MuscleFatSegmentator()
                            segmentator.input_files = [l3_file]
                            segmentator.image_dimensions = (512, 512)
                            segmentator.model_files = self.model_files
                            segmentator.mode = self.mode
                            segmentator.output_directory = os.path.join(self.output_directory, 'segmentator')
                            output_files = segmentator.execute()
                            for f in output_files:
                                print(f)
                            if 'calculate' in self.steps:
                                # calculte body composition metrics
                                # todo: output to CSV
                                calculator = BodyCompositionCalculator()
                                calculator.input_files = segmentator.input_files
                                calculator.input_segmentation_files = output_files
                                output_metrics = calculator.execute()
                                print(output_metrics)


if __name__ == '__main__':
    def main():

        parser = argparse.ArgumentParser()
        parser.add_argument('input_directory')
        parser.add_argument('output_directory')
        parser.add_argument('--mode', choices=['ARGMAX', 'PROBABILITIES'], default='ARGMAX')
        parser.add_argument('--steps', nargs='+')
        parser.add_argument('--model_files', nargs='+')
        args = parser.parse_args()
        print(args)

        pipeline = BodyCompositionPipeline(
            input_directory=args.input_directory,
            output_directory=args.output_directory, 
            model_files=args.model_files,
            steps=args.steps,
            mode=MuscleFatSegmentator.ARGMAX if args.mode == 'ARGMAX' else MuscleFatSegmentator.PROBABILITIES,
        )
        pipeline.execute()
    main()
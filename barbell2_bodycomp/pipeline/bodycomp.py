import os
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
                 model_files, 
                 mode=MuscleFatSegmentator.ARGMAX
                 ):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.model_files = model_files
        self.mode = mode

    def execute(self):
        # convert dicoms to nifti
        d2n = DicomToNifti()
        d2n.input_directory = self.input_directory
        d2n.output_file = os.path.join(self.output_directory, 'file.nii.gz')
        nifti_file = d2n.execute()
        # run total segmentator to obtain l3 vertebra
        totalseg = TotalSegmentator()
        totalseg.input_file = nifti_file
        totalseg.output_directory = os.path.join(self.output_directory, 'totalseg')
        totalseg.fast = True
        output_dir = totalseg.execute()
        # select l3 vertebra roi
        selector = RoiSelector()
        selector.input_directory = output_dir
        selector.output_directory = os.path.join(self.output_directory, 'roi')
        selector.roi = RoiSelector.VERTEBRAE_L3
        roi_file = selector.execute()
        # select l3 slice
        selector = SliceSelector()
        selector.input_dicom_directory = self.input_directory
        selector.input_roi = roi_file
        selector.input_volume = nifti_file
        selector.mode = SliceSelector.MEDIAN
        l3_file = selector.execute()[0]
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
        # calculte body composition metrics
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
        parser.add_argument('model_files', nargs='+', default=[])
        parser.add_argument('mode', choices=['ARGMAX', 'PROBABILITIES'])
        args = parser.parse_args()

        pipeline = BodyCompositionPipeline(
            input_directory=args.input_directory,
            output_directory=args.output_directory, 
            model_files=args.model_files,
            mode=MuscleFatSegmentator.ARGMAX if args.mode == 'ARGMAX' else MuscleFatSegmentator.PROBABILITIES,
        )
        pipeline.execute()
    main()

import os
import json
import zipfile
import logging
import pydicom
import numpy as np

from barbell2_bodycomp.utils import is_dicom_file, get_pixels

logger = logging.getLogger(__name__)


class MuscleFatSegmentator:

    ARGMAX = 0
    PROBABILITIES = 1

    def __init__(self):
        self.input_files = None
        # self.image_dimensions = None
        self.model_files = None
        self.mode = MuscleFatSegmentator.ARGMAX
        self.output_directory = None
        self.output_segmentation_files = None

    @staticmethod
    def load_model(file_path):
        import tensorflow as tf
        model_directory = '/tmp/barbell2_bodycomp/model'
        os.makedirs(model_directory, exist_ok=True)
        with zipfile.ZipFile(file_path) as zip_obj:
            zip_obj.extractall(path=model_directory)
        return tf.keras.models.load_model(model_directory, compile=False)

    @staticmethod
    def load_params(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def load_model_files(self):
        model, contour_model, params = None, None, None
        for file_path in self.model_files:
            file_name = os.path.split(file_path)[1]
            if file_name == 'model.zip':
                model = self.load_model(file_path)
            elif file_name == 'contour_model.zip':
                contour_model = self.load_model(file_path)
            elif file_name == 'params.json':
                params = self.load_params(file_path)
            else:
                logger.error(f'Unknown model file {file_name}')
        return model, contour_model, params

    @staticmethod
    def normalize(img, min_bound, max_bound):
        img = (img - min_bound) / (max_bound - min_bound)
        img[img > 1] = 0
        img[img < 0] = 0
        c = (img - np.min(img))
        d = (np.max(img) - np.min(img))
        img = np.divide(c, d, np.zeros_like(c), where=d != 0)
        return img

    def predict_contour(self, contour_model, src_img, params):
        ct = np.copy(src_img)
        ct = self.normalize(ct, params['min_bound_contour'], params['max_bound_contour'])
        img2 = np.expand_dims(ct, 0)
        img2 = np.expand_dims(img2, -1)
        pred = contour_model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        pred_max = pred_squeeze.argmax(axis=-1)
        mask = np.uint8(pred_max)
        return mask

    @staticmethod
    def convert_labels_to_157(prediction):
        new_prediction = np.copy(prediction)
        new_prediction[new_prediction == 1] = 1
        new_prediction[new_prediction == 2] = 5
        new_prediction[new_prediction == 3] = 7
        return new_prediction

    def execute(self):
        logger.info('Running MuscleFatSegmentator...')
        if self.input_files is None:
            logger.error('Input files not specified')
            return None
        # if self.image_dimensions is None:
        #     logger.error('Image dimensions not specified')
        #     return None
        if self.model_files is None:
            logger.error('Model files not specified')
            return None
        if self.output_directory is None:
            logger.error('Output directory not specified')
            return None
        os.makedirs(self.output_directory, exist_ok=True)
        model, contour_model, params = self.load_model_files()
        self.output_segmentation_files = []
        for f in self.input_files:
            f_name = os.path.split(f)[1]
            if is_dicom_file(f):
                p = pydicom.dcmread(f)
                # if dicom file compressed, decompress it before continuing
                img1 = get_pixels(p, normalize=True)
                if contour_model is not None:
                    mask = self.predict_contour(contour_model, img1, params)
                    img1 = self.normalize(img1, params['min_bound'], params['max_bound'])
                    img1 = img1 * mask
                else:
                    img1 = self.normalize(img1, params['min_bound'], params['max_bound'])
                img1 = img1.astype(np.float32)
                img2 = np.expand_dims(img1, 0)
                img2 = np.expand_dims(img2, -1)
                pred = model.predict([img2])
                pred_squeeze = np.squeeze(pred)
                print(pred_squeeze[256][256])
                if self.mode == MuscleFatSegmentator.ARGMAX:
                    pred_max = pred_squeeze.argmax(axis=-1)
                    pred_max = self.convert_labels_to_157(pred_max)
                    segmentation_file = os.path.join(self.output_directory, f'{f_name}.seg.npy')
                    self.output_segmentation_files.append(segmentation_file)
                    np.save(segmentation_file, pred_max)
                elif self.mode == MuscleFatSegmentator.PROBABILITIES:
                    segmentation_file = os.path.join(self.output_directory, f'{f_name}.seg.prob.npy')
                    self.output_segmentation_files.append(segmentation_file)
                    np.save(segmentation_file, pred_squeeze)
                else:
                    logger.warn(f'Unknown mode {self.mode}')
            else:
                logger.warning(f'File {f} is not a valid DICOM file')
        return self.output_segmentation_files


if __name__ == '__main__':
    def main():
        segmentator = MuscleFatSegmentator()
        # segmentator.input_files = ['/Users/ralph/Desktop/SliceSelector/L3.dcm']
        segmentator.input_files = ['/mnt/localscratch/cds/rbrecheisen/raw/pancreas-demo-1/1.dcm']
        # segmentator.image_dimensions = (512, 512)
        segmentator.model_files = [
            '/mnt/localscratch/cds/rbrecheisen/models/v2/model.zip',
            '/mnt/localscratch/cds/rbrecheisen/models/v2/contour_model.zip',
            '/mnt/localscratch/cds/rbrecheisen/models/v2/params.json',
        ]
        # segmentator.mode = MuscleFatSegmentator.ARGMAX
        segmentator.mode = MuscleFatSegmentator.PROBABILITIES
        segmentator.output_directory = '/tmp/barbell2/bodycomp/seg.py'
        files = segmentator.execute()
        for f in files:
            print(f)
    main()

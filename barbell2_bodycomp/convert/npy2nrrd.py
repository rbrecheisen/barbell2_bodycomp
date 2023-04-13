import numpy as np
import nrrd


class Numpy2Nrrd:

    def __init__(self, npy_array_or_file_path, output_file_path):
        self.npy_array_or_file_path = npy_array_or_file_path
        self.output_file_path = output_file_path
        self.index_order = 'C'

    def execute(self):
        if isinstance(self.npy_array_or_file_path, str):
            npy_array = np.load(self.npy_array_or_file_path)
        else:
            npy_array = self.npy_array_or_file_path
        nrrd.write(self.output_file_path, npy_array)


def main():
    from barbell2.converters.tag2npy import Tag2Numpy
    t2n = Tag2Numpy('data/file.tag', shape=(512, 512))
    npy_array = t2n.execute()
    print(np.unique(npy_array))
    np.save('data/file.npy', npy_array)
    n2n = Numpy2Nrrd(npy_array, 'data/file.nrrd')
    n2n.execute()


if __name__ == '__main__':
    main()

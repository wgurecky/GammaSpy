"""!
@biref Wapper around some parts of xylib to parse Genie *.CNF files.
Also allows read/write to HDF5
"""
import os
from six import iteritems
import xylib
import h5py
import numpy as np


class DataReader(object):
    """!
    @biref Wapper around some parts of xylib to parse Genie *.CNF files.
    Also allows read/write to HDF5
    """
    def __init__(self):
        pass

    def _export_metadata(self, meta):
        """!
        @brief Read metadata from CNF file
        """
        metadata = {}
        for i in range(meta.size()):
            key = meta.get_key(i)
            value = meta.get(key)
            metadata[key] = value
        return metadata

    def _readXY(self, fname, i=0):
        """!
        @brief Read data from CNF file
        """
        xy_data = xylib.load_file(fname)
        print("Reading data by xylib from file format: %s \n" % xy_data.fi.name)
        block = xy_data.get_block(i)
        metadata_raw = self._export_metadata(block.meta)

        ncol = block.get_column_count()
        # column 0 is pseudo-column with point indices, we skip it
        col_names = [block.get_column(k).get_name() or ('column_%d' % k)
                     for k in range(1, ncol+1)]
        nrow = block.get_point_count()
        count_energy = np.zeros((nrow, 2))
        for j in range(nrow):
            values = ["%.6f" % block.get_column(k).get_value(j)
                      for k in range(1, ncol+1)]
            count_energy[j, :] = np.array([float(v) for v in values])
        # convert raw metadata from cnf file to clean format
        metadata = {'e_cal': []}
        for key, val in iteritems(metadata_raw):
            if key.split(' ')[0] == 'live':
                metadata['l_time'] = float(val)
            elif key.split(' ')[0] == 'real':
                metadata['r_time'] = float(val)
            elif key.split(' ')[0] == 'energy':
                metadata['e_cal'].append(float(val))
        return [metadata, count_energy]

    def _readHDF5(self, fname, chan=0):
        """!
        @brief Reads count vs energy data from HDF5 file and
        energy calibration data (if present)
        @param fname String.  Name of file.
        @return [metadata, count_energy]
        """
        h5f = h5py.File(fname, 'r')
        count_energy = h5f[str(chan) + '/spectrum'][:]
        metadata = {}
        metadata['e_cal'] = h5f[str(chan) + '/e_cal'][:]
        metadata['live_time'] = h5f[str(chan) + '/l_time']
        metadata['real_time'] = h5f[str(chan) + '/r_time']
        h5f.close()
        return [metadata, count_energy]

    def read(self, fname, chan=0):
        """!
        @brief Read external CNF or HDF5 file into numpy arrays
        @return [metadata, count_energy]
        """
        if type(fname) is tuple:
            fname = fname[0]
        _, ext = os.path.splitext(fname)
        if ext == '.h5' or ext == '.hdf5':
            return self._readHDF5(fname, chan)
        return self._readXY(fname)

    def write(self, fname, metadata, spectrum, peak_info=None):
        """!
        @brief Write spectrum data and fitted peak info to HDF5 file
        @param fname String.  output filename
        @param metadata dict.
        @param spectrum  Numpy 2D array (counts vs energy)
        @param peak_info array of peak parameters
        """
        h5f = h5py.File(fname, 'w')
        h5f.create_dataset('0/spectrum', data=spectrum)
        h5f.create_dataset('0/e_cal', data=metadata['e_cal'])
        h5f.create_dataset('0/l_time', data=metadata['l_time'])
        h5f.create_dataset('0/r_time', data=metadata['r_time'])
        h5f.close()


if __name__ == "__main__":
    """!
    @brief Run from cmd line
    """
    dreader = DataReader()
    mdata, edata = dreader.read('../../examples/data/NORM-H2O.CNF')
    # write to h5 file
    dreader.write('testout.h5', mdata, edata)

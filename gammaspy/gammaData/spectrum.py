"""!
@brief Defines spectrum actions such as
find all peaks in spectrum
"""
import peak as pk
import roi
import numpy as np


class GammaSpectrum(object):
    def __init__(self, spectrum):
        self.spectrum = spectrum
        self.peak_bank = {}

    def add_peak(self, peak_loc, peak_model='gauss', bg_model='linear'):
        self.peak_bank[peak_loc] = roi.Roi(self.spectrum, peak_loc)

    def mod_peak(self, peak_loc, peak_model='gauss', bg_model='linear'):
        """!
        @brief Modify selected peak's background and or peak model
        """
        pass

    def del_peak(self, peak_loc):
        return self.peak_bank.pop(peak_loc, None)

    def peak_locs(self):
        peak_locs = np.array(self.peak_bank.keys())
        return peak_locs

    def find_peaks(self):
        """!
        @brief Attempt automatic peak detection.
        """
        pass

    def auto_roi(self, peak_locs=[]):
        """!
        @brief Attempt auto ROI for all selected peaks.
        @brief peak_locs  list of peaks to attempt auto ROI estimation
        """
        if peak_locs is None:
            peak_locs = self.peak_locs()
        pass

    def fit_peak(self, peak_loc):
        """!
        @breif Fit selected peak to data.
        Simulataneously fits background and peak.
        """
        pass

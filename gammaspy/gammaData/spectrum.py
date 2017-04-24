"""!
@brief Defines spectrum actions such as
find all peaks in spectrum
"""
import peak as pk
import roi
import numpy as np
from scipy.signal import find_peaks_cwt


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

    def find_cwt_peaks(self, widths=[1., 2., 3., 4., 5., 7.5, 10., 15., 20., 30.], **kwargs):
        """!
        @brief Automatic peak detection by the continuous wavelet transform method.
        """
        cwt_peaks = find_peaks_cwt(self.spectrum, widths, **kwargs)
        return cwt_peaks

    def find_gradient_peaks(self, **kwargs):
        pass

    def auto_peaks(self, method='cwt', **kwargs):
        """!
        @brief Auto find all peaks in spectrum.
        """
        for peak_loc in self.find_cwt_peaks(**kwargs):
            self.add_peak(peak_loc)

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
        try:
            self.peak_bank[peak_loc].fit()
        except:
            print("Peak fitting failed.")

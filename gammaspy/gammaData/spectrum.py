"""!
@brief Defines spectrum actions such as
find all peaks in spectrum
"""
import gammaspy.gammaData.peak as pk
import gammaspy.gammaData.roi as roi
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

    def pop_peak(self, peak_loc):
        """!
        @brief Deletes and returns peak.
        """
        popped_peak = self.peak_bank.pop(peak_loc, None)
        print("-----------------------------------------")
        print("Removed Peak: %f " % popped_peak.centroid)
        print(popped_peak)
        print("Remaining Peaks:")
        print(self.peak_bank.keys())
        print("-----------------------------------------")

    def del_all_peaks(self):
        self.peak_bank = {}

    def peak_locs(self):
        peak_locs = np.array(self.peak_bank.keys())
        return peak_locs

    def find_cwt_peaks(self, widths=[5.0, 7.5, 10., 15., 20., 25.], **kwargs):
        """!
        @brief Automatic peak detection by the continuous wavelet transform method.
        """
        noise = kwargs.get("noise_perc", 20)
        min_snr = kwargs.get("min_snr", 1.5)
        cut = kwargs.pop("cut", 40)  # max number of peaks to retain
        cwt_peaks_idxs = find_peaks_cwt(self.spectrum[:, 1], widths, min_snr=min_snr, noise_perc=noise, **kwargs)
        print("N auto Peak Locations = %d" % len(cwt_peaks_idxs))
        print("-----------------------")
        cwt_peaks = self.spectrum[cwt_peaks_idxs, 0]
        print(cwt_peaks)
        return cwt_peaks[:cut]

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
        for peak_loc in peak_locs:
            self.peak_bank[peak_loc].find_roi()

    def fit_peak(self, peak_loc):
        """!
        @breif Fit selected peak to data.
        Simulataneously fits background and peak.
        """
        try:
            self.peak_bank[peak_loc].fit()
        except:
            print("Peak fitting failed.")

"""!
@brief Module roi.
Contains region of interest model def
"""
from __future__ import division
import peak
import bg
from scipy.odr import Model, Data, ODR
import numpy as np


class Roi(object):
    """!
    @brief Region of interest (ROI)
    which can be further broken into three subregions:
    a left background, peak, and right background.
    @verbatim
                   .._.
                 ._    _.
                _        _
    ....----._.-          --_...-..._....
    |   l_bg   |   peak     |   r_bg   |
    @endverbatim
    """
    def __init__(self, spectrum, centroid=1000.):
        self._centroid = centroid
        self.bg_bounds = [self._centroid - 50.,
                          self._centroid - 40.,
                          self._centroid + 40.,
                          self._centroid + 50.]
        self._peak_models = ["gauss"]
        self._bg_models = ["linear"]
        # composition
        self.peak_model = peak.GaussModel([1., self._centroid, np.sqrt(self._centroid)])
        self.bg_model = bg.LinModel()
        self._init_params = np.concatenate((self.bg_model.params, self.peak_model.params))
        # data stor
        self.update_data(spectrum)

    def update_data(self, spectrum):
        selection = (spectrum[:, 0] > self.bg_bounds[0]) & (spectrum[:, 0] < self.bg_bounds[-1])
        self.roi_data = spectrum[selection]

    @property
    def centroid(self):
        """!
        @brief Peak center
        """
        return self._centroid

    @property
    def peak_models(self):
        """!
        @brief Peak models to consider when fitting.
        """
        return self._peak_models

    @property
    def bg_models(self):
        """!
        @brief Background models to consider when fitting.
        """
        return self._peak_models

    @property
    def init_params(self):
        return self._init_params

    @init_params.setter
    def init_params(self, init_params):
        self._init_params = init_params

    def set_peak_model(self):
        """!
        @brief Set ODR model
        """
        x = self.roi_data[:, 0]
        y = self.roi_data[:, 1]
        data = Data(x, y)
        #
        bgn = len(self.bg_model.params)
        tot_model = lambda p, X: self.bg_model.eval(p[:bgn], X) + self.peak_model.eval(p[bgn:], X)
        self.odr_model = ODR(data, tot_model, beta0=self._init_params)

    def net_area(self):
        """!
        @brief Peak - Background
        """
        pass

    def total_area(self):
        """!
        @brief Integral of peak + bg
        """
        pass

    def fit(self):
        """!
        @brief Fit model via non linear least squares.
        Simulataneously fits background and peak
        """
        self.set_peak_model()
        # 1SD uncert in fitted params = self.fit_output.sd_beta
        # fitted func values at input x = self.fit_output.y
        self.fit_output = self.odr_model.run()

    def fit_mcmc(self):
        """!
        @brief Fit peak by marcov chain monte carlo
        """
        pass

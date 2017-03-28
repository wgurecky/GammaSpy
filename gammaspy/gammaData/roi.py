"""!
@brief Module roi.
Contains region of interest model def
"""
from __future__ import division


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
    def __init__(self, centroid=None):
        self._centroid = centroid
        self._bg_bounds = (0., 0., 0., 0.)
        self._fwhm = 0.
        self._peak_models = ["gauss"]
        self._bg_models = ["linear"]
        # composition
        self.peak_model = None
        self.bg_model = None

    @property
    def centroid(self):
        """!
        @brief Peak mean
        """
        return self._centroid

    @property
    def fwhm(self):
        """!
        @brief Full width half maximum
        """
        return self._fwhm

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

    @bg_bounds.setter
    def bg_bounds(self, bg_bounds_in):
        """!
        @brief Sets background bounds
        """
        if len(bg_bounds_in) != 4:
            return ValueError("Must specify length 4 tuple")
        else:
            self._bg_bounds = bg_bounds_in

    @property
    def bg_bounds(self):
        """!
        @brief Background bounds.
        """
        # (bgl_lower, bgl_upper, bgr_lower, bgr_upper)
        return self._bg_bounds

    def net_area(self):
        """!
        @brief Peak - Background
        """
        pass

    def raw_area(self):
        """!
        @brief Integral of peak
        """
        pass

    def fit(self, method="SLSQP", peak=True, bgrnd=True, *args0):
        """!
        @brief Fit peak model by maximum liklihood /
        non linear least squares.
        Simulataneously fits background and peak or p
        """
        pass

    def fit_mcmc(self, peak=True, bgrnd=True, *args0):
        """!
        @brief Fit peak by marcov chain monte carlo
        """
        pass

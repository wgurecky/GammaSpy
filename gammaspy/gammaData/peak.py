"""!
@brief Module peak
Contains peak model def
"""
from __future__ import division
import numpy as np
import numdifftools as nd
from scipy.special import erf


class GaussModel(object):
    """!
    @brief Gaussian model of the form:
    \f[
    y(x) = a\ e^{\frac{-(x - b)^2}{2c^2}}
    \f]
    Where $a$ is the scaling factor
    $b$ is the mean
    and $c$ is the std. deviation.
    """
    def __init__(self, init_params=[1., 1., 1.], **kwargs):
        self.name = kwargs.pop("name", "gauss")
        # ((min bounds), (max param bounds))
        self.bounds = ((0., 0., 0.), (np.inf, 3000., 15.))
        self._params = init_params
        self.model_trust = 1

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        if params is None:
            self._params = [100., 100., 100.]
        else:
            assert(len(params) == 3)
            self._params = params

    def eval(self, params, x):
        """!
        @brief Eval Gauss model for ODR pack.
        ODR pack likes f([params], x) argument arrangement.
        @param params  Gaussian model parameter array (len=3)
        @param x np_array of abscissa to evaluate gauss model at
        @return np_array value of gauss model at specified points.
        """
        gauss_f = params[0] * np.exp((-1. * (x - params[1]) ** 2) / (2. * params[2] ** 2))
        return gauss_f

    def opti_eval(self, x, *params):
        """!
        @brief Identical to eval, with flipped argument positions.
        Scipy optimization routines typically like f(x, *params) format.
        @param x np_array of abscissa to evaluate gauss model at
        @param params  Gaussian model parameter array (len=3)
        """
        gauss_f = params[0] * np.exp((-1. * (x - params[1]) ** 2) / (2. * params[2] ** 2))
        return gauss_f

    def integral(self, a, b, params):
        """!
        @brief Compute definite integral of general gaussian model.
        @param a Start.
        @param b End.
        @param params  Gaussian model parameter array (len=3)
        """
        a = np.sqrt(np.pi / 2.) * -params[0] * params[2]
        b_f = erf((params[1] - b) / (np.sqrt(2.) * params[2]))
        b_i = erf((params[1] - a) / (np.sqrt(2.) * params[2]))
        return a * (b_f - b_i)

    def int_hess(self, a, b, params):
        """!
        @brief Computes hessian of gaussian integral for
        area uncertainty calculations.
        \f[
        H^-1 \approx C
        \f]
        Where $C$ is the covar matrix and $H$ is the hessian.
        """
        reduced_int = lambda p: self.integral(a, b, p)
        hess_matrix = nd.Hessian(reduced_int)(params)
        return hess_matrix

    def int_jac(self, a, b, params):
        reduced_int = lambda p: self.integral(a, b, p)
        jac = nd.Jacobian(reduced_int)(params)
        return jac

    def area(self, params):
        """!
        @brief  Computes area under entire gauss peak
        on $(-\infty, \infty)$.
        \f[
        A = H * sigma * sqrt(2 *\pi)
        \f]
        Where $H=f(\mu)$
        """
        ar = self.eval(params, params[1]) * np.abs(params[2]) * np.sqrt(2. * np.pi)
        return ar

    def area_hess(self, params):
        """!
        @brief Compute hessian of gaussian area function
        """
        hess_matrix = nd.Hessian(self.area)(params)
        return hess_matrix

    def area_jac(self, params):
        jac = nd.Jacobian(self.area, step=1e-6)(params)
        return jac

    def fwhm(self, params):
        """!
        @brief Compute full width half max of gaussian
        """
        return 2.35482 * params[2]

class DblGaussModel(object):
    def __init__(self, init_params=[1., 1., 1., 2., 2., 2.], **kwargs):
        self.name = kwargs.pop("name", "dblgauss")
        self.bounds = ((0., 0., 0., 0., 0., 0.), (np.inf, np.inf, np.inf, np.inf, np.inf, np.inf))
        self._params = init_params
        self.gauss_1 = GaussModel(self._params[:3])
        self.gauss_2 = GaussModel(self._params[3:])
        self.model_trust = 0.5

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        if params is None:
            self._params = [100., 100., 100., 120, 120, 120]
        else:
            assert(len(params) == 6)
            self._params = params

    def eval(self, params, x):
        gauss_f_1 = self.gauss_1.eval(params[:3], x)
        gauss_f_2 = self.gauss_2.eval(params[3:], x)
        return gauss_f_1 + gauss_f_2

    def opti_eval(self, x, *params):
        gauss_f_1 = self.gauss_1.eval(params[:3], x)
        gauss_f_2 = self.gauss_2.eval(params[3:], x)
        return gauss_f_1 + gauss_f_2

    def integral(self, a, b, params):
        gauss_int_1 = self.gauss_1.integral(a, b, params[:3])
        gauss_int_2 = self.gauss_2.integral(a, b, params[3:])
        return gauss_int_1 + gauss_int_2

    def int_jac(self, a, b, params):
        reduced_int = lambda p: self.integral(a, b, p)
        jac = nd.Jacobian(reduced_int)(params)
        return jac

    def area(self, params):
        gauss_area_1 = self.gauss_1.area(params[:3])
        gauss_area_2 = self.gauss_2.area(params[3:])
        return gauss_area_1 + gauss_area_2

    def area_hess(self, params):
        hess_matrix = nd.Hessian(self.area)(params)
        return hess_matrix

    def area_jac(self, params):
        jac = nd.Jacobian(self.area)(params)
        return jac

    def fwhm(self, params):
        return self.gauss_1.fwhm(params[:3]), self.gauss_2.fwhm(params[3:])


def peak_model_factory(name, **kwargs):
    """!
    @brief Given string, return correct peak class.
    @param name String.  "gauss" or "dblgauss"
    @return GaussModel instance
    """
    init_params = kwargs.pop("params", None)
    if name == "gauss":
        return GaussModel(init_params)
    elif name == "dblgauss":
        return DblGaussModel(init_params)
    else:
        return GaussModel(init_params)


if __name__ == "__main__":
    gs = GaussModel()
    print(gs.area([4.,4.,4.]))
    print(gs.integral(-20., 20., [4., 4., 4.]))
    print(gs.area_jac([4., 4., 4.]))

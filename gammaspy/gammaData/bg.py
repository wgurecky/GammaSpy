"""!
@brief Module background
Contains background model def
"""
from __future__ import division
import numpy as np
import numdifftools as nd


class LinModel(object):
    """!
    """
    def __init__(self, init_params=[1., 1.]):
        self._params = init_params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        if params is None:
            self._params = [0., 100.]
        else:
            assert(len(params) == 2)
            self._params = params

    def eval(self, params, x):
        """!
        """
        model_f = params[0] * x + params[1]
        return model_f

    def integral(self, a, b, params):
        """!
        @brief Compute definite integral of general gaussian model.
        @param a Start.
        @param b End.
        @param params  Gaussian model parameter array (len=3)
        """
        f_f = params[0] * b ** 2. / 2. + params[1] * b
        f_i = params[0] * a ** 2. / 2. + params[1] * a
        return f_f - f_i

    def int_hess(self, a, b, params):
        """!
        @brief Computes hessian of integral for
        area uncertainty calculations.
        \f[
        H^-1 \approx C
        \f]
        Where $C$ is the covar matrix and $H$ is the hessian.
        """
        reduced_int = lambda p: self.integral(a, b, p)
        jac = nd.Jacobian(reduced_int)(params)
        h_approx = np.dot(jac.T, jac)
        return h_approx


def bg_model_factory(name, **kwargs):
    """!
    @brief Given string, return correct bg class
    @param name String.  "linear" or "quadratic"
    @return BgModel instance
    """
    init_params = kwargs.pop("params", None)
    if name == "linear":
        return LinModel(init_params)
    else:
        return LinModel(init_params)


if __name__ == "__main__":
    lm = LinModel()
    print(lm.integral(0, 20., [0., 100.]))
    print(lm.int_hess(0, 20., [0., 100.]))

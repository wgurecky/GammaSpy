"""!
@brief Module background
Contains background model def
"""
from __future__ import division
import numpy as np
import numdifftools as nd


class LinModel(object):
    """!
    @brief Linear background model.
    """
    def __init__(self, init_params=[0., 100.], **kwargs):
        self.name = kwargs.pop("name", "linear")
        self.bounds = ((-np.inf, -np.inf), (np.inf, np.inf))
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
        @brief Evaluate the linear background model
        """
        model_f = params[0] * x + params[1]
        return model_f

    def opti_eval(self, x, *params):
        model_f = params[0] * x + params[1]
        return model_f

    def integral(self, a, b, params):
        """!
        @brief Compute definite integral of linear model.
        @param a Start.
        @param b End.
        @param params  model parameter array (len=2)
        """
        f_f = params[0] * b ** 2. / 2. + params[1] * b
        f_i = params[0] * a ** 2. / 2. + params[1] * a
        return f_f - f_i

    def int_jac(self, a, b, params):
        """!
        @brief Computes jacobian of integral for
        area uncertainty calculations.
        \f[
        H^-1 \approx C
        \f]
        Where $C$ is the covar matrix and $H$ is the jacobian.
        """
        reduced_int = lambda p: self.integral(a, b, p)
        jac = nd.Jacobian(reduced_int, step=1e-8)(params)
        return jac


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
    print(lm.int_jac(0, 20., [0., 100.]))

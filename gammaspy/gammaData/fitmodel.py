from gammaspy.gammaData import peak, bg
import numpy as np
from six import iteritems


class FitModel(object):
    """!
    @brief Combines background and peak models via Composition.
    """
    def __init__(self, bg_order=1, n_peaks=1, peak_centers=[1000.]):
        self.model_params = np.array([])
        self.model_params_bounds = [[],[]]
        self.model_bank = {}
        self.build(bg_order, n_peaks, peak_centers)

    def build(self, bg_order, n_peaks, peak_centers):
        """!
        @brief Quickly build a multi-peak model with background
        """
        bg_model = bg.LinModel()  # todo add more bg model flexibility
        self.add_model(bg_model)
        for i in range(n_peaks):
            name = "gauss_" + str(i)
            self.add_model(peak.GaussModel(init_params=[100., peak_centers[i], 1.],
                                           name=name))

    def add_model(self, in_model):
        """!
        @brief Add a sub-model to the total model.
        Appends models sequentially
        """
        self.model_bank[in_model.name] = {}
        self.model_bank[in_model.name]["model"] = in_model
        input_model_nparams = len(in_model._params)
        current_nparams = len(self.model_params)
        self.model_params = np.concatenate((self.model_params, in_model._params))
        self.model_bank[in_model.name]["idxs"] = list(range(current_nparams, current_nparams + input_model_nparams))
        # parameter bounds for optimization
        self.model_params_bounds[0] += in_model.bounds[0]
        self.model_params_bounds[1] += in_model.bounds[1]
        print("Model Added: %s" % in_model.name)

    def opti_eval(self, x, *params):
        """!
        @brief Evaluates all sub models.
        Automatically partitions *params list into sublists
        for each submodel.
        @param x np_array of abscissa to evaluate gauss model at
        @param params  Gaussian model parameter array (len=3)
        """
        output = np.zeros(len(x))
        for model_name, model in iteritems(self.model_bank):
            #output += model["model"].opti_eval(x, *params[model["idxs"]])
            output += model["model"].eval(np.array(params)[model["idxs"]], x)
        return output

    def set_params(self, params):
        """!
        @biref Freeze internal model parameters.
        """
        if len(params) == len(self.model_params):
            self.model_params = params
        else:
            print("WARNING: invalid number of parameters specified")

    def set_cov(self, cov):
        self.model_params_cov = cov

    def eval(self, x):
        """!
        @biref Evaluate model.
        """
        output = np.zeros(len(x))
        for model_name, model in iteritems(self.model_bank):
            output += model["model"].eval(np.array(self.model_params)[model["idxs"]], x)
        return output

    def net_area(self):
        """!
        @brief Area with background subtracted.
        """
        peak_area_list, net_area = [], 0.
        for model_name, model in iteritems(self.model_bank):
            if "gauss" in model_name:
                area = model["model"].area(np.array(self.model_params)[model["idxs"]])
                net_area += area
                peak_area_list.append(area)
        return net_area, peak_area_list

    def net_area_uncert(self, lbound, ubound, cov):
        """!
        @brief Computes Jacobian of the area fn for uncertainty calcs.
        @param lbound Float. Lower bound of ROI (for integral of bg model)
        @param ubound Float. Upper bound of ROI (for integral of bg model)
        @param covariance matrix
        @return total area 1sigma uncert and list of individual submodel 1sigma uncerts
        """
        assert(cov.shape[0] == len(self.model_params))
        assert(cov.shape[1] == len(self.model_params))
        area_jac_all = np.array([])
        for model_name, model in iteritems(self.model_bank):
            if "gauss" in model_name:
                # jacobian of a gaussian peak area
                area_jac = model["model"].area_jac(np.array(self.model_params)[model["idxs"]])
            else:
                # jacobian of area under the bg model
                area_jac = model["model"].int_jac(lbound, ubound, np.array(self.model_params)[model["idxs"]])
            if len(area_jac.shape) == 2:
                area_jac_all = np.concatenate((area_jac_all, area_jac[0]))
            else:
                area_jac_all = np.concatenate((area_jac_all, area_jac))
        # std prop of uncetainty J * C * J.T
        net_uncert = np.dot(area_jac_all, cov)
        net_uncert = np.dot(net_uncert, area_jac_all)
        peak_area_list = np.array(self.net_area()[1])
        peak_area_ratio = peak_area_list / np.sum(peak_area_list)
        peak_area_uncerts = net_uncert * (peak_area_ratio)
        # return varience, not SD!
        return net_uncert, peak_area_uncerts

    def peak_means(self):
        """!
        @brief Mean of each subpeak
        """
        peak_means = []
        for model_name, model in iteritems(self.model_bank):
            if "gauss" in model_name:
                # mean of gaussian peak
                peak_means.append(np.array(self.model_params)[model["idxs"]][1])
        return peak_means

    def peak_sigmas(self):
        """!
        @brief Mean of each subpeak
        """
        sigmas = []
        for model_name, model in iteritems(self.model_bank):
            if "gauss" in model_name:
                # 1sd of gaussian peak
                sigmas.append(np.abs(np.array(self.model_params)[model["idxs"]][2]))
        return sigmas

    def tot_area(self):
        """!
        @brief Total area under the model.
        """
        pass

    def pprint_params(self):
        """!
        @brief Return nicely formatted table of fitted parameters.
        """
        pass

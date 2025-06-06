import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime


def model_poly1(x, a, b):
    return a + b * x


def model_poly2(x, a, b, c):
    return model_poly1(x, a, b) + c * x * x


def model_poly3(x, a, b, c, d):
    return model_poly2(x, a, b, c) + d * x * x * x


def model_annual(x, a, b):
    return a * np.sin(x * 2 * np.pi / 365.25) + b * np.cos(x * 2 * np.pi / 365.25)


def model_exponential(x, a, b, c):
    x = normalize(x)  # normalize ordinal dates to avoid overflow
    return a + b * np.exp(c * x)


def normalize(x):
    return (x - x.min()) / (x.max() - x.min())


class FittingModels:
    def __init__(self, x=None, y=None, model="poly-1"):
        self.x = x
        self.y = y
        self.model = model
        self.ordinal_dates = self.datesToOrdinal()

    def datesToOrdinal(self):
        return np.array([x.toordinal() for x in self.x])

    def ordinalTodates(self, ordinals):
        return [datetime.fromordinal(int(x)) for x in ordinals]

    def fit(self, model=None, seasonal=False):
        x = self.ordinal_dates
        y = self.y
        if model is None:
            model = self.model
        fit_models_dict = {"poly-1": model_poly1, "poly-2": model_poly2,
                           "poly-3": model_poly3, "exp": model_exponential}
        fit_model = fit_models_dict[model]
        popt, pcov = curve_fit(fit_model, x, y)
        model_x_linspace = np.linspace(min(x), max(x), 100)
        model_x = self.ordinalTodates(model_x_linspace)
        model_y = fit_model(model_x_linspace, *popt)
        fit_y = fit_model(x, *popt)

        if seasonal:
            popt_seasonal, _ = curve_fit(model_annual, x, y-fit_y)
            model_y_seasonal = model_annual(model_x_linspace, *popt_seasonal)
            fit_y_seasonal = model_annual(x, *popt_seasonal)
            model_y += model_y_seasonal
            fit_y += fit_y_seasonal

        return fit_y, model_x, model_y

    def fitVelocity(self):
        x = self.ordinal_dates
        y = self.y
        popt, pcov = curve_fit(model_poly1, x, y)
        return popt[1]*365.25

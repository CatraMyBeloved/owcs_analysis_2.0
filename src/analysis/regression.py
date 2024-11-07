import numpy as np
from scipy.optimize import curve_fit
from sklearn import linear_model


class Regression:
    def __init__(self, data):
        self._data = data

    def logistic_regression(self, x, y):
        log_model = linear_model.LogisticRegression()
        log_model.fit(x, y)
        return log_model

    def linear_regression(self, x, y):
        lin_model = linear_model.LinearRegression()
        lin_model.fit(x, y)
        return lin_model

    def custom_fit(self, x, y, function):
        best_parameters, covariance = curve_fit(function, x, y)
        return best_parameters, covariance
from numpy import sin



phiListForTest = [sin]


import numpy as np


def gauss(mu, sigma):
    return lambda x: np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def logNormal(mu, sigma):
    return lambda x: np.exp(-0.5 * ((np.log(x) - mu) / sigma) ** 2) / (sigma * x * np.sqrt(2 * np.pi))

def logNormalFitting(x, mu, sigma, norma):
    return np.exp(-0.5 * ((np.log(x) - mu) / sigma) ** 2) / (sigma * x * np.sqrt(2 * np.pi)*norma)



import numpy as np
import matplotlib.pyplot as plt
from numpy import vectorize, ndarray
from functools import partial
from scipy.integrate import quad
from typing import Union


# gaussKernel = lambda sigma: lambda x, y: \
#     np.exp(-0.5 * ((x - y) ** 2) / sigma * sigma) / (sigma * np.sqrt(2 * np.pi))


## Набор дифферернциальных ядер из оптики

# щелеобразная
def rectangular(x : Union[ndarray, float], alpha: float = 1.) -> Union[ndarray, float]:
    if type(x) != np.ndarray:
        if (np.abs(x)/alpha < 0.5):
            return 1./alpha
        else:
            return 0.
    else:
        indx = np.abs(x)/alpha < 0.5
        return (indx)/alpha

# af1 = np.vectorize(af1, excluded=['alpha'])
# дифракционная
def diffraction(x : Union[ndarray, float], alpha: float = 1.) -> Union[ndarray, float]:
    s0 = alpha/0.886
    res = (np.sin(np.pi * x / s0) / (np.pi * x / s0)) ** 2 / (s0)
    return res
# гауссова
def gaussian(x : Union[ndarray, float], alpha: float = 1.) -> Union[ndarray, float]:
    return (2/alpha)*np.sqrt(np.log(2)/np.pi)*np.exp(-4*np.log(2)*(x/alpha)**2)
# треугольная
def triangular(x : Union[ndarray, float], alpha: float = 1.) -> Union[ndarray, float]:
    if type(x) != np.ndarray:
        if (np.abs(x)/alpha <= 1):
            return (1-np.abs(x)/alpha)/alpha
        else:
            return 0
    else:
        indx = np.abs(x)/alpha < 0.5
        return (indx)*(1-np.abs(x)/alpha)/alpha
# дисперсионная
def dispersive(x :Union[ndarray, float], alpha: float = 1.) -> Union[ndarray, float]:
    return (alpha/(2*np.pi))/(x**2 + (alpha/2)**2)
# экспоненциалная
def exponential(x : Union[ndarray, float], alpha: float = 1.) -> Union[ndarray, float]:
    return (np.log(2)/alpha)*np.exp(-2*np.log(2)*(np.abs(x)/alpha))

_opticsKernels = [rectangular,
                  triangular,
                  gaussian,
                  diffraction,
                  dispersive,
                  exponential]



def convolveFunc(K, phi, ym, boundary):
    a, b = boundary
    n = ym.shape[0]
    res = np.zeros(n)
    for i in range(n):
        res[i] = quad(lambda x: K(x,ym[i])*phi(x),a,b)[0]
    return res


if __name__ == '__main__':
    x = np.linspace(-3,3, 100)

    for f in _opticsKernels:
        plt.plot(x, f(x))
    plt.show()

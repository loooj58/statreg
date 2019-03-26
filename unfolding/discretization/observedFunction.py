import numpy as np
from numpy import ndarray
from typing import List, Callable

from unfolding.interface import IUnfoldingResult
from ..interface.ibasis import IBasis

from numpy.core.multiarray import ndarray

from unfolding.interface.interface import IModelParameter, ICheckoutInformation
from unfolding.interface.iObservedFunction import IObservedFunction, IUniformObservedFunction
from .pointWise import PointWiseBasis


class ObservedFunction(IObservedFunction):
    def __call__(self, x: ndarray):
        res = self.coef[0] * self.bf[0](x)
        for i in range(1, len(self.bf)):
            res += self.coef[i] * self.bf[i](x)
        return res


class UniformObservedFunction(IUniformObservedFunction, ObservedFunction):
    """
    UniformObservedFunction(self, coef, bf, sig=None, original_phi=None, a=None, b=None)
    Generalized Vector for discretization of true function class.
    Parameters
    ----------
    coef : ndarray
        Coeficient (phi vector) for basis function.
    bf : list of function
        List of basis function
    covariance : 2darray, optional
        Covariance matrix of phi vector
    a : float, optional
        Left boundary of interval of domain function
    b : float, optional
        Right boundary of interval of domain function
    Returns
    -------
    UniformObservedFunction : callable
        Phi vector of function.
    """

    def __init__(self, coef: ndarray, covariance: ndarray = None, basis: IBasis = None):
        if basis is None:
            self.basis = PointWiseBasis(coef.shape[0], (coef[0], coef[1]))
        else:
            self.basis = basis


        self.coef = coef
        self.covariance = covariance
        # self.a = self.basis.
        # self.b = b
        self.bf = self.basis.bf

    def error(self, x: ndarray) -> ndarray:
        bfValue = np.array([f(x) for f in self.bf])
        if type(x) != np.ndarray:
            return (np.dot(np.dot(bfValue, self.covariance), bfValue)) ** 0.5
        else:
            res = np.zeros(x.shape[0])
            for indx, val in enumerate(bfValue.T):
                res[indx] = np.dot(np.dot(val, self.covariance), val)
            return res ** 0.5


class UniformUnfoldingResult(IUnfoldingResult):
    def __init__(self, observedSignal: UniformObservedFunction = None, modelParameter: IModelParameter =None, checkoutInformation: ICheckoutInformation = None):
        self.observedSignal = observedSignal
        self.modelParameter = modelParameter
        self.checkoutInformation = checkoutInformation
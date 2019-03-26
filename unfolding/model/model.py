import inspect

import numpy as np
from numpy import ndarray
from scipy.optimize import minimize
from ..interface.interface import IUnfolder, ICheckoutInformation
from unfolding.discretization.observedFunction import UniformUnfoldingResult
from ..discretization.observedFunction import UniformObservedFunction
from ..interface.ibasis import IBasis
from typing import Union, Callable
from .priorInforamtion import ParametricPrior
from ..tools.exeption import ModelParameterError





class _GaussErrorUnfolder:
    def __init__(self, kernel: ndarray, omega: ndarray, method: str = 'moda'):
        self._m, self._n = kernel.shape
        assert (self._n == omega.shape[0])
        self._K = kernel
        self._Kt = np.transpose(self._K)
        self._omega = omega
        self._rankOmega = np.linalg.matrix_rank(self._omega)
        self._method = method

    def _alpha_prob(self, alpha):
        """
        Calculate log of unnormalized probability of given alpha
        """
        BaO = self._B + alpha * self._omega
        iB = np.linalg.inv(BaO)
        dotp = np.dot(self._b, np.dot(iB, self._b))
        _, det = np.linalg.slogdet(BaO)
        return np.log(alpha) * (self._rankOmega / 2.) - det / 2. + dotp / 2.

    def _process(self, data: ndarray, dataError: ndarray, alpha: float = None):
        assert data.shape[0] == self._m
        assert dataError.shape[0] == self._m
        dataErrorInv = np.linalg.inv(dataError)
        self._B = self._Kt.dot(dataErrorInv.dot(self._K))
        self._b = np.dot(self._Kt, np.dot(dataErrorInv, data))
        if self._method == 'moda':
            if alpha is None:
                r = minimize(lambda a: -self.alpha_prob(np.exp(a)), -1, method='Nelder-Mead')
                alpha = np.exp(r.x[0])
            self._modelParameter['smoothness']['parameter'] = self.alpha
            BaO = self._B + alpha * self._omega
            iBaO = np.linalg.inv(BaO)
            phiCoef = np.dot(iBaO, self._b)
        return phiCoef, BaO

class GaussErrorUnfolder(IUnfolder, _GaussErrorUnfolder):
    METHODS = ['moda']

    def __init__(self, kernel: Union[ndarray, Callable], basis: IBasis = None, smoothness: Union[bool, ndarray, ParametricPrior] = True, parametricPrior: ParametricPrior = None, method: str = 'moda', y: ndarray = None):
        _GaussErrorUnfolder.__init__()
        # порядок опроса параматеров Ядро,  Гладкость

        frame = inspect.currentframe()
        argsDict = inspect.getargvalues(frame)

        self._modelParameter = {'arguments' : {'init': argsDict}, kernel: {}, }
        if isinstance(kernel, Callable):
            self._modelParameter['kernel']['function'] = kernel

            if y is not None and isinstance(y, ndarray):
                if basis is not None:
                    self._modelParameter['kernel']['y'] = y
                    kernel = basis.discretizeKernel(kernel, y)
                else:
                    raise ModelParameterError
            else:
                raise ModelParameterError
        self._modelParameter['kernel']['matrix'] = kernel
        if isinstance(smoothness, bool):
            if smoothness:
                if basis is not None:
                    smoothness = basis.getOmega()
                else:
                    raise ModelParameterError
            self._modelParameter['smoothness'] = {'matrix': smoothness}
        if not (method in self.METHODS):
            raise ModelParameterError
        self._modelParameter['methods'] = method
        _GaussErrorUnfolder.__init__(self, kernel, smoothness, method)
        self._basis = basis
        if basis is not None:
            self._modelParameter['basis'] = basis

    def process(self, data: ndarray, dataError: ndarray, alpha: float = None, checkInfo: ICheckoutInformation = None) -> UniformUnfoldingResult:
        if isinstance(data, list):
            data = np.array(data)
        if isinstance(dataError, list):
            dataError = np.array(dataError)
        self._modelParameter['arguments']['process'] = {'data': data, 'dataError': dataError}

        self.result = UniformUnfoldingResult()
        phiCoef, iBaO = self._process(data, dataError, alpha)


        self.result.observedSignal = UniformObservedFunction(phiCoef, basis=self._basis, covariance=iBaO)
        self.result.checkoutInformation = checkInfo
        self.result.modelParameter = self._modelParameter
        return self.result

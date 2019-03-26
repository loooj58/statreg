from abc import ABCMeta, abstractmethod

from numpy.core.multiarray import ndarray

from unfolding.interface.iObservedSignal import IObservedSignal
from unfolding.interface.ibasis import IBasis


class IObservedFunction(IObservedSignal, metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, x: ndarray)->ndarray:
        pass


class IUniformObservedFunction(IObservedFunction,metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, coef: ndarray, covariance: ndarray = None, basis: IBasis = None):
        pass
    @abstractmethod
    def error(self, x:ndarray)->ndarray:
        pass
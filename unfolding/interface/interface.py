from abc import ABCMeta
from abc import abstractmethod
from typing import Union, Callable
from numpy import ndarray

from unfolding.interface.iObservedSignal import IObservedSignal


# from ..discretization.observedFunction import UniformObservedFunction

class IModelParameter(metaclass=ABCMeta):
    pass

class ICheckoutInformation(metaclass=ABCMeta):
    pass


class CheckoutInformation(ICheckoutInformation):
    def __init__(self, trueObservedFunction: Union[Callable, IObservedSignal]):
        self.trueObservedFunction = trueObservedFunction

class IUnfoldingResult(metaclass=ABCMeta):
    def __init__(self, observedSignal: IObservedSignal, modelParameter: IModelParameter, checkoutInformation: ICheckoutInformation = None):
        self.observedSignal = observedSignal
        self.modelParameter = modelParameter
        self.checkoutInformation = checkoutInformation


class IUnfolder(metaclass=ABCMeta):
    @abstractmethod
    def process(self) -> IUnfoldingResult:
        pass


class IUnfoldingBuilder(metaclass=ABCMeta):
    __paremeters = {}

    @abstractmethod
    def build(self) -> IUnfolder:
        pass

    def set(self, **kwargs):
        for key in kwargs.keys():
            try:
                self.__paremeters[key] = kwargs[key]
            except KeyError:
                print("{} is not parameter of unfolder".format(key))
        return






class IPriorInformation(metaclass=ABCMeta):
    # abstract class for prior information
    pass


class Factory:
    def __init__(self, kernel: Union[Callable, ndarray], priorInformationList):
        #kernel is apparatus function or its matrix form
        #priorInformationListpriorInformationList
        pass
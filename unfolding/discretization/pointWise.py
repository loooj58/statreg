from unfolding.interface.ibasis import IBasis
from typing import Callable, Tuple
from numpy import ndarray

from ..interface.iObservedFunction import IUniformObservedFunction
import numpy as np

class PointWiseBasis(IBasis):
    """

    Класс для наивного представления функции как набора значений

    """
    def __init__(self, n: int, boundary: Tuple[float, float], endpoint:bool = True):
        a, b = boundary
        self.points, self.step = np.linspace(a,b,n, endpoint=endpoint, retstep=True)
        self.n = n
        #Следующий кусок решает проблему циклических зависимостей
        from .observedFunction import UniformObservedFunction
        self._uof = UniformObservedFunction


    def discretize(self, phi: Callable[[ndarray], ndarray])->IUniformObservedFunction:
        coef = phi(self.points)
        return self._uof(coef, basis=self)

    def calc_omega(self):
        omega = np.zeros((self.n, self.n))
        omega[0,0] = omega[-1,-1] = 1
        tempCenter = -2/self.step**2
        tempEdge = 1/self.step**2
        for i in range(1, self.n - 1):
            omega[i,i-1] = omega[i,i+1] = tempEdge
            omega[i,i] = tempCenter
        return omega




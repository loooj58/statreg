import numpy as np
from scipy.integrate import quad
from abc import ABCMeta, abstractmethod
from typing import Callable
from numpy import ndarray
from unfolding.interface.iObservedSignal import IObservedSignal


class IBasis(metaclass=ABCMeta):
    """
    Parent class for basis in functional space
    Basis of functions for true observable distribution.

    Should implement
    ----------------
    a : float
        left boundary of range
    b : float
        right boundary of range
    bf : [float -> float]
        list of basis functions

    calc_omega(self) :
        function to calculate matrix for integral of second
        derivatives
    """
    omega_cached = None

    @abstractmethod
    def discretize(self, phi: Callable[[ndarray],ndarray]) -> IObservedSignal:
        pass

    @abstractmethod
    def calc_omega(self) -> ndarray:
        pass

    def __call__(self, coef, x):
        """
        Evaluate function at the point

        Parameters
        ----------
        coef : vector of float
            coefficients
        x    : float
            point to evaluate function
        """
        res = 0
        for i in range(len(self.bf)):
            res += coef[i] * self.bf[i](x)
        return res

    def __len__(self) :
        "dimension of basis"
        return len(self.bf)

    def support(self) :
        "Return support of function"
        return (self.a, self.b)

    def basisFun(self, i):
        "Returns i-th basis function"
        return self.bf[i]

    def getOmega(self):
        """
        Returns matrix for calculation of integral

        .. math:: \int dx\, \phi(x)''^2

        Matrix is cached so its only calculated once
        """
        if self.omega_cached is None:
            self.omega_cached = self.calc_omega()
        return self.omega_cached

    def discretizeKernel(self, K, y) :
        """
        Discretize convolution kernel:

        -- math: f(x) = \int K(y,x) \phi(x) dx

        Parameters
        ----------
        K : 2-arg function
            2-parameter convolution kernel
        y : 1darray
            points for observed data

        Returns
        -------
        Km : matrix
        """
        a   = self.a
        b   = self.b
        Kmn = np.zeros((y.shape[0], len(self)))
        for m, ym in enumerate(y):
            for n, f in enumerate(self.bf):
                Kmn[m][n] = quad(lambda x: K(x,ym) * f(x), a, b, limit=100)[0]
        return Kmn

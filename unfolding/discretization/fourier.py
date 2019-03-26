from unfolding.interface.ibasis import IBasis
import numpy as np
from math import pi
from scipy.integrate import quad
from unfolding.discretization.observedFunction import UniformObservedFunction


class FourierBasis(IBasis):
    """
    FourierBasis(a ,b, n)
    Basis of Fourier series
    Parameters
    ----------
    a : float
        Left boundary of interval of domain function
    b : float
        Right boundary of interval of domain function
    n : int
        Fourier order: (сos nx, sin nx)
    Returns
    -------
    FourierBasis : callable
        Basis in functional space for phi vector.
    """

    def __init__(self, a, b, n):
        self.a = a
        self.b = b
        self.n = n
        self.l = (b - a) / 2.
        self.bf = self.basisfunc()

    def basisfunc(self):
        a = self.a
        b = self.b
        l = self.l
        mid = (a + b) / 2.
        func = [np.vectorize(lambda x: 0.5)]

        def fcos(n):
            return lambda x: np.cos(n * pi * (x - mid) / l)

        def fsin(n):
            return lambda x: np.sin(n * pi * (x - mid) / l)

        for i in range(1, self.n + 1):
            func.append(fcos(i))
            func.append(fsin(i))
        return func

    def discretize(self, phi):
        coef = np.zeros(len(self.bf))
        a = self.a
        b = self.b
        l = self.l
        for indx, f in enumerate(self.bf):
            # TODO: delete
            # if indx == 0:
            #     coef[indx] = quad(phi, a, b)[0] / l
            # else:
            coef[indx] = quad(lambda x: (f(x) * phi(x)), a, b)[0] / l
        return UniformObservedFunction(coef, self.bf, phi)

    def calc_omega(self, n=None):
        if n is None:
            n = 2
        temp = np.zeros(2 * self.n + 1)
        for i in range(1, self.n + 1):
            temp[2 * i - 1] = ((i * np.pi / self.l) ** (2 * n)) * self.l
            temp[2 * i] = temp[2 * i - 1]
        return np.diag(temp)

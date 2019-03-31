#!/usr/bin/python
"""
Transmission functions
"""
import numpy as np
from scipy.special import erf, erfc

def transmissionLinear(prec) :
    "Piecewise linear approximation of transition function"
    def fun(e, V):
        "V is endpoint of transition function"
        dV = V * prec
        if e < V:
            return 0
        elif e > V + dV:
            return 1
        else:
            return (e - V) / dV
    return fun

def tranmissionConvolved(prec, sigma) :
    """
    Convolution of piecewise linear approximation of transition
    function with jitter of electron gun. See notebook
    sympy-transmision-func.ipynb for derivation
    """
    def fun(E, V):
        delta  = V * prec
        e      = E - V
        #
        denom  = np.sqrt(2) * sigma
        denom2 = 2 * sigma**2
        return ( erfc((delta-e) / denom) / 2
               + e / (2*delta) * (erf(e/denom) + erf((delta-e)/denom))
               + ( sigma/(np.sqrt(2*np.pi)*delta)
                 * (np.exp( -e**2 / denom2) - np.exp( -(e-delta)**2 / denom2 ))
                 )
               )
    return fun

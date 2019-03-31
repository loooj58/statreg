#!/usr/bin/python
"""
"""
from dataclasses import dataclass
from typing      import Optional
import pandas as pd
import numpy           as np
import unfolding       as lib
import unfolding.basis as libB

from .datasets            import Dataset
from .numass.transmission import transmissionLinear, tranmissionConvolved


## ----------------------------------------------------------------

@dataclass
class Dataset:
    dataset   : str
    dv_prec   : float
    el_gun_E  : float
    gun_sigma : Optional[float]

def read_spectrum(meta : Dataset) :
    "Read measured spectrum"
    with open(meta.dataset) as f :
        ls = [ l for l in f.readlines()
               if l.strip() != '' and l[0] != '#'
             ]
        ls = [ l.split() for l in ls ]
        ls = [ (float(l[0]), float(l[-2]), float(l[-1])) for l in ls ]
        return pd.DataFrame.from_records( ls, columns=['vs', 'cnt', 'err'])

    
## ----------------------------------------------------------------

@dataclass
class BasisSpec:
    dirichletA : bool = True # f(a) = 0
    dirichletB : bool = True # f(b) = 0
    oversample : int  = 1  # How much oversample

def make_basis(meta : BasisSpec, data):
    "Create basis for subsequent unfolding"
    assert(meta.dirichletA)
    assert(meta.dirichletB)
    assert(type(meta.oversample) is int)
    assert(meta.oversample > 0)
    #
    knots = data['vs'].values
    if meta.oversample > 1 :
        knots = np.sort(np.concatenate(
            [knots] +
             [ np.linspace(knots[i], knots[i+1], meta.oversample, endpoint=False)[1:]
               for i in range(len(knots) - 1)]))
    return lib.CubicSplines(knots, "dirichlet")


## ----------------------------------------------------------------

@dataclass
class UnfoldingSpec:
    dataset:      Dataset
    transmission: str

def make_unfolding(meta: UnfoldingSpec, basis, dat):
    if meta.transmission == "linear":
        prec = meta.dataset.dv_prec        
        fun  = transmissionLinear(prec)
    else:
        raise Exception("Unknown transmission function: " ++ meta.transmission)
    dat = lib.Dataset(xs = dat['vs'].values,
                      ys = dat['cnt'].values,
                      sig= dat['err'].values,)
    # We need monkeypatch function out from unfolding object
    unf = lib.Unfolding( fun, basis, dat, [lib.omega(2)], )
    delattr(unf, 'Kfun')
    return unf

## ----------------------------------------------------------------

def calc_alpha(unf):
    return unf.optimal_alpha()

def calc_deconvolve(unf, alpha):
    res,sigR  = unf.deconvolve(alpha)
    return lib.PhiVec(res, unf.basis, sigR)

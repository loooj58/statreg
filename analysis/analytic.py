#!/usr/bin/python
"""
"""
from dataclasses import dataclass
from typing      import Optional,List,Union
import pandas as pd
import numpy          as np
from   numpy          import exp,log,expm1,sqrt
from   scipy.optimize import ridder,newton
import unfolding      as lib

from .numass.transmission import transmissionLinear, transmissionConvolved


class Analytic:
    def __init__(self, ctx):
        self.ctx    = ctx
        #
        self.dat    = ctx.call( read_spectrum,
                                meta_cheap=True, meta_path='dataset')
        self.basis  = ctx.call( make_basis, self.dat,
                                meta_cheap=True, meta_path='basis')
        self.unfold = ctx.call( make_unfolding, self.basis, self.dat)
        self.alpha  = ctx.call0( calc_alpha, self.unfold)
        self.phi    = ctx.call0( calc_deconvolve, self.unfold, self.alpha)
        self.aPost  = ctx.call0( AlphaPosterior,  self.unfold, self.alpha)

## ----------------------------------------------------------------

@dataclass
class Dataset:
    """
    Information about dataset
    """
    dataset   : str
    dv_prec   : float
    el_gun_E  : float
    gun_sigma : Optional[float]
    drop_init : Optional[int] = None
    drop_last : Optional[int] = None


def read_spectrum(meta : Dataset) -> lib.Dataset:
    "Read measured spectrum"
    with open(meta.dataset) as f :
        ls = [ l for l in f.readlines()
               if l.strip() != '' and l[0] != '#'
             ]
        ls = [ l.split() for l in ls ]
        ls = [ (float(l[0]), float(l[-2]), float(l[-1])) for l in ls ]
        df = pd.DataFrame.from_records( ls, columns=['vs', 'cnt', 'err'])
        # Drop parts of data
        off1 = meta.drop_init
        off2 = None if meta.drop_last is None else -meta.drop_last
        # Normalize counts since  our kernel imply that we continue
        df = df[off1:off2]
        df['cnt'] -= df['cnt'].values[-1]
        return df


## ----------------------------------------------------------------

@dataclass
class BasisSpec:
    """
    Specification of basis which is derived from dataset
    """
    dirichletA : bool = True # f(a) = 0
    dirichletB : bool = True # f(b) = 0
    oversample : int  = 1    # How much oversample

def make_basis(meta : BasisSpec, data: lib.Dataset) -> lib.Basis:
    "Create basis for subsequent unfolding"
    assert(type(meta.oversample) is int)
    assert(meta.oversample > 0)
    #
    knots = data['vs'].values
    if meta.oversample > 1 :
        knots = np.sort(np.concatenate(
            [knots] +
             [ np.linspace(knots[i], knots[i+1], meta.oversample, endpoint=False)[1:]
               for i in range(len(knots) - 1)]))
    bndA = "dirichlet" if meta.dirichletA else None
    bndB = "dirichlet" if meta.dirichletB else None
    return lib.CubicSplines(knots, (bndA,bndB))


## ----------------------------------------------------------------


@dataclass
class OmegaIntSpec:
    "Specififcation of regularization matrix"
    deg:      Optional[int]
    equalize: Optional[bool]

@dataclass
class OmegaBndSpec:
    "Boundary regularization"
    pass


@dataclass
class UnfoldingSpec:
    """
    Specifiction of uunfolding
    """
    dataset:      Dataset         # Dataset being used
    transmission: str             # transmission function
    # Regulariztion matrices
    omega:        List[Union[OmegaIntSpec,OmegaBndSpec]]

def make_unfolding(meta: UnfoldingSpec, basis: lib.Basis, dat: lib.Dataset) -> lib.Unfolding:
    """
    Generate unfolding object
    """
    if meta.transmission == "linear":
        prec = meta.dataset.dv_prec
        fun  = transmissionLinear(prec)
    elif meta.transmission == "folded":
        prec = meta.dataset.dv_prec
        gunS = meta.dataset.gun_sigma
        fun  = transmissionConvolved(prec, gunS)
    else:
        raise Exception("Unknown transmission function: " ++ meta.transmission)
    dat = lib.Dataset(xs = dat['vs'].values,
                      ys = dat['cnt'].values,
                      sig= dat['err'].values,)
    # We need monkeypatch function out from unfolding object
    def to_omega(o):
        if isinstance(o, OmegaIntSpec):
            return lib.omega(o.deg, equalize=o.equalize)
        if isinstance(o, OmegaBndSpec):
            return lib.boundaryAB()
        raise Exception("Cannot calculate omega")
    omegas = [ to_omega(o) for o in meta.omega ]
    unf = lib.Unfolding( fun, basis, dat, omegas, )
    delattr(unf, 'Kfun')
    return unf

## ----------------------------------------------------------------

def calc_alpha(unf: lib.Unfolding) -> lib.PhiVec:
    "Calculate optimal alpha for unfolding"
    return unf.optimal_alpha()

def calc_deconvolve(unf: lib.Unfolding, alpha: float):
    "Perform unfolding"
    res,sigR  = unf.deconvolve(alpha)
    return lib.PhiVec(res, unf.basis, sigR)

## ----------------------------------------------------------------

class Lognorm():
    """
    Sort-of lognormal distirbution
    """
    def __init__(self, mu, sig):
        self.mu  = mu
        self.sig = sig
        self.modeP = self.logpdf(self.mode())

    def logpdf(self, xs, normed=False):
        mu   = self.mu
        sig  = self.sig
        logP = - (np.log(xs) - mu)**2/(2*sig**2) - np.log(xs)
        if normed:
            logP -= self.modeP
        return logP

    def mode(self):
        return exp(self.mu - self.sig**2)


class AlphaPosterior:
    """
    Information about posterior of alpha
    """
    def __init__(self, unfold: lib.Unfolding, alpha):
        assert len(unfold.omegas) == 1
        assert alpha is None or len(alpha) == 1
        # ----
        self.aMax   = alpha[0]
        self.unfold = unfold
        aMax = alpha[0]
        pMax = unfold.alpha_prob(alpha)
        # Calculate credible intervals for α
        self.ci1Sigma = (
            ridder(lambda x : unfold.alpha_prob([x]) - pMax + 0.5, aMax/10, aMax),
            ridder(lambda x : unfold.alpha_prob([x]) - pMax + 0.5, aMax, aMax*10),
        )
        self.ci2Sigma = (
            ridder(lambda x : unfold.alpha_prob([x]) - pMax + 2, aMax/10, aMax),
            ridder(lambda x : unfold.alpha_prob([x]) - pMax + 2, aMax, aMax*10),
        )

    def lognormal(self, scale=1):
        """
        Calculate lognormal approximation
        """
        def lognorm_sig(s):
            return expm1(s**2) * np.exp(2*log(self.aMax) + 3 * s**2)
        (a1,a2) = self.ci1Sigma
        s0    = scale * (a2 - a1) / 2
        sigma = newton( lambda s: lognorm_sig(s) - (2*s0)**2, 1)
        mu    = np.log(self.aMax) + sigma**2
        return Lognorm(mu, sigma)

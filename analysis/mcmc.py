#!/usr/bin/python
"""
"""
from   dataclasses import dataclass
from   typing      import Optional,List,Union
import pandas as pd
import pymc3 as pm
import numpy          as np
from   numpy          import exp,log,expm1,sqrt
from   scipy.optimize import ridder,newton
import unfolding      as lib


from .analytic import Analytic

class MCMC:
    def __init__(self, ctx):
        self.aa    = Analytic(ctx)
        self.model = ctx.call( make_model,
                               self.aa.dat,
                               self.aa.basis,
                               self.aa.unfold,
                               self.aa.aPost,
                               meta_cheap=True,
                               meta_path="mcmc")
        self.trace = ctx.call( calc_trace,
                               self.model,
                               meta_path="mcmc",)       
        self.MAP   = ctx.call( calc_MAP,
                               self.model,
                               meta_path="mcmc",)

        
## ----------------------------------------------------------------

@dataclass
class AlphaLognormal:
    scale : float = 1

@dataclass
class ModelSpec:
    alphaPrior : Union[float, AlphaLognormal, type(None)]
    phiPrior   : str

def make_model(spec: ModelSpec, dat, basis, unfold, aPosterior):
    with pm.Model() as model:
        # Prior for alpha
        if isinstance( spec.alphaPrior, float):
            alpha = spec.alphaPrior
        elif isinstance( spec.alphaPrior, AlphaLognormal):
            alphaLN = aPosterior.lognormal(scale=spec.alphaPrior.scale)
            alpha   = pm.Lognormal('alpha', mu=alphaLN.mu, sd=alphaLN.sig)
        elif spec.alphaPrior is None:
            alpha   = pm.HalfFlat('alpha')
        else:
            raise Exception("Unknown prior for alpha")
        # Prior for phi
        nPhi  = len(basis)
        om    = unfold.omegas[0].mat
        chol  = np.linalg.cholesky(np.linalg.inv(om))        
        low   = np.repeat(0, nPhi)
        if spec.phiPrior == "positive":
            phiDistr = pm.Bound(pm.MvNormal, lower=low)
        elif spec.phiPrior == "any":
            phiDistr = pm.MvNormal
        phi   = phiDistr('phi',
                      mu    = np.zeros(nPhi),
                      chol  = chol/np.sqrt(alpha),
                      shape = nPhi)
        # Experimental data
        f     = pm.Normal('f', 
                      mu       = pm.math.dot(unfold.K, phi),
                      sd       = dat['err'].values, 
                      shape    = len(dat),
                      observed = dat['cnt'].values,
                     )
    return model
    

## ----------------------------------------------------------------

@dataclass
class MCMCSpec:
    SEED:   int
    draws:  int
    nCores: int

def calc_trace(mcmc: MCMCSpec, model):
    np.random.seed(mcmc.SEED)
    with model:
        trace = pm.sample(draws=mcmc.draws,
                          cores=mcmc.nCores
                          )
        return trace

def calc_MAP(mcmc: MCMCSpec, model):
    with model:
        return pm.find_MAP()

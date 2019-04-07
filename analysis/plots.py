#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""

import numpy             as np
from   scipy.optimize import ridder
import matplotlib.pyplot as plt
import matplotlib

def plot_measurements(unf, phi=None, coef=None, xlim=None) :
    """
    Plot data and convolution of restored function side by side.

    Optional parameters:
      - phi:  reconstructed vector
      - coef: coefficients for restored vector
    """
    if phi is not None:
        cs = phi.coef
    elif coef is not None:
        cs = coef
    else:
        raise Exception("plot_measurements: no reconstruction")
    folded = unf.K.dot(cs)
    # ----------------
    fig  = plt.figure()
    # Plot Data-model
    fig.add_axes((0.1, 0.3, 0.8, 0.6))
    plt.title('Measurements & convolution of restored func.')
    plt.grid()
    #
    plt.errorbar(unf.data.xs, unf.data.ys, yerr=unf.data.sig)
    plt.plot(unf.data.xs, folded, 'r.')
    # Residual plot
    fig.add_axes((0.1, 0.1, 0.8, 0.15))
    plt.fill_between(unf.data.xs, -unf.data.sig, unf.data.sig, color='b', alpha=0.5)
    plt.plot(unf.data.xs, unf.data.ys-folded, 'r')
    plt.grid()
    #
    if xlim is not None:
        fig.axes[0].set_xlim(xlim)
        fig.axes[1].set_xlim(xlim)
    return fig


def plot_deconvolved(unf, phi, meta, title=None, xlim=None, ylim=None) :
    """
    Plot deconvolved function and pointwise errors
    """
    gunE = meta['dataset']['el_gun_E']
    vs = np.linspace(unf.data.xs[0], unf.data.xs[-1], 2000)
    ys = phi(vs)
    dy = np.asarray([phi.error(v) for v in vs])
    #
    fig = plt.figure()
    plt.title('Deconvolution result' if title is None else title)
    if xlim is not None:
        fig.axes[0].set_xlim(xlim)
        if ylim is None:
            x1,x2 = xlim
            idx   = ((gunE - vs) >= x1) & ((gunE - vs) <= x2)
            y1    = np.min((ys - dy)[idx])
            y2    = np.max((ys + dy)[idx])
            delta = (y2 - y1) * 0.05
            ylim  = (y1 - delta, y2 + delta)
    if ylim is not None:
        fig.axes[0].set_ylim(ylim)
    #
    plt.plot(gunE - vs, ys, 'r')
    plt.plot(gunE - unf.data.xs, phi(unf.data.xs), 'g.')
    plt.fill_between(gunE - vs, ys-dy, ys+dy, color='b', alpha=0.5)
    plt.grid()
    return fig

def plot_correlations_matrix(sig) :
    """
    Plot correlation matrix given covariance matrix
    """
    corr = np.matrix(sig)
    n,_  = np.shape(corr)
    for i in range(n):
        for j in range(n):
            corr[i,j] = corr[i,j] / np.sqrt(sig[i,i] * sig[j,j])
    plt.matshow(corr, vmin=-1, vmax=1, cmap=matplotlib.cm.RdYlBu)
    plt.title(u'Correlation matrix for φ', y=1.08)
    plt.colorbar()

def plot_KWK_eigenvalues(r) :
    fig = plt.figure()
    KWK = r.res.conv.B
    evals  = np.linalg.eigvals(KWK)
    evals  = np.flip(np.sort(np.abs(evals)),0)
    evalsR = np.linalg.eigvals(KWK + r.res.alpha * r.res.conv.omega())
    evalsR = np.flip(np.sort(np.abs(evalsR)),0)
    plt.plot(evals)
    plt.plot(evalsR)
    plt.grid()
    plt.semilogy()
    C   = evals[0]/evals[-1]
    C_R = evalsR[0]/evalsR[-1]
    plt.title("cond. number = %.2e / %.2e [%.1e]" % (C, C_R, C/C_R))
    return fig

def plot_Omega_eigenvalues(r) :
    plt.figure()
    evals  = np.linalg.eigvals(r.res.conv.omega())
    evals  = np.flip(np.sort(evals),0)
    plt.plot(evals)
    plt.grid()
    plt.semilogy()
    C   = evals[0]/evals[-1]
    plt.title("cond. number = %.2e" % (C,))

def plot_alpha(unfold, alpha=None):
    """
    Likelihood plot for α
    """
    assert len(unfold.omegas) == 1
    assert alpha is None or len(alpha) == 1
    #
    if alpha is None:
        aMax = r.conv.optimal_alpha()[0]
    else:
        aMax = alpha[0]
    pMax = unfold.alpha_prob([aMax])

    a1_1 = ridder(lambda x : unfold.alpha_prob([x]) - pMax + 0.5, aMax/10, aMax)
    a2_1 = ridder(lambda x : unfold.alpha_prob([x]) - pMax + 0.5, aMax, aMax*10)
    a1_2 = ridder(lambda x : unfold.alpha_prob([x]) - pMax + 2, aMax/10, aMax)
    a2_2 = ridder(lambda x : unfold.alpha_prob([x]) - pMax + 2, aMax, aMax*10)
    aa   = np.linspace(a1_2, a2_2)
    plt.figure()
    plt.plot(aa, [unfold.alpha_prob([a1]) - pMax for a1 in aa])
    plt.grid()
    plt.axvline(aMax, c='red')
    plt.axvline(a1_1, c='b')
    plt.axvline(a2_1, c='b')
    plt.title(u"α = %.3e - %.2e + %.2e" % (aMax,aMax-a1_1,a2_1-aMax))

#!/usr/bin/python
"""
"""

from repropy import Meta


dataset_2011 = Meta(
    dataset   = 'data/G18_loss.out',
    dv_prec   = 1.9e-05,
    el_gun_E  = 18700,
    gun_sigma = 0.27179
)
dataset_2014H2 = Meta(
    dataset  = 'data/h2_19_1_loss.out',
    dv_prec  = 8.3e-05,
    el_gun_E = 19005.5,
)
dataset_2014D2 = Meta(
    dataset  = 'data/d2_19_1_loss.out',
    dv_prec  = 8.3e-05,
    el_gun_E = 19005.5,
)

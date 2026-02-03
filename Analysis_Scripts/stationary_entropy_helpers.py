# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 15:57:45 2026

@author: ksteinfe

Helper functions to compute and normalize stationary entropy calculations
"""

import numpy as np

def shannon_entropy_bits(p):
    p = p[p > 0]  # avoid lodf2(0)
    return -np.sum(p * np.log2(p))

def normalized_entropy(p, n_states):
    H = shannon_entropy_bits(p)
    if np.isnan(H):
        return np.nan
    Hmax = np.log2(n_states)  # here n_states=4 faces
    return H / Hmax if Hmax > 0 else np.nan

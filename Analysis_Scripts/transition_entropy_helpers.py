# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 16:14:02 2026

@author: ksteinfe

Helpers to compute 
- transition entropy (GTE)
- modified transition entropy (mGTE)
- directional transition counts

"""
import pandas as pd
import numpy as np

def _transition_matrix_AOIs(seq, levels, targ=None, count_targ=0):
    '''
    

    Parameters
    ----------
    seq : TYPE
        DESCRIPTION.
    levels : TYPE
        DESCRIPTION.
    targ : TYPE, optional
        DESCRIPTION. The default is None.
    count_targ : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    # create a 4x4 0-filled df
    counts = pd.DataFrame(0, index=levels, columns=levels, dtype=int)
    
    # if count_targ (T-D and D-T) then there must be a target
    if count_targ==1 and targ==None:
        return print('missing a target')
    
    # if not counting the target, but provided a target, then counting D-D only
    if count_targ==0 and targ:
        count_dist=1
    else:
        count_dist=0
        
    for a, b in zip(seq[:-1], seq[1:]):
        if a == '-' or b == '-':       # ignore gap-adjacent pairs
            continue
        if a==b: # remove self transitions
            continue
        if (count_dist==1) and (a == targ or b == targ): # if count_dist, don't count targ adjacent
            continue
        if count_targ==1 and not ((a == targ) or (b == targ)): # if count_targ, only count targ adjacent
            continue
        if a in counts.index and b in counts.columns:
            counts.loc[a, b] += 1
    return counts

def GTE(counts, time_per_state, time_weight=1, TD=0, targ=""):
     """
      Entropy rate H = sum_i pi_i * H(P_i·), weighting rows by *time* in state i.
      modes:
        counts = df with the relevant transition counts, filled with 0 for T-D if D-D and vice-versa
        time_per_state = series with total fixation time on each face, always 4 faces 
        time_weight = 1 for classic GTE, time_weight = 0 for simple average
        TD=0 for D-D transitions and 1 for T->D transitions, only in effect if time_weight = 0
        targ= one of ['LeftTopFace', 'RightTopFace', 'RightBottomFace', 'LeftBottomFace'], only in effect if time_weight = 0
     """
     # 1) we always keep all states in the matrix 
     kept_states = list(counts.index)                          

     # 2) map labels -> row/col indices, and align time vector
     idx_map = {s: i for i, s in enumerate(kept_states)}

     k = len(kept_states)

     # 3) realign dwell-time series with idx_map
     if isinstance(time_per_state, pd.Series):
        time_per_state = time_per_state.reindex(idx_map.keys()).fillna(0.0)
        tvec = time_per_state.to_numpy(dtype=float)

        total_time = float(tvec.sum())
        if total_time <= 0:
          return np.nan

     # 3) fill the Cij matrix with previously calculated transition counts
     # C = np.zeros((k, k), dtype=float)
     # for i,a in enumerate(kept_states):
     #     for j,b in enumerate(kept_states):
     #         C[i,j]=counts.loc[a,b]
             
     C = counts.to_numpy(dtype=float)
     
     # 4) row-normalize Ci to Pi
     with np.errstate(invalid='ignore', divide='ignore'):
         row_sums = C.sum(axis=1, keepdims=True)
         P = np.divide(C, row_sums, out=np.zeros_like(C), where=row_sums > 0)

     # 5) per-row entropies
     row_H = np.zeros(k, dtype=float)
     for i in range(k):
         # if that whole row has 0 probabilities (origin is 0)
         if row_sums[i, 0] == 0:
           # then it contributes 0 entropy to the GTE sum
           # time-weighting will * 0 anyway 
           row_H[i] = 0.0
           continue
         p = P[i]
         with np.errstate(divide='ignore', invalid='ignore'):
             # if p is 0 then it should contribute 0 bits to the sum since 0*n = 0
            term = np.where(p > 0, p * np.log2(p), 0.0)
         row_H[i] = -np.sum(term) 

     # 6) time-weighted mixture (bits per unit time since pi_time sums to 1)
     # normalize time by sum of time in k states 
     pi_time = tvec  / total_time
  
     # safeguard if there is no time
     if np.isnan(pi_time).any():
        return np.nan
     
     if time_weight==1:
     # time-weighted average of Hi by row-time
         H_rate = float(np.dot(pi_time, row_H))   # time-weighted
         H_norm = H_rate/np.log2(k-1)
     if time_weight==0: # the variation with the TD parameter
     # no time_weighting
         if TD==1:
             s=1  #origin is 1 of 1 target
             no_time = np.full(s, 1.0 / s)
             j=4 # 1T and 3D
             Hrows = idx_map[targ]
         if TD==0:
             s=3  #origin is 1 of 1 target
             no_time = np.full(s, 1.0 / s)
             j=3 # 3D
             Hrows = [idx_map[dist] for dist in idx_map.keys() if dist!=targ]
         sub_row_H = row_H[Hrows]
         H_rate = float(np.dot(no_time, sub_row_H))
         H_norm = H_rate/np.log2(j-1)
     return H_norm


def directional_counts(seq, target, distractors):
    td = dt = 0
    for a,b in zip(seq[:-1], seq[1:]):
        if a == target and b in distractors: td += 1
        if a in distractors and b == target: dt += 1
    return td, dt

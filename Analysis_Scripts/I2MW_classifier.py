# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 17:41:33 2025

@author: ksteinfe

Python code to classify saccades based on 2 yoked moving windows 

Adapted from the Matlab Code available in https://zenodo.org/records/6958425

Original Code: Hooge, I.T.C., Niehorster, D.C., Nyström, M., 
                Andersson, R. & Hessels, R.S. (2022). Fixation classification: 
               how to merge and select fixation candidates. 
               Behavior Research Methods. 
               https://doi.org/10.3758/s13428-021-01723-1.

"""


import numpy as np
from typing import NamedTuple


class Episodes(NamedTuple):
    start: np.ndarray   # 0-based sample indices
    end:   np.ndarray   # inclusive


def bool2bounds(mask: np.ndarray) -> Episodes:
    """Convert a boolean vector to start/end index pairs (inclusive)."""
    diff = np.diff(np.concatenate([[False], mask, [False]]))
    #print(f'diff {diff}')
    starts = np.where(diff == 1)[0]
    ends   = np.where(diff == -1)[0] - 1
    #print(f'starts {starts}')
    #print(f'ends {ends}')
    return Episodes(starts, ends)


def i2mw(
    x_deg: np.ndarray,
    y_deg: np.ndarray,
    samp_freq: float = 30.0,           # Hz
    window_ms: float = 150,           # per Hooge: ~10–25 ms, must be odd #samples
    gap_samp: int   = 1,               # separation between the two windows
    amp_thr: float  = 2,            # deg
    allow_missing: bool = False
) -> Episodes:
    """
    Identification-by-Two-Moving-Windows (I2MW) saccade finder.

    Parameters
    ----------
    x_deg, y_deg : 1-D float arrays (NaNs allowed)
        Gaze positions in degrees of visual angle.
    samp_freq    : float
        Sampling rate in Hz (60Hz here).
    window_ms    : float
        Length of each moving window in ms.  Must be an odd
        number of samples; use e.g. 17 ms at 60 Hz → 1 sample per window.
    gap_samp     : int
        Samples separating the two windows (here 1).
    amp_thr      : float
        Threshold (deg) for the Euclidean distance between the two
        window medians.
    allow_missing: bool
        If False, episodes containing NaNs are discarded.

    Returns
    -------
    Episodes(start, end)  – sample indices of saccades.
    """
    x = np.asarray(x_deg, dtype=float)
    y = np.asarray(y_deg, dtype=float)
    
    assert x.shape == y.shape, "x and y must have same length"
    n_samp = x.size

    # translate window length from ms to number of samples 
    span = int(round(window_ms / 1000 * samp_freq))
    
    #print(f'span {span}')
    # make the span an odd number
    if span % 2 == 0:
        
        span += 1                            
    half_win = (span - 1) // 2
    #print(f'half win {half_win}')
    #print(f"I2MW: window = {span} samp ({window_ms:.1f} ms), "
          #f"gap = {gap_samp} samp, thr = {amp_thr}°")

    # pre-compute window offsets
    w1 = np.arange(half_win)                 # left window indices
    #print(f' w1 {w1}')
    sep = np.arange(half_win, half_win + gap_samp)
    w2 = sep + gap_samp                      # right window indices
    #print(f' w2 {w2}')
    last_pos = n_samp - (2 * half_win + gap_samp)
    
   
    if last_pos+w2[0] != len(x):
        #print(f'last pos is {last_pos} but data is {len(x)} - padding')
    
        new_samp = 2 * half_win + gap_samp + last_pos 
        #print(new_samp)
        new_n_samp = new_samp + 2*w2[0]
        #print(new_n_samp)
        diff_n_samp = new_n_samp-n_samp
        #seq = np.repeat(0, diff_n_samp)
        #print(seq)
        x_deg=list(x_deg)
        y_deg=list(y_deg) 
        
        #pad with last values 
        x_deg.extend(np.repeat(x_deg[n_samp-1], diff_n_samp))
        y_deg.extend(np.repeat(y_deg[n_samp-1], diff_n_samp))
       
        x = np.asarray(x_deg, dtype=float)
        y = np.asarray(y_deg, dtype=float)
        
        n_samp= x.size
        last_pos = n_samp - (2 * half_win + gap_samp)
        #print(f'last pos is {last_pos}, data is {len(x)} - done padding')
    sacc_mask = np.zeros(n_samp, dtype=bool)

    for p in range(last_pos):
        idx1 = p + w1
        #print(f'idx1 {idx1}')
        idx2 = p + w2
        #print(f'idx2 {idx2}')
        xw1, yw1 = x[idx1], y[idx1]
        xw2, yw2 = x[idx2], y[idx2]
        #print(f'xw1 {xw1}')

        med1 = np.nanmedian(np.column_stack([xw1, yw1]), axis=0)
        med2 = np.nanmedian(np.column_stack([xw2, yw2]), axis=0)
        #print(f'med1 {med1}')

        if np.hypot(med1[0] - med2[0], med1[1] - med2[1]) > amp_thr:
            sacc_mask[p + sep] = True       # centre sample(s)
            
    #print(f' sacc-mask {sacc_mask}')
    
    # turn boolean mask into start/end lists
    episodes = bool2bounds(sacc_mask.astype(int))
    
    #print(f'episodes {episodes}')
    
    # optionally drop episodes containing NaNs
    if not allow_missing and episodes.start.size:
        keep = []
        for s, e in zip(episodes.start, episodes.end):
            if not (np.isnan(x[s:e+1]).any() or np.isnan(y[s:e+1]).any()):
                keep.append((s, e))
        if keep:
            episodes = Episodes(
                start=np.array([k[0] for k in keep], dtype=int),
                end=np.array([k[1] for k in keep], dtype=int)
            )
        else:
            episodes = Episodes(start=np.array([], dtype=int),
                                end=np.array([], dtype=int))
            
    return episodes

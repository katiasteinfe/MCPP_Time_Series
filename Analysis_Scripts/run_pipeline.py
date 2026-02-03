# -*- coding: utf-8 -*-
"""

@author: ksteinfe
"""

import os
import pandas as pd

from environment_setup import output_dir, data_dir_children, data_dir_adults, raw_file_name_adults, raw_file_name_children

# Adults
from sanitize_adults import sanitize_adults
from compute_dwell_metrics_adults import compute_dwell_metrics_adults
from compute_transition_metrics_adults import compute_transition_metrics_adults

#Children
from sanitize_children import sanitize_children
from compute_dwell_metrics_children import compute_dwell_metrics_children
from compute_transition_metrics_children import compute_transition_metrics_children

from Classify import classify
from create_fix_df import create_fix_df


PIPELINE_CONFIG = {
    "adults": {
        "data_dir": data_dir_adults,
        "raw_pkl": raw_file_name_adults,
        "sanitize_fn": sanitize_adults,
        "dwell_fn": compute_dwell_metrics_adults,
        "transition_fn": compute_transition_metrics_adults,
        "prefix": "adults",
    },
    "children": {
        "data_dir": data_dir_children,
        "raw_pkl": raw_file_name_children,
        "sanitize_fn": sanitize_children,
        "dwell_fn": compute_dwell_metrics_children,
        "transition_fn": compute_transition_metrics_children,
        "prefix": "children",
    },
}


def run_pipeline(group: str, PIPELINE_CONFIG=PIPELINE_CONFIG, 
                 output_dir=output_dir):
    '''
    Runs the whole preprocessing pipeline for children and adults.
    Saves output of each preprocessing script to a 1_preprocessing subfolder
    Saves output for analysis in 2_analysis scripts
    All outputs are saved with _children or _adults suffixes
    Different scripts are run for children and adults from sanitize() onwards

    Parameters
    ----------
    group : str
        Must be "children" or "adults"
    output_dir : path, optional
        As defined in environment_setup.py. The default is output_dir.

    Raises
    ------
    ValueError
        If the group is not "children" or "adults".

    Returns
    -------
    dwell_metrics : df
        Contains PTLT and stationary entropy, 
        saved as dwell_metrics_{children or adults}.py
    transition_metrics : df
        Contains mGTE, GTE and transition rate
        saved as transition_metrics_{children or adults}.py

    '''
    if group not in PIPELINE_CONFIG:
        raise ValueError(f"Unknown group='{group}'. Use one of: {list(PIPELINE_CONFIG.keys())}")

    cfg = PIPELINE_CONFIG[group]
    
    group_out = os.path.join(output_dir, group)
    preprocess_dir = os.path.join(group_out, "1_preprocess")
    analysis_dir = os.path.join(group_out, "2_analysis")
    dwell_dir = os.path.join(analysis_dir, "dwell")
    transition_dir = os.path.join(analysis_dir, "transition")

    for d in (preprocess_dir, dwell_dir, transition_dir):
        os.makedirs(d, exist_ok=True)

    # -------------------------
    # 1) Preprocess
    # -------------------------
    data_dir = cfg["data_dir"]
    raw_path = os.path.join(data_dir, cfg["raw_pkl"])
    raw_df = pd.read_pickle(raw_path)

    classified_raw_df = classify(preprocess_dir, raw_df)
    fixations_df = create_fix_df(classified_raw_df, preprocess_dir)
    fixations_clean_df = cfg["sanitize_fn"](fixations_df, preprocess_dir)

    # -------------------------
    # 2) Analysis
    # -------------------------
    dwell_metrics = cfg["dwell_fn"](fixations_clean_df, dwell_dir)
    transition_metrics = cfg["transition_fn"](fixations_clean_df, transition_dir)


    return dwell_metrics, transition_metrics

#%% Example uses
# def run_pipeline_adults(**kwargs):
#     return run_pipeline("adults", **kwargs)


# def run_pipeline_children(**kwargs):
#     return run_pipeline("children", **kwargs)

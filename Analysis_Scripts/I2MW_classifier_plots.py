# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 19:44:59 2026

@author: ksteinfe
"""
import numpy as np
import os
import pandas as pd
from typing import NamedTuple
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
import sys
# helper to identify saccades
sys.path.append(os.path.dirname(os.path.abspath(r'C:\Users\ksteinfe\Desktop\MCPP Time Series\4_Preliminary_Analysis\MCPP_Time_Series_Code\0_Preprocessing_pipeline_fromraw')))

from I2MW_classifier import i2mw
#%%
data_dir= r"C:\Users\ksteinfe\Desktop\MCPP Time Series\1_Experimental_Data\3_Final Time Series Data_Adults\NSF Exp 1 Adult"
output_dir = r"C:\Users\ksteinfe\Desktop\MCPP Time Series\4_Preliminary_Analysis\MCPP_Time_Series_Code\0_Preprocessing_pipeline_fromraw\Preprocessing_results"

file_path = os.path.join(data_dir, "RawData_Clean_Exp1_Adults.pkl")
yesblinks_df = pd.read_pickle(os.path.join(output_dir,"Classified_YesBlink_Adults.pkl"))
#%%
       
noise_dfs=[]
  
# Euclidian noise computations
for trial_id in yesblinks_df["Trial"].dropna().unique():
    trial_noblinks = yesblinks_df[yesblinks_df["Trial"] == trial_id].copy()
    
    for p_id in trial_noblinks['Participant'].unique():
        ptrial = trial_noblinks[trial_noblinks.Participant == p_id].copy().reset_index()
        ptrial.fix_count = ptrial.fix_count.fillna(-1).astype(int)
        # Loop through these identified fixations to quantify noise
        th = np.pi/4
        
    
        flat_trace = [np.full(len(ptrial), np.nan), np.full(len(ptrial), np.nan)]
        nojitter_trace = [np.full(len(ptrial), np.nan), np.full(len(ptrial), np.nan)]
        raw_trace = [np.full(len(ptrial), np.nan), np.full(len(ptrial), np.nan)]
        
        
        blinks =  ptrial.loc[(ptrial['Pupil Size Right X [px]']=='-') & (ptrial['Point of Regard Right X [px]'].isna() ) & (ptrial['Point of Regard Right Y [px]'].isna())]['Point of Regard Right X [px]'].index  
        
        
        # Write back denoised/smoothed/raw data to yesblinks_df
        trial_mask = (yesblinks_df['Trial'] == trial_id) & (yesblinks_df['Participant'] == p_id)
       
        yesblinks_df.loc[trial_mask, 'rawtrace_x']  = raw_trace[0]
        yesblinks_df.loc[trial_mask, 'rawtrace_y']  = raw_trace[1]
        
        for i in range(0,ptrial.fix_count.unique().max()+1):
           
            # Indices for this fixation
            fix_idx = ptrial[ptrial.fix_count == i].index
            fix_vals = [ptrial.loc[fix_idx, 'Point of Regard Right X [px]'].astype(float).to_numpy(), ptrial.loc[fix_idx, 'Point of Regard Right Y [px]'].astype(float).to_numpy()]
            raw_trace[0][fix_idx]=fix_vals[0]
            raw_trace[1][fix_idx]=fix_vals[1]

        plot = True
        if plot:
            fig, ax = plt.subplots(2, 1, figsize=(8, 3), sharex=True)
            x_shared = np.arange(len(ptrial))
            
            # Raw gaze
            ax[0].plot(x_shared, ptrial['Point of Regard Right X [px]'], label="x", lw=1, color='blue')
            ax[0].plot(x_shared, ptrial['Point of Regard Right Y [px]'], label="y",  lw=1, color='black')
            ax[0].set_title("Raw Gaze Trace")
            ax[0].vlines(ptrial.loc[ptrial['fix'] == True].index, 0, 100, color='gray', alpha=0.5)
            ax[0].vlines(blinks,-100,0, color='purple')
            
            # Fixation segments
          
            ax[1].set_title("Fixation Segments")
            ax[1].plot(x_shared, raw_trace[0], lw=1, color='blue', alpha=0.3, zorder=0, label='x')
            ax[1].plot(x_shared, raw_trace[1], lw=1, color='black', alpha=0.3, zorder=0, label='y')
            
            
            ax[0].legend()
            ax[1].legend()
            
            plt.tight_layout()
            plt.show()

            fig.savefig(os.path.join(output_dir, 'I2MW_Classifier_Euclidian', f'FILT_I2MW_EU_{p_id}_{trial_id}.png'),dpi=300)
            plt.close() 
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 18:12:57 2025

@author: ksteinfe

Inputs: I2MW_classifier.py, RawData_Clean_Exp1_Adults 
        or RawData_Clean_Exp1_Children
    
1)   Discard segments without identified right eye pupil ​

2)   Mark saccades using I2MW​

3)   Discard segments marked as saccades​

4)   Mark remaining inter-saccade segments as fixations

Output in preprocessing_results folder:
    - raw blinks
    - raw saccades
    - raw fixation
"""
#%%
import numpy as np
import os
import pandas as pd
from I2MW_classifier import i2mw
import matplotlib.pyplot as plt
from screen_params import screen_res_x, screen_res_y, screen_w_cm_x, screen_w_cm_y, view_dist_cm

# Helper to get the fixation/sacc points that are adjacent in time (no merge)
def mask_cluster(data_deg):

    cluster_mask = []
    filtered_data = []
    new_clust = []
    new_data = []
    
    for i in range(len(data_deg) - 1):
        new_clust.append(data_deg.index[i])
        #print(new_clust)
        new_data.append(data_deg.loc[data_deg.index[i]])
        
        # If the next index is not consecutive, end the cluster
        if data_deg.index[i] + 1 != data_deg.index[i + 1]:
            cluster_mask.append(new_clust)
            filtered_data.append(new_data)
            
            new_clust = []
            new_data = []
    # Handle last point
    new_clust.append(data_deg.index[-1])
    new_data.append(data_deg.loc[data_deg.index[-1]])
    
    cluster_mask.append(new_clust)
    filtered_data.append(new_data)
  
    return cluster_mask, filtered_data


def classify(output_dir, raw_sheet, 
                      screen_w_cm_x = screen_w_cm_x , 
                      screen_w_cm_y = screen_w_cm_y , 
                      screen_res_x = screen_res_x , 
                      screen_res_y = screen_res_y , 
                      view_dist_cm = view_dist_cm , 
                      Fig_plot = False , 
                      Fig_save = False , 
                      samp_freq = 60 , 
                      window_ms = 150):
    '''
    

    Parameters
    ----------
    output_dir : path
        Where the df with identified fixations is saved as pkl and csv.
    raw_sheet : df
        Raw output from SMI of length duration of trials in sec * 1/sampling 
    screen_w_cm_x : np.float
        screen width in cm
    screen_w_cm_y : np.float
        screen length in cm
    screen_res_x : np.float
        horizontal screen resolution in px
    screen_res_y : np.float
        vertical screen resolution in px
    view_dist_cm : np.float
        viewing distance in cm
    Fig_plot : Boolean, optional
        Plot figures parameter. The default is False.
    Fig_save : Boolean, optional
        Save figures parameter. The default is false
    samp_freq : int, optional
        Eye tracker sampling freq in Hz. The default is 60.
    window_ms : int, optional
        Width of the window parameter for I2MW. The default is 150.

    Returns
    -------
    yesblinks_df : df 
        Input raw_sheet with additional columns to identify fixations such as:
            - sacc: Boolean
            - sacc_count: index of saccade
            - fix: Boolean
            - fix_count: index of fixation

    '''

    # Before starting make sure '-' are np.nan and relevant columns are float
    raw_sheet.replace('-', np.nan)
    
    raw_sheet['Point of Regard Right X [px]'] = raw_sheet['Point of Regard Right X [px]'].replace('-', np.nan)
    raw_sheet['Point of Regard Right X [px]'] = raw_sheet['Point of Regard Right X [px]'].astype(float)
    raw_sheet['Point of Regard Right Y [px]'] = raw_sheet['Point of Regard Right Y [px]'].replace('-', np.nan)
    raw_sheet['Point of Regard Right Y [px]'] = raw_sheet['Point of Regard Right Y [px]'].astype(float)
    
    # Convert screen measurements to deg
    px_pitch_cm_x   = screen_w_cm_x / screen_res_x     # cm per pixel
    px_pitch_cm_y   = screen_w_cm_y / screen_res_y     # cm per pixel
    px_to_deg_x     = (px_pitch_cm_x / view_dist_cm) * (180 / np.pi)
    px_to_deg_y    = (px_pitch_cm_y / view_dist_cm) * (180 / np.pi)

    
    # Container to collect results per participant
    cleaned_data = [] # reset idx of each trial after removing blinks
    rawclass_data = [] # no reset of idx after removing blinks
    
    # Detect rows where no pupil is recorded (blink-like)
    raw_blinks= raw_sheet.loc[(raw_sheet['Pupil Size Right X [px]']=='-') & (raw_sheet['Point of Regard Right X [px]']=='-' ) & (raw_sheet['Point of Regard Right Y [px]']=='-')]
    print(f"Blinks/Total: {len(raw_blinks)}/{len(raw_sheet)}")
    
    # Prep data and apply classifiers for comparison
    for trial_id in raw_sheet["Trial"].dropna().unique():
        trial_raw = raw_sheet[raw_sheet["Trial"] == trial_id].copy()

      
        for p_id in trial_raw['Participant'].unique():
            ptrial_raw = trial_raw[trial_raw.Participant == p_id].copy()
    
            # Remove blinks
            blink_idx = raw_blinks.index.intersection(ptrial_raw.index)
            
            ptrial_idx = ptrial_raw.copy().drop(index=blink_idx).index
            ptrial_noblinks = ptrial_raw.copy().drop(index=blink_idx).reset_index(drop=True)
    
            # Find episodes using i2mw
            # First row is sacc starts, second one is sacc ends
            eps = i2mw(
                ptrial_noblinks['Point of Regard Right X [px]']* px_to_deg_x,
                ptrial_noblinks['Point of Regard Right Y [px]']* px_to_deg_y,
                samp_freq=samp_freq,
                window_ms=window_ms,
                amp_thr=1,
                allow_missing=False
            )
            
            # Get the indexes of each saccade between start and end
            sacc_bool = pd.Series(False, index = ptrial_noblinks.index)
            for s, e in zip(eps.start, eps.end):
                sacc_bool.iloc[s:e+1] = True
            #print(f"{trial_id},{p_id},{len(sacc_bool)}, {len(ptrial_noblinks)}")
            
             
            # Add those saccades/fix indexes as a column 
            ptrial_noblinks['sacc']=sacc_bool
            
            fix_bool = ~sacc_bool
            ptrial_noblinks['sacc']=sacc_bool
            
            ptrial_noblinks['fix']=fix_bool
            
            if Fig_plot == True:
                
                stim = trial_raw['Stimulus'].iloc[0]
                condition = (
                    'VisAsync' if 'VisAsync' in stim or 'VisAync' in stim or 'ViisAsync' in stim
                    else 'AudSync' if 'AudSync' in stim
                    else 'Other'
                )
                color_trial = 'red' if condition == 'VisAsync' else 'black'

                fig, ax = plt.subplots(1,1,figsize=(8, 3))
                t=[x for x in ptrial_noblinks['Point of Regard Right X [px]'].index]
                ax.plot(t,ptrial_noblinks['Point of Regard Right X [px]'].astype(float),  label=f"Gaze {condition}", lw=1, color = color_trial)
                ax.vlines([x for x in fix_bool.index if fix_bool[x]==True],0,20,  color='darkblue', alpha=0.2, zorder=0)
                ax.vlines([x for x in sacc_bool.index if sacc_bool[x]==True],0,20,  color='darkgreen', alpha=0.2, zorder=0)
                ax.set_title(f"Fix in blue and Sacc in green by I2MW, {p_id}, {trial_id}")

                plt.ylim(0, ptrial_noblinks['Point of Regard Right X [px]'].astype(float).max()*1.2 ); plt.xlabel("time (s)"); #plt.legend(); plt.tight_layout()
                plt.show()
                if Fig_save == True:
                    fig.savefig(os.path.join(output_dir, f'I2MW_{p_id}_{trial_id}.png'),dpi=300)
                plt.close()
            
          
            # Get the fixation/sacc points that are adjacent in time (no merge rule here)
            if (len(ptrial_noblinks.loc[ptrial_noblinks['fix']==True])>0):
                cluster_fix, fixs = mask_cluster( ptrial_noblinks.loc[ptrial_noblinks['fix']==True])
                # Flattened fixation and saccade cluster labels
                len_fix = [i for i, cluster in enumerate(cluster_fix) for _ in range(len(cluster))]
                # Assign fix cluster labels or NaN based on boolean column
                fix_iter = iter(len_fix)
                ptrial_noblinks['fix_count']= [
                    next(fix_iter) if is_fix else np.nan
                    for is_fix in ptrial_noblinks['fix']
                ]
            else:
                (f"{trial_id},{p_id},no fixations")
                
            if len(ptrial_noblinks.loc[ptrial_noblinks['sacc']==True])>0:
                cluster_sacc, saccs = mask_cluster( ptrial_noblinks.loc[ptrial_noblinks['sacc']==True])
             
                len_sacc = [i for i, cluster in enumerate(cluster_sacc) for _ in range(len(cluster))]
            
                # Assign saccade cluster labels or NaN based on boolean column
                sacc_iter = iter(len_sacc)
                ptrial_noblinks['sacc_count']= [
                    next(sacc_iter) if is_sacc else np.nan
                    for is_sacc in ptrial_noblinks['sacc']
                ]
            else:
                print(f"{trial_id},{p_id},no saccades")
            
            
            #Append to container
            cleaned_data.append(ptrial_noblinks)
            #copy before modifying
            ptrial_nob= ptrial_noblinks.copy()
            #change index to original before resetting 
            ptrial_nob.index=ptrial_idx
            
            ptrial_raw_2= ptrial_raw.copy()
            ptrial_raw_2['sacc']=np.repeat(np.nan, len(ptrial_raw_2))
            ptrial_raw_2['sacc_count']=np.repeat(np.nan, len(ptrial_raw_2))
            ptrial_raw_2['fix']=np.repeat(np.nan, len(ptrial_raw_2))
            ptrial_raw_2['fix_count']=np.repeat(np.nan, len(ptrial_raw_2))
            
           
            for i in ptrial_idx:
                ptrial_raw_2.loc[i]=ptrial_nob.loc[i]
                
            rawclass_data.append(ptrial_raw_2.copy())    
              
    # Combine all cleaned participant data for this trial

    yesblinks_df = pd.concat(rawclass_data, ignore_index=True)
    yesblinks = yesblinks_df.loc[(yesblinks_df['Pupil Size Right X [px]']=='-') & (yesblinks_df['Point of Regard Right X [px]'].isna() ) & (yesblinks_df['Point of Regard Right Y [px]'].isna())]
    print(f"Blinks/Total: {len(yesblinks)}/{len(yesblinks_df)}")
    yesblinks_df.to_pickle(os.path.join(output_dir,"Classified_YesBlink.pkl"))
    
    return yesblinks_df


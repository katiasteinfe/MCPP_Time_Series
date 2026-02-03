# -*- codindf: utf-8 -*-
"""
Created on Thu Sep 18 20:09:54 2025

@author: ksteinfe

"""

import numpy as np
import pandas as pd
import os
import re 
from stationary_entropy_helpers import shannon_entropy_bits, normalized_entropy

def compute_dwell_metrics_children(I2MW_fix_clean, output_dir):
    '''
    
    Parameters
    ----------
    I2MW_fix_clean : df
        DataFrame of fixations as output by sanitize_adults.py
    output_dir : path
        Where output is saved as pkl

    Returns
    -------
    DwellMetrics : df, saved as FaceTrialSummary.pkl
        Dwell metrics for each trial, includes:
        - latency: onset of first target fixation,
                   the first fixation in the trial is not considered
        - target_PFA: fixation on the target over sum of face fixations
        - distractor_PFA: sum of fixations on distractors 
                          over sum of face fixations
        - STE_allfaces_PFA: stationary entropy on all face AOIs
        - STE_distractors_PFA: normalized stationary entropy 
                               on all face AOIs
    DwellMetrics : df, saved as DwellMetrics.pkl
        Transition metrics averaged for trial.

    '''
    I2MW_fix = I2MW_fix_clean.copy()
    
    face_labels = ['LeftTopFace', 'RightTopFace', 'RightBottomFace','LeftBottomFace']
    
    sync_rows = []
    
    for (pid, trial), df in I2MW_fix.groupby(['Participant','Trial'], sort=False):
        df = df.copy()
        cond = df.Condition.iloc[0]
        #print(cond)
        stim = df.Stimulus.iloc[0]
    
            
        if cond == 'Async':
            continue
        
        # sums per face 
        face_sums = (df.loc[df['fAOI'].isin(face_labels), ['fAOI','fixdur']]
                       .groupby('fAOI', sort=False)['fixdur']
                       .sum()
                       .reindex(face_labels, fill_value=0))
    
        # totals
        faces_total = face_sums.sum()
        if faces_total == 0:
            print(f'{pid}, {trial}, {df.fix_count.max()}: face sums is 0')
            continue
            
        nonface_total = df.loc[df['fAOI'] == '-']['fixdur'].sum()
        
        fix_total = df['fixdur'].sum()
        
        # check that the totals match
        if not np.isclose(faces_total + nonface_total, fix_total):
    
            print(f'{pid}, {trial}: sum of face + non face is not == to total of fixs')
        
        # as a record
        trial_total = df.fix_end.iloc[-1] - df.fix_start.iloc[0]
  
        targ = df.Target.iloc[0]
        # targ_split = re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|\d+', targ)
        # targ = targ_split[1]+targ_split[0]+'Face'
       
        actor = df.Actor.iloc[0]
        #actor = stim.split('_')[0]
        iteration = df.Iteration.iloc[0]
        #iteration = stim.split(' ')[3] 
        age = df.Age.iloc[0]
    
        if not age:
            age = 0
        group = df.Group_demo.iloc[0]
        
        fix_count_total = df.iloc[-1].fix_count
         
        fix_count_faces = df.loc[df.fAOI != '-'].fix_count.count()
         
        
        row = {'Participant': pid, 'Trial': trial, 
               'Condition': cond, 'Actor':actor, 
               'Iteration':iteration,'Age':age, 
               'Target':targ, 'Stimulus':stim, 'Group':group,
               'Total_Fix': fix_count_total, 'Total_Fix_Faces': fix_count_faces}#'Target':targ, }
        
       
        # append totals
        row['nonface_time'] =  nonface_total
        row['face_time'] = faces_total
        row['fix_time'] = nonface_total + faces_total
        row['trial_time'] = trial_total
    
        # append PTLT for faces / fix total (1-nonface)
        row['face_PFX'] = (faces_total / fix_total)*100 if (faces_total.all()>0) & (fix_total > 0) else 0.0
    
        # time and PTLT per face / total face fixation time  
        for fl in face_labels:
            row[f'{fl}_time'] = face_sums.loc[fl]
            row[f'{fl}_PFA'] = (face_sums.loc[fl] / faces_total)*100 if (face_sums[fl]>0) & (faces_total > 0) else 0.0
        
        #compute PTLT for target and distractors without averaging over distractors PTLT
        row['target_time'] = face_sums.loc[face_sums.index==targ].sum()
        row['distractors_time'] = face_sums.loc[face_sums.index!=targ].sum()
        
        row['target_PFA'] = (row['target_time'] / faces_total)*100 if (row['target_time'].all()>0) & (faces_total > 0) else 0.0
        row['distractors_PFA'] = (row['distractors_time'] / faces_total)*100 if (row['distractors_time'].all()>0) & (faces_total > 0) else 0.0
    
        # entropy on face time / total faces time
        counts = face_sums.reindex(face_labels, fill_value=0).to_numpy(dtype=float)
        faces_total_arr = np.asarray(  [faces_total], dtype=float)
        p_FA =counts / faces_total_arr if (counts.any() != 0) & (faces_total_arr > 0) else np.zeros_like(counts, dtype=float)
        
        row['STE_allfaces_PFA'] = shannon_entropy_bits(p_FA)
        row['normSTE_allfaces_PFA'] = normalized_entropy(p_FA, n_states=len(face_labels))
    
        counts_distractors = face_sums.loc[face_sums.index != targ].to_numpy(dtype=float)
        counts_distractors=counts_distractors[counts_distractors>0]
        total_FA_dist_time = faces_total_arr-face_sums.loc[face_sums.index == targ].sum()
        p_dist_FA =counts_distractors / total_FA_dist_time if (counts.sum()> 0) & (total_FA_dist_time > 0) else np.zeros_like(counts_distractors, dtype=float)
        row['STE_distractors_PFA'] = shannon_entropy_bits(p_dist_FA)
        row['normSTE_distractors_PFA'] = normalized_entropy(p_dist_FA, n_states=len(face_labels)-1)
         
        # ensure time order - should be fine
        df = df.sort_values('fix_count', kind='mergesort')
    
        face_labels = ['LeftTopFace', 'RightTopFace', 'RightBottomFace','LeftBottomFace']
    
        mask = (df['fAOI'] == targ)
        
        if (mask==True).any():
            first_time = df[1:].loc[mask, 'fix_start'].iloc[0]     # safe: iloc on the filtered series
            row['target_found']=1
            row['latency']=first_time
            
            if first_time > trial_total:
                print(f'!! error, check {pid}, {trial} - lat > trial end')
        else:
    
            print(f'{pid}, {trial}, {targ}, {cond}: first time is nan, total fixs {df.fix_count.max()}')
            #print(f'{df.fAOI}')
            row['target_found']=0
            row['latency'] = np.nan
            sync_rows.append(row)
            continue
        
            
    
        
        sync_rows.append(row)
    
        
    
    FaceTrialSummary = pd.DataFrame(sync_rows)
    

    async_rows=[]
    #I2MW_fix['Actor']=I2MW_fix.Stimulus.apply(lambda x: x.split('_')[0])
    #I2MW_fix['Iteration']=I2MW_fix.Stimulus.apply(lambda x: x.split(' ')[3] )
    # Compute the entropy on equivalent latency period in Async trials with same target
    for (pid, target, actor, iteration), sync_trial  in I2MW_fix.loc[I2MW_fix.Condition=='Sync'].groupby(['Participant','Target','Actor','Iteration'], sort=False):
        
        if len(sync_trial.Target.unique())>1:
            print(f'{pid}-{target}-more than 1 trial with this stimulus in SYNC')
            
        targ=target
        # targ_split = re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|\d+', target)
        # targ = targ_split[1]+targ_split[0]+'Face'
        
        sync_summary=FaceTrialSummary.loc[(FaceTrialSummary.Participant==pid) & 
                                       (FaceTrialSummary.Target==targ) & 
                                       (FaceTrialSummary.Actor==actor) &
                                       (FaceTrialSummary.Iteration==iteration)&
                                       (FaceTrialSummary.Condition == 'Sync') ]
        if len(sync_summary)==0:
            print(f'{pid}-{target}-{actor}-{iteration}-Sync empty')
            continue
        async_trial = I2MW_fix.loc[
            (I2MW_fix.Participant==pid) &
            (I2MW_fix.Target==target) &
            (I2MW_fix.Actor==actor) &
            (I2MW_fix.Iteration==iteration) &
            (I2MW_fix.Condition=='Async')
        ]
        
        if async_trial.empty:
            # no paired ASYNC trial to compute pre/post
            print(f'{pid}, {target},{actor},{iteration}: no corresponding async trial ')
            continue
        
        trials = async_trial.Trial.unique()
        if len(trials) > 1:
            print(f'{pid}-{target}-{trials} is len {len(trials)} for ASYNC')
    
        age = async_trial.Age.iloc[0]
        group = async_trial.Group_demo.iloc[0]
        if pd.isna(age):
            age = 0
            
        fix_count_total = async_trial.iloc[-1].fix_count
         
        fix_count_faces = async_trial.loc[async_trial.fAOI != '-'].fix_count.count()
         
        stim = async_trial.Stimulus.iloc[0]
       
        row = {
            'Participant': pid, 'Condition': 'Async', 'Actor': actor,
            'Iteration': iteration, 'Target': targ, 'Age': age, 
            'Group': group, 'Trial': trials[0], 'Stimulus':stim,
            'Total_Fix': fix_count_total, 'Total_Fix_Faces': fix_count_faces
            }
        
        
        # sums per face 
        face_sums = (async_trial.loc[async_trial['fAOI'].isin(face_labels), ['fAOI','fixdur']]
                       .groupby('fAOI', sort=False)['fixdur']
                       .sum()
                       .reindex(face_labels, fill_value=0))
    
        # totals
        faces_total = face_sums.sum()
        if faces_total == 0:
            print(f'{pid}, {trial}, {async_trial.fix_count.max()}: face sums is 0')
            continue
            
        nonface_total = async_trial.loc[async_trial['fAOI'] == '-']['fixdur'].sum()
        
        fix_total = async_trial['fixdur'].sum()
        
        # check that the totals match
        if not np.isclose(faces_total + nonface_total, fix_total):
    
            print(f'{pid}, {trial}: sum of face + non face is not == to total of fixs')
        
        # as a record
        trial_total = async_trial.fix_end.iloc[-1] - async_trial.fix_start.iloc[0]
       
        # append totals
        row['nonface_time'] =  nonface_total
        row['face_time'] = faces_total
        row['fix_time'] = nonface_total + faces_total
        row['trial_time'] = trial_total

    
        # time and PTLT per face / total face fixation time  
        for fl in face_labels:
            row[f'{fl}_time'] = face_sums.loc[fl]
            row[f'{fl}_PFA'] = (face_sums.loc[fl] / faces_total)*100 if (face_sums[fl]>0) & (faces_total > 0) else 0.0
        
        #compute PTLT for target and distractors without averaging over distractors PTLT
        row['target_time'] = face_sums.loc[face_sums.index==targ].sum()
        row['distractors_time'] = face_sums.loc[face_sums.index!=targ].sum()
        
        row['target_PFA'] = (row['target_time'] / faces_total)*100 if (row['target_time'].sum()>0) & (faces_total > 0) else 0.0
        row['distractors_PFA'] = (row['distractors_time'] / faces_total)*100 if (row['distractors_time'].sum()>0) & (faces_total > 0) else 0.0
    
        # entropy on face time / total faces time
        counts = face_sums.reindex(face_labels, fill_value=0).to_numpy(dtype=float)
        faces_total_arr = np.asarray(  [faces_total], dtype=float)
        p_FA =counts / faces_total_arr if (counts.any() != 0) & (faces_total_arr > 0) else np.zeros_like(counts, dtype=float)
        
        row['STE_allfaces_PFA'] = shannon_entropy_bits(p_FA)
        row['normSTE_allfaces_PFA'] = normalized_entropy(p_FA, n_states=len(face_labels))
    
        counts_distractors = face_sums.loc[face_sums.index != targ].to_numpy(dtype=float)
        counts_distractors=counts_distractors[counts_distractors>0]
        total_FA_dist_time = faces_total_arr-face_sums.loc[face_sums.index == targ].sum()
        p_dist_FA =counts_distractors / total_FA_dist_time if (counts.sum()> 0) & (total_FA_dist_time > 0) else np.zeros_like(counts_distractors, dtype=float)
        row['STE_distractors_PFA'] = shannon_entropy_bits(p_dist_FA)
        row['normSTE_distractors_PFA'] = normalized_entropy(p_dist_FA, n_states=len(face_labels)-1)
        # entropy on face time / total face + nonface time
    
        latency = sync_summary['latency'].iloc[0]
        
        if pd.isna(latency):
            row['latency']= np.nan
            row['target_found'] = 0
            async_rows.append(row)
            print(f'{pid}-{age}-{actor}-{iteration}-{targ}: target not found for Sync')
            continue
        else:
            row['latency'] = latency
            row['target_found'] = 1
            
      
        # entropy on face time / total faces time
        counts = face_sums.reindex(face_labels, fill_value=0).to_numpy(dtype=float)
        faces_total_arr = np.asarray(  [faces_total], dtype=float)
        p_FA =counts / faces_total_arr if (counts.any() != 0) & (faces_total_arr > 0) else np.zeros_like(counts, dtype=float)
        
        age = async_trial.Age.iloc[0]
        group = async_trial.Group_demo.iloc[0]
        if not age:
            age = 0
            
     
        async_rows.append(row)

    
    sync_df= pd.DataFrame(sync_rows)
    
    async_df = pd.DataFrame(async_rows)
    
    DwellMetrics=pd.concat([sync_df,async_df])

    DwellMetrics = DwellMetrics.sort_values(['Participant','Target','Actor','Iteration'])
    
    DwellMetrics.to_pickle(os.path.join(output_dir, 'DwellMetrics_Children.pkl'))

    
    return DwellMetrics
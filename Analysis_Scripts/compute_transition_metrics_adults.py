# -*- codindf: utf-8 -*-
"""
Created on Thu Sep 18 20:09:54 2025

@author: ksteinfe

"""


import pandas as pd
from transition_entropy_helpers import _transition_matrix_AOIs, GTE, directional_counts
import os 


def compute_transition_metrics_adults(I2MW_fix_clean, output_dir):
    '''

    Parameters
    ----------
    I2MW_fix_clean : df
        DataFrame of fixations as output by sanitize_adults.py
    output_dir : path
        Where output is saved as pkl
    Returns
    -------
    TransitionMetrics : df
        Transition metrics for each trial, includes:
        - latency : onset of first target fixation,
                   the first fixation in the trial is not considered
        - GTE_allfaces : transition entropy on all face AOIs
        - mGTE_allfaces : modified transition entropy on all face AOIs
        - GTE_distractors : transition entropy involving distractor AOIs
        - mGTE_distractors : modified transition entropy 
                            involving distractor AOIs
        - GTE_target: transition entropy involving the target AOI
        - mGTE_distractors : modified transition entropy involving the target 
    TransitionMetrics : df
        Transition metrics for each trial.

    '''
    
    I2MW_fix=I2MW_fix_clean.copy()
    
    # Define face labels
    face_labels = ['LeftTopFace', 'RightTopFace', 'RightBottomFace','LeftBottomFace']
    AOI_LEVELS = face_labels
    
    I2MW_fix['Actor']=I2MW_fix.Stimulus.apply(lambda x: x.split('_')[0])
    
    I2MW_fix['Iteration']=I2MW_fix.Stimulus.apply(lambda x: x.split(' ')[3] )
    sync_rows=[]
    
    for (pid, trial), df in I2MW_fix.groupby(['Participant','Trial'], sort=False):
        df = df.copy()
        
          
        if df.empty :
           continue
        
        cond = df.Condition.iloc[0]
    
        if cond == 'Async':
            continue
        
        # sums per face 
        face_sums = (df.loc[df['fAOI'].isin(face_labels), ['fAOI','fixdur']]
                       .groupby('fAOI', sort=False)['fixdur']
                       .sum()
                       .reindex(face_labels, fill_value=0))
    
        # totals
        faces_total= face_sums.sum().sum()
        #faces_total = face_sums.loc[face_sums.index != '-'].sum()
        if faces_total == 0:
            print(f'{pid}, {trial}, {df.fix_count.max()}: face sums is 0')
            
            continue
            
        nonface_total = df.loc[df['fAOI'] == '-']['fixdur'].sum()
        
        
        fix_total = df['fixdur'].sum()

        
        # as a record
        trial_total = df.fix_end.iloc[-1] - df.fix_start.iloc[0]
      
        #Select only Vis Async trials
        cond =  df.Condition.iloc[0]
        targ = df.Target.iloc[0]
        stimulus = df.Stimulus.iloc[0]
        actor = df.Actor.iloc[0]
        iteration = df.Iteration.iloc[0]
        age = 11 # set to 11 for plotting
    
        if not age:
            age = 0
            
        group = 0 # group =0 for adults
        
        fix_count_total = df.iloc[-1].fix_count
        
        fix_count_faces = df.loc[df.fAOI != '-'].fix_count.count()

        row = {'Participant': pid, 'Trial': trial, 'Condition': cond, 'Actor':actor, 'Iteration':iteration,'Age':age, 'Target':targ, 'Stimulus':stimulus, 'Group':group,
               'Total_Fix': fix_count_total, 'Total_Fix_Faces': fix_count_faces}
        
        face_sums = (df.loc[df['fAOI'].isin(face_labels), ['fAOI','fixdur']]
                       .groupby('fAOI', sort=False)['fixdur']
                       .sum()
                       .reindex(face_labels, fill_value=0))
        AOIface_sums = face_sums.loc[face_sums.index != '-']
        
        # total time of fixation 
        row['fix_total'] = fix_total
       
        # total time of fixation outside of face AOIs
        row['nonface_time'] =  nonface_total
        # total time of fixations on face AOIs
        row['face_time'] = faces_total
        # sum of fixations on faces and outside of faces
        row['fix_time'] = nonface_total + faces_total
        # total duration of a trial
        row['trial_time'] = trial_total
        # total time of fixation on face AOIs that are not the target face
        distractors_time = face_sums.loc[face_sums.index!=targ].sum()
        # total time of fixation on the target face AOI
        target_time = face_sums.loc[face_sums.index==targ].sum()
        row['dist_time'] = distractors_time
        row['targ_time'] = target_time
        
        #Calculate face-face only
        all_seq =  df["fAOI"].tolist()
        
        # All transitions between faces (does not include transitions to/from area outside of faces)
        all_counts_AOI = _transition_matrix_AOIs(all_seq, AOI_LEVELS, count_targ=0, targ=None) # all transitions
        n_allswitches_AOI =  int(all_counts_AOI.to_numpy().sum())
        # Transition entropy between all faces 
        all_ent_AOI = GTE(all_counts_AOI, AOIface_sums, time_weight=1)
    
        row["Nswitches_AOI"]=n_allswitches_AOI
        row["Transitions_AOI"]=all_counts_AOI
        row["GTE_AOI"]=all_ent_AOI
        
        #All transitions between distractors 
        all_dist_counts_AOI = _transition_matrix_AOIs(all_seq, AOI_LEVELS, count_targ=0, targ=targ) # distractors adjacent
        n_distswitches_AOI =  int(all_dist_counts_AOI.to_numpy().sum())
        #Transition entropy between distractors
        all_dist_ent_AOI = GTE(all_dist_counts_AOI, AOIface_sums, time_weight=1)
        #Modified transition entropy between distractors (no time weighting)
        all_notime_dist_ent_AOI = GTE(all_dist_counts_AOI, AOIface_sums, time_weight=0, TD=0, targ=targ)
        row["Nswitches_Dist_AOI"]=n_distswitches_AOI
        row["Transitions_Dist_AOI"]=all_dist_counts_AOI
        row["GTE_Dist_AOI"]=all_dist_ent_AOI
        row["mGTE_Dist_AOI"]=all_notime_dist_ent_AOI
        
        #All transitions involving the target 
        all_targ_counts_AOI = _transition_matrix_AOIs(all_seq, AOI_LEVELS, count_targ=1, targ=targ) #targ adjacent
        n_targswitches_AOI =  int(all_targ_counts_AOI.to_numpy().sum())
        #Transition entropy involving the target
        all_targ_ent_AOI = GTE(all_targ_counts_AOI, AOIface_sums, time_weight=1)
        #Modified transition entropy involving the target (no time weighting)
        all_notime_targ_ent_AOI = GTE(all_targ_counts_AOI, AOIface_sums, time_weight=0, TD=1, targ=targ)
        
        row["Nswitches_Targ_AOI"]=n_targswitches_AOI
        row["Transitions_Targ_AOI"]=all_targ_counts_AOI
        row["GTE_Targ_AOI"]=all_targ_ent_AOI
        row["mGTE_Targ_AOI"]=all_notime_targ_ent_AOI
       
        # Counts of transitions to and from the target 
        td, dt = directional_counts(all_seq, targ, [x for x in face_labels if x!=targ])
        row['Nswitch_from_Targ'] =  td
        row['Nswitch_to_Targ'] =  dt

        sync_rows.append(row)
    
    FaceTrialSummary = pd.DataFrame(sync_rows)
    
    #Second pass to compute pre and post in Async according to latency
    async_rows=[]
    row={}
    async_rows=[]

    # Compute the entropy on equivalent latency period in Async trials with same target
    for (pid, target, actor, iteration), sync_trial  in I2MW_fix.loc[I2MW_fix.Condition=='Sync'].groupby(['Participant','Target','Actor','Iteration'], sort=False):
     
        sync_summary=FaceTrialSummary.loc[(FaceTrialSummary.Participant==pid) & 
                                       (FaceTrialSummary.Target==target) & 
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
        
        targ=target
        
        if async_trial.empty:
            # no paired ASYNC trial to compute pre/post
            print(f'{pid}, {target},{actor},{iteration}: no corresponding async trial ')
            continue
        
        trial = async_trial.Trial.unique()
        if len(trial) > 1:
            print(f'{pid}-{target}-{trial} is len {len(trial)} for ASYNC')
    
        age = 11  # set as 11 for plotting
        group = 0 # for adults group is always 0
        if pd.isna(age):
            age = 0
            
        stim = async_trial.Stimulus.iloc[0]
        
            
        fix_count_total = async_trial.iloc[-1].fix_count
         
        fix_count_faces = async_trial.loc[async_trial.fAOI != '-'].fix_count.count()
         
        
        row = {
            'Participant': pid, 'Condition': 'Async', 'Actor': actor,
            'Iteration': iteration, 'Target': target, 'Age': age, 
            'Group': group, 'Trial': trial[0], 'Stimulus':stim,
            'Total_Fix': fix_count_total, 'Total_Fix_Faces': fix_count_faces
        }
        
        fix_total = async_trial['fixdur'].sum()
        row['fix_total'] = fix_total
        
        # sums per face 
        face_sums = (async_trial.loc[async_trial['fAOI'].isin(face_labels), ['fAOI','fixdur']]
                       .groupby('fAOI', sort=False)['fixdur']
                       .sum()
                       .reindex(face_labels, fill_value=0))
    
        # totals
        faces_total = face_sums.sum().sum()
        if faces_total == 0:
            print(f'{pid}, {trial}, {async_trial.fix_count.max()}: face sums is 0')
            continue
            
        nonface_total = async_trial.loc[async_trial['fAOI'] == '-']['fixdur'].sum()
        
        AOIface_sums = face_sums.loc[face_sums.index != '-']
     
  
        # as a record
        trial_total = async_trial.fix_end.iloc[-1] - async_trial.fix_start.iloc[0]
        #if trial_total_end < trial_total:
            #print(f'!! {pid}, {trial}, trial total shorter than start of first fix to end of last fix')

        # append totals
        row['nonface_time'] =  nonface_total
        row['face_time'] = faces_total
        row['fix_time'] = nonface_total + faces_total
        row['trial_time'] = trial_total
        
        distractors_time = face_sums.loc[face_sums.index!=targ].sum()
    
        target_time = face_sums.loc[face_sums.index==targ].sum()
        row['dist_time'] = distractors_time
        #print(row['dist_time'])
        row['targ_time'] = target_time
        
        #Calculate face-face only
        
        all_seq =  async_trial["fAOI"].tolist()
        
        #All transitions between faces
        all_counts_AOI = _transition_matrix_AOIs(all_seq, AOI_LEVELS, count_targ=0, targ=None) # all transitions
        n_allswitches_AOI =  int(all_counts_AOI.to_numpy().sum())
        #Entropy of transitions between all face AOIs
        all_ent_AOI = GTE(all_counts_AOI, AOIface_sums, time_weight=1)
        
        row["Nswitches_AOI"]=n_allswitches_AOI
        row["Transitions_AOI"]=all_counts_AOI
        row["GTE_AOI"]=all_ent_AOI
 
        
        # All transitions between distractors
        all_dist_counts_AOI = _transition_matrix_AOIs(all_seq, AOI_LEVELS, count_targ=0, targ=targ) # distractors adjacent
        n_distswitches_AOI =  int(all_dist_counts_AOI.to_numpy().sum())
        # Entropy of transitions between distractors
        all_dist_ent_AOI = GTE(all_dist_counts_AOI, AOIface_sums, time_weight=1)
        # Modified entropy of transitions between distractors (no time weighting)
        all_notime_dist_ent_AOI = GTE(all_dist_counts_AOI, AOIface_sums, time_weight=0, TD=0, targ=targ)
        row["Nswitches_Dist_AOI"]=n_distswitches_AOI
        row["Transitions_Dist_AOI"]=all_dist_counts_AOI
        row["GTE_Dist_AOI"]=all_dist_ent_AOI
        row["mGTE_Dist_AOI"]=all_notime_dist_ent_AOI
        
        # All transitions involvinf the target face AOI
        all_targ_counts_AOI = _transition_matrix_AOIs(all_seq, AOI_LEVELS, count_targ=1, targ=targ) #targ adjacent
        n_targswitches_AOI =  int(all_targ_counts_AOI.to_numpy().sum())
        # Transition entropy involving the target face AOI
        all_targ_ent_AOI = GTE(all_targ_counts_AOI, AOIface_sums, time_weight=1)
        # Modified transition entropy involving the target face AOI (no time weighting)
        all_notime_targ_ent_AOI = GTE(all_targ_counts_AOI, AOIface_sums, time_weight=0, TD=1, targ=targ)
        
        
        row["Nswitches_Targ_AOI"]=n_targswitches_AOI
        row["Transitions_Targ_AOI"]=all_targ_counts_AOI
        row["GTE_Targ_AOI"]=all_targ_ent_AOI
        row["mGTE_Targ_AOI"]=all_notime_targ_ent_AOI
       
        
        td, dt = directional_counts(all_seq, targ, [x for x in face_labels if x!=targ])
        row['Nswitch_from_Targ'] =  td
        row['Nswitch_to_Targ'] =  dt
        #Calculate face-nonAOI only
    
        async_rows.append(row)
        
    
    sync_df= FaceTrialSummary.copy()
    
    async_df = pd.DataFrame(async_rows)
    
    TransitionMetrics=pd.concat([sync_df,async_df])
    
    TransitionMetrics = TransitionMetrics.sort_values(['Participant','Target','Actor','Iteration'])
    
    TransitionMetrics.to_pickle(os.path.join(output_dir, 'TransitionMetrics_Adults.pkl'))
    
    return TransitionMetrics
#%%
# )
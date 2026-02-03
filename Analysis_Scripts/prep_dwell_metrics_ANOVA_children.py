# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 14:43:05 2025

@author: ksteinfe
"""

import numpy as np
import pandas as pd
import os

def prep_dwell_metrics_ANOVA_children( file_name, data_dir, output_dir):
    
    FaceSummary = pd.read_pickle(os.path.join(data_dir, file_name))
    face_labels = ['LeftTopFace', 'RightTopFace', 'RightBottomFace','LeftBottomFace']
    
    #-----------------------------------------------------------------------------
    # Latency
    #------------------------------------------------------------------------------
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Target', 'Age'], 
        value_vars=['latency'],
        var_name='StimType_PF', 
        value_name='Latency'
    )
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Target'],
                             values='Latency',
                             aggfunc='mean')
                .reset_index())
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    wide.to_pickle(os.path.join(output_dir,"Latency_Wide_Target.pkl"))
    wide.to_csv(os.path.join(output_dir,"Latency_Wide_Target.csv"))
    
    
    #------------------------------------------------------------------------------
    # Target PTLT
    #------------------------------------------------------------------------------
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Target','Age'], 
        value_vars=['target_PFA'],
        var_name='StimType_PF', 
        value_name='PTLT'
    )
    
    # Stimulus type: target vs distractor
    FaceLong_allv['StimType'] = [x.split('_')[0] for x in FaceLong_allv['StimType_PF']]
    FaceLong_allv=FaceLong_allv.loc[FaceLong_allv['StimType']=='target']
    
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition','Target'],
                             values='PTLT',
                             aggfunc='mean')
                .reset_index())
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    
    wide.to_pickle(os.path.join(output_dir,"TargetPTLT_Wide_CondTarget.pkl"))
    wide.to_csv(os.path.join(output_dir,"TargetPTLT_Wide_CondTarg.csv"))
    
    #------------------------------------------------------------------------------
    # Compute PTLT2, as in Lewkovicz et al. (2021, 2022)
    #------------------------------------------------------------------------------
    # For comparison with previous papers
    # Where fixations over distractors are averaged v. summed
    FaceSummary=FaceSummary.reset_index(drop=True)
    FaceSummary['target_PFA_2'] = [ (FaceSummary.loc[i,f'{t}_time'] / FaceSummary.loc[i,'face_time'])*100 for i,t in zip(FaceSummary.index,FaceSummary.Target) ]
    FaceSummary['distractors_PFA_2'] = [ np.mean([FaceSummary.loc[i,f'{d}_time'] / FaceSummary.loc[i,'face_time'] for d in face_labels if d!=t ])*100 for i,t in zip(FaceSummary.index,FaceSummary.Target) ]
    
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Target', 'Age'], 
        value_vars=['target_PFA_2', 'distractors_PFA_2'],
        var_name='StimType_PF', 
        value_name='PTLT2'
    )

    
    # Stimulus type: target vs distractor
    FaceLong_allv['StimType'] = [x.split('_')[0] for x in FaceLong_allv['StimType_PF']]
    #FaceLong_allv=FaceLong_allv.loc[FaceLong_allv['StimType']=='target']
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition','StimType'],
                             values='PTLT2',
                             aggfunc='mean')
                .reset_index())
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    
    wide.to_pickle(os.path.join(output_dir,"PTLT2_Wide_CondStimType.pkl"))
    wide.to_csv(os.path.join(output_dir,"PTLT2_Wide_CondStimType.csv"))
    
    #-----------------------------------------------------------------------------
    # normalized STE on all faces
    #-----------------------------------------------------------------------------
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Target','Age'], 
        value_vars=['normSTE_allfaces_PFA'],
        var_name='StimType_PF', 
        value_name='Entropy'
    )
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition','Target'],
                             values='Entropy',
                             aggfunc='mean')
                .reset_index())
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    wide.to_pickle(os.path.join(output_dir,"normSTE_allfaces_Wide_CondTarg.pkl"))
    wide.to_csv(os.path.join(output_dir,"normSTE_allfaces_Wide_CondTarg.csv"))
    
    #------------------------------------------------------------------------------
    #Normalized STE on distractors
    #------------------------------------------------------------------------------
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Target', 'Age'], 
        value_vars=['normSTE_distractors_PFA'],
        var_name='StimType_PF', 
        value_name='Entropy'
    )
    
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition','Target'],
                             values='Entropy',
                             aggfunc='mean')
                .reset_index())
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    wide.to_pickle(os.path.join(output_dir,"normSTE_distractors_Wide_CondTarg.pkl"))
    wide.to_csv(os.path.join(output_dir,"normSTE_distractors_Wide_CondTarg.csv"))
    
    return

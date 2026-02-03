# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 14:43:05 2025

@author: ksteinfe
"""

import pandas as pd
import os

def prep_transition_metrics_ANOVA_children( file_name, data_dir, output_dir):
    
    FaceSummary = pd.read_pickle(os.path.join(data_dir, file_name))
    #-----------------------------------------------------------------------------
    # normalized GTE on all faces
    #-----------------------------------------------------------------------------
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Target','Age'], 
        value_vars=['GTE_AOI'],
        var_name='StimType', 
        value_name='Entropy'
    )
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition','Target'],
                             values='Entropy',
                             aggfunc='mean')
                .reset_index())
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    wide.to_pickle(os.path.join(output_dir,"normGTE_Wide_CondTarg.pkl"))
    wide.to_csv(os.path.join(output_dir,"normGTE_Wide_CondTarg.csv"))
    
    #--------------------------------------------------------------------------
    # modified GTE on targets and distractors
    # -------------------------------------------------------------------------
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Age'], 
        value_vars=['mGTE_Dist_AOI', 'mGTE_Targ_AOI'],
        var_name='StimType', 
        value_name='Entropy'
        
    )
    FaceLong_allv["StimType"]=[x.split('_')[1] for x in FaceLong_allv.StimType]
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition','StimType'],
                             values='Entropy',
                             aggfunc='mean')
                .reset_index())
    
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    wide.to_pickle(os.path.join(output_dir,"mGTE_Wide_CondStimtype.pkl"))
    wide.to_csv(os.path.join(output_dir,"mGTE_Wide_CondStimtype.csv"))
    
    # -------------------------------------------------------------------------
    # compute rate of transitions
    # -------------------------------------------------------------------------
    # Rate of switches to target v. from target
    FaceSummary['rate_to_Targ'] = (
        FaceSummary['Nswitch_to_Targ'] / FaceSummary['targ_time']
    )


    FaceSummary['rate_from_Targ'] = (
        FaceSummary['Nswitch_from_Targ'] / FaceSummary['targ_time']
    )
    
    
    FaceLong_allv = FaceSummary.melt(
        id_vars=['Participant','Condition','Age'], 
        value_vars=['rate_from_Targ','rate_to_Targ'],
        var_name='StimType_PF', 
        value_name='RateSwitch'
    )
    
    # Stimulus type: target vs distractor
    FaceLong_allv['Direction'] = [x.split('_')[1] for x in FaceLong_allv['StimType_PF']]
    #FaceLong_allv=FaceLong_allv.loc[FaceLong_allv['StimType']=='Dist']
    
    
    wide = (FaceLong_allv.pivot_table(index=['Participant','Age'],
                             columns=['Condition', 'Direction'],
                             values='RateSwitch',
                             aggfunc='mean')
                .reset_index())
    
    wide.columns = ['_'.join(col).strip() for col in wide.columns.values]
    wide.to_pickle(os.path.join(output_dir,"RateTransition_Wide_CondDir.pkl"))
    wide.to_csv(os.path.join(output_dir,"RateTransition_Wide_CondDir.csv"))
        
    return
 
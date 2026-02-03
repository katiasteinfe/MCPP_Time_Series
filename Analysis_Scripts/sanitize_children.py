# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 19:39:10 2025

@author: ksteinfe

Transform the AOI column into face only and small AOI only columns
Remove the word Target from the AOI columns
Create a condition column
Create a target column
"""

#%%
import numpy as np
import pandas as pd
import os
from environment_setup import data_dir_children
import re
def sanitize_children(I2MW_fix, output_dir, data_dir_children = data_dir_children, 
                      exclude_pid = ['575_F_3yrs', 'P1104', 'P1070', 'P1220', 'P1003', 'P1006', 'P1081']):
    '''
    

    Parameters
    ----------
    I2MW_fix : data frame
        Fixations as classified by I2MW_classifier.py 
        and concatenated by Classify.py
    output_dir : path
        Where to save the output
    exclude_pid : list of participant ids
        Must match the ones in the Participant column
        DESCRIPTION. The default is ['575_F_3yrs', 'P1104', 
                                     'P1070', 'P1220', 'P1003',
                                     'P1006', 'P1081']

    Returns
    -------
    I2MW_fix : df 
        DatFrame ready for analysis, saved as I2MW_fix_clean.pkl
    Child_Participants: df, saved as csv
        List of participants
    Child_ParticipantsTrials : df, saved as csv
        Participants and trials for each stimulus
        Allows to check the LatinSquares design
    

    '''
    # Import the excel for demographics
    
    file_path = os.path.join(data_dir_children, "Exp1_Child_Participants_Design.xlsx")
    child_demo = pd.read_excel(file_path, sheet_name='Participants in NSF Exp 1 Child',header=0 )
    child_demo=child_demo.rename(columns={'Condition':'Group'})

    child_demo.to_pickle(os.path.join(output_dir,'Child_Demo.pkl'))

    
    # Create an age column by merging on participant
    child_demo = child_demo.rename(columns={'Participant Number':'Participant', 'Group':'Group_demo'})
    I2MW_fix = I2MW_fix.merge(child_demo, how='left', on='Participant')
    
    # Import the excel sheet for target quadrant
    child_design = pd.read_excel(file_path, sheet_name='Exp_Design',
                                 header=0)
    
    # Remove trials for which the participant's group or stimulus is not defined
    I2MW_fix = I2MW_fix[I2MW_fix.Group_demo.notna()]
    I2MW_fix = I2MW_fix[I2MW_fix.Stimulus.notna()]
    
    # Find the target quadrant for each stimulus and group
    I2MW_fix["Target"] = [ child_design.loc[child_design.Stimulus==Stimulus,
                                            [int(group)]].iloc[0,0] 
                          for Stimulus,group 
                          in zip(I2MW_fix.Stimulus, I2MW_fix.Group_demo)]
    
    # Change the target quadrant name format
    I2MW_fix['Target'] = I2MW_fix['Target'].replace('BbottomLeft','BottomLeft')
    targ_split = [re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|\d+',
                                     x) for x in I2MW_fix['Target']]
    I2MW_fix['Target'] = [x[1]+x[0]+'Face' for x in targ_split]

    # Exclude 8 y.o. group since not enough participants
    I2MW_fix =  I2MW_fix.loc[ I2MW_fix.Age != 8]
    
    #Exclude data from participants in exclude_pid
    I2MW_fix = I2MW_fix.loc[~I2MW_fix["Participant"].isin(exclude_pid)].copy()

    I2MW_fix = I2MW_fix.copy()
    # Create an sAOI column for small AOIs (eyes and mouth)
    # remove "Target"from the sAOI names
    I2MW_fix['AOI_Name_Right']= I2MW_fix['AOI_Name_Right'].apply(lambda x: [y for y in x])
    I2MW_fix['sAOI'] = I2MW_fix['AOI_Name_Right'].apply(lambda x: [aoi for aoi in x if ("Eye" in aoi) or ("Mouth" in aoi) ])
    
    aoi=[]
    for row in I2MW_fix['sAOI']:
        if row:
            aoi.append(row[0].replace('Target',''))
        else:
            aoi.append(np.nan)
    I2MW_fix['sAOI']=aoi      

    # Create an sAOI column for small AOIs (eyes and mouth)
    # remove "Target"from the sAOI names
    f_aoi=[]
    for row in I2MW_fix['AOI_Name_Right']:
        if row == ['-']:
            f_aoi.append('-')
        else:
            labels=[]
            for x in row:
                if 'Mouth' in x:
                    labels.append(x.split('Mouth')[0].replace('Target','')+"Face")
                elif 'Eye' in x:
                    labels.append(x.split('Eye')[0].replace('Target','')+"Face")
                elif 'Face' in x:
                    labels.append(x.replace('Target',''))
            # collapse: choose first, or join with ';'
            f_aoi.append(labels[0] if len(labels)>=1 else '-')
    
    I2MW_fix['fAOI']=f_aoi
    I2MW_fix['fAOI']=[ 'LeftBottomFace' if x=='LeftBbottomFace' else x for x in I2MW_fix['fAOI']]
    I2MW_fix.fAOI = I2MW_fix.fAOI.replace('LeftBbottomFace','LeftBottomFace')
    
    # Drop rows for which the stimulus is unnamed
    I2MW_fix=I2MW_fix.loc[I2MW_fix.Stimulus!='nan']

    # Create a column with actor's first name
    I2MW_fix['Actor']=I2MW_fix.Stimulus.apply(lambda x:x.split(' ')[0])
    # Create a column with the iteration
    I2MW_fix['Iteration']=I2MW_fix.Stimulus.apply(lambda x:x.split(' ')[1])

    
    # Create a columns with the condition
    #I2MW_fix['Condition']=I2MW_fix.Stimulus.apply(lambda x:x.split('_')[3])
    I2MW_fix['Condition'] = [x.split(' ')[-1] for x in I2MW_fix.Stimulus]
    #Create a column wiht the stimulus name
    I2MW_fix.Stimulus=I2MW_fix.Stimulus
    
    #Create a column for duration of fixations
    I2MW_fix = I2MW_fix.copy()
    I2MW_fix['fixdur'] = (I2MW_fix['fix_end'] - I2MW_fix['fix_start']).clip(lower=0)
    I2MW_fix.to_pickle(os.path.join(output_dir,'fix_clean_children.pkl'))
    
    Child_Participants = pd.DataFrame(I2MW_fix.Participant.unique())
    Child_Participants.to_csv(os.path.join(output_dir,'Child_Participants.csv'))
    Child_Participants.to_excel(os.path.join(output_dir,'Child_Participants.xlsx'))
    
    # Get unique combinations of Participant and Trial
    Child_ParticipantsTrials = pd.DataFrame(I2MW_fix[['Participant','Trial','Stimulus']].drop_duplicates())
    # Save to CSV
    Child_ParticipantsTrials.to_excel(
        os.path.join(output_dir, 'Child_Participants_Trials.xlsx'),
        index=False
    )
    
    return I2MW_fix

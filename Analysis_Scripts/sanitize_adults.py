# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 19:39:10 2025

@author: ksteinfe

Prepare the I2MW_fix df of the adult's experiment
for calculation of the dependent variables:
- Transform the AOI column into face only and small AOI only columns
- Remove the word Target from the AOI columns
- Create a condition column
- Create a target column
- Create a fixation duration column
- Exclude participants 
"""

import numpy as np
import os
import difflib

# Read the fixations from raw
#data_dir = r"C:\Users\ksteinfe\Desktop\MCPP Time Series\4_Preliminary_Analysis\MCPP_Time_Series_Code\0_Preprocessing_pipeline_fromraw\Preprocessing_results"
#I2MW_fix = pd.read_pickle(os.path.join(data_dir, 'I2MW_fix.pkl'))
#output_dir = r"C:\Users\ksteinfe\Desktop\MCPP Time Series\4_Preliminary_Analysis\MCPP_Time_Series_Code\6_Adults\Face_Dwell_Analysis"

def sanitize_adults(I2MW_fix, output_dir,exclude_pid=['P32','P26']):
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
        DESCRIPTION. The default is ['P32'].

    Returns
    -------
    I2MW_fix : df 
        Data frame ready for analysis

    '''
   
    # Create a column with actor's first name
    I2MW_fix['Actor']=I2MW_fix.Stimulus.apply(lambda x: x.split('_')[0])
    # Create a column with the iteration
    I2MW_fix['Iteration']=I2MW_fix.Stimulus.apply(lambda x: x.split(' ')[3] )
    
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
    
    # Sanitize AOI name column into a fAOI for face AOIs 
    # vs. '-' for somewhere else on the screen
    # Remove "target" from fAOI names
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
    

    # Add a condition column
    cond =  []
    for _,row in I2MW_fix.iterrows():
        #Select only Vis Async trials
        stim = row['Stimulus']
        if ('Vis' in stim) or ('Viis' in stim):
            cond.append('Async')
        elif 'AudSync' in stim:
            cond.append('Sync')
        else:
            print(stim)
    I2MW_fix['Condition'] = cond
    
    # add a Target column 
    face_labels = ['LeftTopFace', 'RightTopFace', 'RightBottomFace','LeftBottomFace']
    targ =  []
    for _,row in I2MW_fix.iterrows():
        target = row.Stimulus.split('ync ')[1].split(' -')[0]+'Face'
        if target not in face_labels:
            close_match = difflib.get_close_matches(target, face_labels, n=1, cutoff=0.6)[0]
            #print(f'{target} -> {close_match}')
            targ.append(close_match)
        else:
            targ.append(target)
        
    I2MW_fix['Target'] = targ

    #Exclude data from participants in exclude_pid
    I2MW_fix = I2MW_fix.loc[~I2MW_fix["Participant"].isin(exclude_pid)].copy()

    I2MW_fix = I2MW_fix.copy()
    
    #Create a column for duration of fixations
    I2MW_fix['fixdur'] = (I2MW_fix['fix_end'] - I2MW_fix['fix_start']).clip(lower=0)
    
    #Save as pickle
    I2MW_fix.to_pickle(os.path.join(output_dir,'fix_clean_adults.pkl'))

    return I2MW_fix

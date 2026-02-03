* Encoding: UTF-8.

GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\adults\2_analysis\transition\mGTE_Wide_CondStimtype.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
   V1 A32
    Participant A32
    Async_Dist F18.14
    Async_Targ F19.14
    Sync_Dist F18.14
    Sync_Targ F19.14.
EXECUTE.

DATASET NAME mGTE_Wide_CondStimtype.

GLM
 Sync_Dist Sync_Targ Async_Dist Async_Targ
  /WSFACTOR=Condition 2 Polynomial Stimtype 2 Polynomial
  /MEASURE=mGTE
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Stimtype) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype) COMPARE(Stimtype) ADJ(BONFERRONI)
   /EMMEANS=TABLES(Condition*Stimtype) COMPARE(Stimtype) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Stimtype Condition*Stimtype.





* Encoding: UTF-8.
GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\adults\2_analysis\dwell\PTLT2_Wide_CondStimType.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
    V1 A32
    Participant A32
    Async_distractors F19.14
    Async_target F19.14
    Sync_distractors F19.14
    Sync_target F19.14.
EXECUTE.

DATASET NAME PTLT2_Wide_CondStimtype.

GLM Async_distractors Async_target Sync_distractors Sync_target 
  /WSFACTOR=Condition 2 Polynomial Stimtype 2 Polynomial 
  /MEASURE=PTLT2
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Stimtype) COMPARE ADJ (BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype) COMPARE(Stimtype) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype) COMPARE(Condition) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Stimtype Condition*Stimtype.

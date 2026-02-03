* Encoding: UTF-8.

GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\adults\2_analysis\transition\RateTransition_Wide_CondDir.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
   V1 A32
    Participant A32
    Async_from F18.14
    Async_to F19.14
    Sync_from F18.14
    Sync_to F19.14.
EXECUTE.

DATASET NAME RateTransition_Wide_CondStimtype.

GLM
 Sync_from Sync_to Async_from Async_to
  /WSFACTOR=Condition 2 Polynomial Direction 2 Polynomial
  /MEASURE=RateTransition
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Direction) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Direction) COMPARE(Direction) ADJ(BONFERRONI)
   /EMMEANS=TABLES(Condition*Direction) COMPARE(Direction) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Direction Condition*Direction.





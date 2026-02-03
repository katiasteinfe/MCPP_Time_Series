* Encoding: UTF-8.

GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\adults\2_analysis\dwell\TargetPTLT_Wide_CondTarg.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
   V1 A32
    Participant A32
    Async_LeftBottomFace F18.14
    Async_LeftTopFace F19.14
    Async_RightBottomFace F18.14
    Async_RightTopFace F19.14
    Sync_LeftBottomFace F18.14
    Sync_LeftTopFace F19.14
    Sync_RightBottomFace F18.14
    Sync_RightTopFace F19.14.
EXECUTE.

DATASET NAME TargetPTLT_Wide_CondTarg.

GLM
  Sync_LeftTopFace Sync_RightTopFace Sync_RightBottomFace Sync_LeftBottomFace
  Async_LeftTopFace Async_RightTopFace Async_RightBottomFace Async_LeftBottomFace
  /WSFACTOR=Condition 2 Polynomial Target 4 Polynomial
  /MEASURE=TargetPTLT
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Target) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Target) COMPARE(Condition) ADJ(BONFERRONI)
   /EMMEANS=TABLES(Condition*Target) COMPARE(Target) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Target Condition*Target.




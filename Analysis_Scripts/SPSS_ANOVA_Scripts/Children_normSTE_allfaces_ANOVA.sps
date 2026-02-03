* Encoding: UTF-8.

GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\children\2_analysis\dwell\normSTE_allfaces_Wide_CondTarg.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
   V1 A32
    Participant A32
    Age A32
    Async_LeftBottomFace F18.14
    Async_LeftTopFace F19.14
    Async_RightBottomFace F18.14
    Async_RightTopFace F19.14
    Sync_LeftBottomFace F18.14
    Sync_LeftTopFace F19.14
    Sync_RightBottomFace F18.14
    Sync_RightTopFace F19.14.
EXECUTE.

DATASET NAME normSTE_allfaces_Wide_CondTarg.

GLM
  Sync_LeftTopFace Sync_RightTopFace Sync_RightBottomFace Sync_LeftBottomFace
  Async_LeftTopFace Async_RightTopFace Async_RightBottomFace Async_LeftBottomFace BY Age
  /WSFACTOR=Condition 2 Polynomial Target 4 Polynomial
  /MEASURE=normSTE
  /METHOD=SSTYPE(3)
 /METHOD=SSTYPE(3)
  /POSTHOC=Age(BONFERRONI) 
  /EMMEANS=TABLES(OVERALL) 
  /EMMEANS=TABLES(Age) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Target) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Target) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Target) COMPARE(Target) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Target) COMPARE(Age) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Target) COMPARE(Target) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Condition) COMPARE(Age) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Condition) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Target*Age) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Target*Age) COMPARE(Target) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Target*Age) COMPARE(Age) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Target Condition*Target
/DESIGN = Age.





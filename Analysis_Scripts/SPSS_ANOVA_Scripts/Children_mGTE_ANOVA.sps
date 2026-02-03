* Encoding: UTF-8.

GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\children\2_analysis\transition\mGTE_Wide_CondStimtype.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
   V1 A32
    Participant A32
    Age A32
    Async_distractors F18.14
    Async_target F19.14
    Sync_distractors F18.14
    Sync_target F19.14.
EXECUTE.

DATASET NAME mGTE_Wide_CondStimtype.

GLM
  Sync_distractors Sync_target Async_distractors Async_target BY Age
  /WSFACTOR=Condition 2 Polynomial Stimtype 2 Polynomial
  /MEASURE=normGTE
  /METHOD=SSTYPE(3)
  /POSTHOC=Age(BONFERRONI) 
  /EMMEANS=TABLES(OVERALL) 
  /EMMEANS=TABLES(Age) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Stimtype) COMPARE ADJ (BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype) COMPARE(Stimtype) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Condition) COMPARE(Age) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Condition) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Stimtype) COMPARE(Age) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Stimtype) COMPARE(Stimtype) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype*Age) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype*Age) COMPARE(Stimtype) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Stimtype*Age) COMPARE(Age) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Stimtype Condition*Stimtype
  /DESIGN = Age.

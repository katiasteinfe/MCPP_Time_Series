* Encoding: UTF-8.

GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\children\2_analysis\transition\RateTransition_Wide_CondDir.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
   /VARIABLES = 
   V1 A32
    Participant A32
    Age A32
    Async_from F19.14
    Async_to F19.14
    Sync_from F19.14
    Sync_to F19.14

DATASET NAME RateTransition_Wide_CondDirection.

GLM
 Sync_from Sync_to Async_from Async_to BY Age
  /WSFACTOR=Condition 2 Polynomial Direction 2 Polynomial
  /MEASURE=RateTransition
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(OVERALL) 
  /EMMEANS=TABLES(Age) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(Direction) COMPARE ADJ (BONFERRONI)
  /EMMEANS=TABLES(Condition*Direction) COMPARE(Direction) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Direction) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Condition) COMPARE(Age) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Condition) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Direction) COMPARE(Age) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Age*Direction) COMPARE(Direction) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Direction*Age) COMPARE(Condition) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Direction*Age) COMPARE(Direction) ADJ(BONFERRONI)
  /EMMEANS=TABLES(Condition*Direction*Age) COMPARE(Age) ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Condition Direction Condition*Direction
  /DESIGN=Age.




* Encoding: UTF-8.
GET DATA
  /TYPE=TXT
  /FILE="C:\Users\ksteinfe\Desktop\MCPP_Scripts\adults\2_analysis\dwell\Latency_Wide_Target.csv"
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
    Participant A11
    L_e_f_t_B_o_t_t_o_m_F_a_c_e F18.14
    L_e_f_t_T_o_p_F_a_c_e F19.14
    R_i_g_h_t_B_o_t_t_o_m_F_a_c_e F18.14
    R_i_g_h_t_T_o_p_F_a_c_e F19.14.
EXECUTE.

DATASET NAME Latency_Wide_Target.

* Rename to clean names for analysis.
RENAME VARIABLES
  (L_e_f_t_T_o_p_F_a_c_e = LeftTopFace)
  (R_i_g_h_t_T_o_p_F_a_c_e = RightTopFace)
  (R_i_g_h_t_B_o_t_t_o_m_F_a_c_e = RightBottomFace)
  (L_e_f_t_B_o_t_t_o_m_F_a_c_e = LeftBottomFace).
EXECUTE.

GLM LeftBottomFace LeftTopFace RightBottomFace RightTopFace 
  /WSFACTOR=Target 4 Polynomial
  /MEASURE=Latency
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Target) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Target



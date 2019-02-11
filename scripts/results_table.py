
from IPython.display import Image
# For later visualizaton scripts
import pygraphviz as pgv
import time
import sys
import random
import string
import re
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt, mpld3
import seaborn as sns

from IPython import embed

import tabulate
import yaml

#connect to application
from app import * 


  
def fmtr(v):
  if v >= 1:
    return "{:,.0f}".format(float('%.3g' % v))
  else:
    return "{:.2f}".format(float('%.2g' % v))


final_df = pd.DataFrame()


Run_adjustment = 100
# MRF, FB, FB + MRF, All

#df_locs = ["full-pop-10x-only_output_by_cycle_and_state_full.csv"]

# df_locs = [ "fb-and-med-risk-factor_output_by_cycle_and_state_full.csv" ]
df_locs = [ "med-risk-factor_output_by_cycle_and_state_full.csv", "fb_output_by_cycle_and_state_full.csv", "fb-and-med-risk-factor_output_by_cycle_and_state_full.csv", "full-pop_output_by_cycle_and_state_full.csv" ]


for df_loc in df_locs:

  df = pd.read_csv("go/tmp/cycle_state/remotes-oct-16/" + df_loc)
  # df = pd.read_csv("go/tmp/cycle_state/remotes-jun-26/" + df_loc)

  # remove calib data
  df = df[df.Year > 2016]
  print "CALIB DATA REMOVED"

  # initial processing
  df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
  df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
  df["Average life expectancy, months"] = df["Months_life_remaining_total"] / df.Population
  df["Expected total active cases"] = df["Months_life_remaining_total"] * df["Risk_of_prog_total"] / df.Population
  intervention_ids = pd.unique(df.Intervention_id)

  df["Elim"] = (df["Population"] * Run_adjustment) / 1000000
  df["PreElim"] = (df["Population"] * Run_adjustment) / 100000


  in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
  fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
  active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
  testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]



  intervention_names = []
  for intervention_id in intervention_ids:
    intervention_names.append(pd.unique(df[df.Intervention_id == intervention_id].Intervention_name)[0])


  results_df = pd.DataFrame(index=[i for i in intervention_names])

  fr = pd.DataFrame(index=[i for i in intervention_names])


  for intervention_id in intervention_ids:

    intervention_name = intervention_names[intervention_id]

    bdf = df[(df.Intervention_id == 0)]
    ldf = df[(df.Intervention_id == intervention_id)]

    # embed()

    # Treatment costs
    results_df.loc[intervention_name, "true_positive_treatment_costs_base"] = ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "true_positive_treatment_costs_low"] =  ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "true_positive_treatment_costs_high"] = ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

    # FP Treatment costs
    results_df.loc[intervention_name, "false_positive_treatment_costs_base"] = ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "false_positive_treatment_costs_low"] =  ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "false_positive_treatment_costs_high"] = ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment


    # Testing costs
    results_df.loc[intervention_name, "testing_costs_base"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "testing_costs_low"] =  ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "testing_costs_high"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

    # Total tests administered
    results_df.loc[intervention_name, "tests_administered_base"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Population.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "tests_administered_low"] =  ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Population.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "tests_administered_high"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Population.sum().max() * Run_adjustment

    # Active disease costs
    results_df.loc[intervention_name, "active_disease_costs_base"] = ldf[ldf.State_name.isin(active_disease_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "active_disease_costs_low"] =  ldf[ldf.State_name.isin(active_disease_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "active_disease_costs_high"] = ldf[ldf.State_name.isin(active_disease_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

    # Total costs
    results_df.loc[intervention_name, "total_costs_base"] = ldf.groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "total_costs_low"] =  ldf.groupby("Iteration_num").Costs.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "total_costs_high"] = ldf.groupby("Iteration_num").Costs.sum().max() * Run_adjustment

    # Total active TB cases
    results_df.loc[intervention_name, "active_cases_m2_base"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment
    results_df.loc[intervention_name, "active_cases_m2_low"] =  ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().min() * Run_adjustment
    results_df.loc[intervention_name, "active_cases_m2_high"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().max() * Run_adjustment

    # Cost compared to control
    results_df.loc[intervention_name, "cost_compared_to_control"] =  results_df.loc[intervention_name, "total_costs_base"] - results_df.loc["Basecase", "total_costs_base"] 

    # Active cases averted
    results_df.loc[intervention_name, "active_cases_averted"] =  results_df.loc["Basecase", "active_cases_m2_base"] - results_df.loc[intervention_name, "active_cases_m2_base"] 

    # Cost per averted case
    results_df.loc[intervention_name, "cost_per_case_averted"] =  results_df.loc[intervention_name, "cost_compared_to_control"] / results_df.loc[intervention_name, "active_cases_averted"]

    # Percent reduction in annual case count by 2035
    l_active_cases_in_2035 = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
    b_active_cases_in_2035 = bdf[(bdf.State_name == "Life") & (bdf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
    results_df.loc[intervention_name, "Percent reduction in annual case count by 2035"] = 1.0 - (l_active_cases_in_2035 / b_active_cases_in_2035)

    # Percent reduction in annual case count by 2050
    l_active_cases_in_2050 = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
    b_active_cases_in_2050 = bdf[(bdf.State_name == "Life") & (bdf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
    results_df.loc[intervention_name, "Percent reduction in annual case count by 2050"] = 1.0 - (l_active_cases_in_2050 / b_active_cases_in_2050)

    # % of simulations meeting PE by 2035
    pre_elim_cuttoff = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].PreElim.mean()
    tmp = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum() * Run_adjustment
    tmp = tmp.to_frame()
    results_df.loc[intervention_name, "Percent of simulations meeting PE by 2035"] = float(tmp[tmp.Risk_of_prog_total <= pre_elim_cuttoff].count() / tmp.count())

    # % of simulations meeting E by 2050
    elim_cuttoff = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].Elim.mean()
    tmp = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum() * Run_adjustment
    tmp = tmp.to_frame()
    results_df.loc[intervention_name, "Percent of simulations meeting E by 2050"] = float(tmp[tmp.Risk_of_prog_total <= elim_cuttoff].count() / tmp.count())

    # Average year of pre-elimination

    lmin  = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.PreElim)].groupby("Iteration_num").Year.min().min())
    lmean  = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.PreElim)].groupby("Iteration_num").Year.min().mean())
    lmax  = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.PreElim)].groupby("Iteration_num").Year.min().max())

    results_df.loc[intervention_name, "Year of pre-elimination, min"] =  " - " if np.isnan(lmin) else lmin
    results_df.loc[intervention_name, "Year of pre-elimination, mean"] = " - " if np.isnan(lmean) else lmean
    results_df.loc[intervention_name, "Year of pre-elimination, max"] =  " - " if np.isnan(lmax) else lmax

    # Average year of elimination

    lmin = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.Elim)].groupby("Iteration_num").Year.min().min())
    lmean = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.Elim)].groupby("Iteration_num").Year.min().mean())
    lmax = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.Elim)].groupby("Iteration_num").Year.min().max())

    results_df.loc[intervention_name, "Year of elimination, min"] =  " - " if np.isnan(lmin) else lmin
    results_df.loc[intervention_name, "Year of elimination, mean"] = " - " if np.isnan(lmean) else lmean
    results_df.loc[intervention_name, "Year of elimination, max"] =  " - " if np.isnan(lmax) else lmax


    fr.loc[intervention_name, "Total tests administered"] = results_df.loc[intervention_name, "tests_administered_base"]
    fr.loc[intervention_name, "Testing costs (m)"] = results_df.loc[intervention_name, "testing_costs_base"] / 1000000.0
    fr.loc[intervention_name, "LTBI treatment costs (m)"] = (results_df.loc[intervention_name, "true_positive_treatment_costs_base"] + results_df.loc[intervention_name, "false_positive_treatment_costs_base"])/ 1000000.0
    fr.loc[intervention_name, "Active disease costs (m)"] = results_df.loc[intervention_name, "active_disease_costs_base"]/ 1000000.0
    fr.loc[intervention_name, "All TB-related costs (m)"] = results_df.loc[intervention_name, "total_costs_base"]/ 1000000.0
    fr.loc[intervention_name, "All TB-related costs* (m)"] = results_df.loc[intervention_name, "cost_compared_to_control"]/ 1000000.0
    fr.loc[intervention_name, "Cases of TB"] = results_df.loc[intervention_name, "active_cases_m2_base"]
    fr.loc[intervention_name, "Cases of TB averted*"] = results_df.loc[intervention_name, "active_cases_averted"]
    fr.loc[intervention_name, "Cost per case averted*"] = results_df.loc[intervention_name, "cost_per_case_averted"]
    fr.loc[intervention_name, "Percent reduction by 2035"] = results_df.loc[intervention_name, "Percent reduction in annual case count by 2035"]
    fr.loc[intervention_name, "Percent reduction by 2050"] = results_df.loc[intervention_name, "Percent reduction in annual case count by 2050"]
    fr.loc[intervention_name, "Year of PE"] = results_df.loc[intervention_name, "Year of pre-elimination, mean"]
    fr.loc[intervention_name, "Year of E"] = results_df.loc[intervention_name, "Year of elimination, mean"]

  # formatting
    fr.loc[intervention_name, "Total tests administered"] = fmtr(fr.loc[intervention_name, "Total tests administered"])
    fr.loc[intervention_name, "Testing costs (m)"] = fmtr(fr.loc[intervention_name, "Testing costs (m)"])
    fr.loc[intervention_name, "LTBI treatment costs (m)"] = fmtr(fr.loc[intervention_name, "LTBI treatment costs (m)"])
    fr.loc[intervention_name, "Active disease costs (m)"] = fmtr(fr.loc[intervention_name, "Active disease costs (m)"])
    fr.loc[intervention_name, "All TB-related costs (m)"] = fmtr(fr.loc[intervention_name, "All TB-related costs (m)"])
    fr.loc[intervention_name, "All TB-related costs* (m)"] = fmtr(fr.loc[intervention_name, "All TB-related costs* (m)"])
    fr.loc[intervention_name, "Cases of TB"] = fmtr(fr.loc[intervention_name, "Cases of TB"])
    fr.loc[intervention_name, "Cases of TB averted*"] = fmtr(fr.loc[intervention_name, "Cases of TB averted*"])
    fr.loc[intervention_name, "Cost per case averted*"] = fmtr(fr.loc[intervention_name, "Cost per case averted*"])
    fr.loc[intervention_name, "Percent reduction by 2035"] = fmtr(fr.loc[intervention_name, "Percent reduction by 2035"])
    fr.loc[intervention_name, "Percent reduction by 2050"] = fmtr(fr.loc[intervention_name, "Percent reduction by 2050"])
    fr.loc[intervention_name, "Year of PE"] = fr.loc[intervention_name, "Year of PE"]
    fr.loc[intervention_name, "Year of E"] = fr.loc[intervention_name, "Year of E"]


    #embed()
  # results_df.to_csv("results_df_" + Output_name + ".csv")
  # fr.T.to_csv("fr_df_" + Output_name + ".csv")
  final_df = final_df.append(fr)


final_df.T.to_csv("final_df.csv")

print "Done"
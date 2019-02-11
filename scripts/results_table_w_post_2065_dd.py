
##################
# TO DO - analysis per iteration, then have distributions for all outputs
# can just take away min and max, and iteration over iteratons, save as you go
# and sort them out at the end, then at the end of all iterations, find the distrubtions


# results_table_w_post_2065.py:375: RuntimeWarning: invalid value encountered in double_scalars
#   results_df.loc[(iteration,intervention_name), "cost_per_case_averted_undiscounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_undiscounted"] / results_df.loc[(iteration,intervention_name), "active_cases_averted"]
# results_table_w_post_2065.py:384: RuntimeWarning: invalid value encountered in double_scalars
#   results_df.loc[(iteration,intervention_name), "cost_per_qaly_undiscounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_undiscounted"] / results_df.loc[(iteration,intervention_name), "qalys_saved_undiscounted_base"]
# results_table_w_post_2065.py:432: RuntimeWarning: invalid value encountered in double_scalars
#   results_df.loc[(iteration,intervention_name), "cost_per_case_averted_discounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_discounted"] / results_df.loc[(iteration,intervention_name), "active_cases_averted"]
# results_table_w_post_2065.py:435: RuntimeWarning: invalid value encountered in double_scalars
#   results_df.loc[(iteration,intervention_name), "cost_per_qaly_discounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_discounted"] / results_df.loc[(iteration,intervention_name), "qalys_saved_discounted_base"]


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
import scipy.stats as st
from IPython import embed

import tabulate
import yaml
import argparse

#connect to application
from app import * 


def low(a):
  return a.min()
  # return st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))[0]

def high(a):
  # return st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))[1]
  return a.max()

def mean(a):
  return a.mean()

def fmtrYear(v):
  return "{:.0f}".format(float(v))

def fmtr(v):
  if v > 10000000000: # if over 10 bill, 0 decmial point
    v = v/1000000000
    return "{:,.0f}b".format(float('%.3g' % v))
  if v > 1000000000: # if over 1 bill, 1 decmial point
    v = v/1000000000
    return "{:,.1f}b".format(float('%.3g' % v))
  if v > 100000000: # if over 100 mill, two decmial points
    v = v/1000000000
    return "{:,.2f}b".format(float('%.3g' % v))
  if v > 1000000:
    v = v/100000
    return "{:,.0f}m".format(float('%.3g' % v))
  if v > 1000:
    v = v/1000
    return "{:,.0f}k".format(float('%.3g' % v))
  if v >= 10:
    return "{:,.0f}".format(float('%.3g' % v))
  else:
    return "{:.2f}".format(float('%.2g' % v))


parser = argparse.ArgumentParser(description='s m l')
parser.add_argument("-n", "--name", type=str,
                    help="name of simulation")
args = parser.parse_args()
name = args.name

final_df = pd.DataFrame()
final_raw_df = pd.DataFrame()


Run_adjustment = 1000
# MRF, FB, FB + MRF, All

# df_locs = ["basecase_output_by_cycle_and_state_full.csv"]
#df_locs = ["full-pop-10x-only_output_by_cycle_and_state_full.csv"]

# df_locs = [ "fb-and-med-risk-factor_output_by_cycle_and_state_full.csv" ]
# df_locs = [ "med-risk-factor_output_by_cycle_and_state_full.csv", "fb_output_by_cycle_and_state_full.csv", "fb-and-med-risk-factor_output_by_cycle_and_state_full.csv", "full-pop_output_by_cycle_and_state_full.csv" ]
# df_locs = [ "med-risk-factor_output_by_cycle_and_state_full_psa_iter_1.csv", "fb_output_by_cycle_and_state_full_psa_iter_1.csv", "fb-and-med-risk-factor_output_by_cycle_and_state_full_psa_iter_1.csv", "full-pop_output_by_cycle_and_state_full_psa_iter_1.csv" ]
df_locs = [ "med-risk-factor-limited-master.csv", "fb-limited-master.csv", "fb-and-med-risk-factor-limited-master.csv", "full-pop-limited-master.csv" ]


for df_loc in df_locs:

  df = pd.read_csv("/hdd/share/" + name + "/masters/" + df_loc)

  # df = pd.read_csv("go/tmp/cycle_state/dec30best_guess/fb-limited-master.csv")

  # remove calib data
  df = df[df.Year > 2016]
  print "CALIB DATA REMOVED"

  # initial processing
  df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
  df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
  df["Average life expectancy, months"] = df["Months_life_remaining_total"] / df.Population
  df["Expected total active cases"] = df["Months_life_remaining_total"] * df["Risk_of_prog_total"] / df.Population

  intervention_ids = pd.unique(df.Intervention_id)

  secondary_cases_per_primary = 1.3 # decide if you want this!!
  qalys_lost_per_case_mrf = 1.1 # same for now
  qalys_lost_per_case_no_mrf = 1.7

  df["Active_disease_costs_discounted"] = 31400.0 * df["Risk_of_prog_total"] * 0.97 ** (df["Year"]-2017)
  df["Active_disease_costs_undiscounted"] = 31400.0 * df["Risk_of_prog_total"]

  df["Qalys_lost"] =  0
  df.loc[(df.State_name == "No medical risk factor"), "Qalys_lost"] = df[(df.State_name == "No medical risk factor")]["Risk_of_prog_total"] * qalys_lost_per_case_no_mrf
  df.loc[(df.State_name == "Medical risk factor"), "Qalys_lost"] = df[(df.State_name == "Medical risk factor")]["Risk_of_prog_total"] * qalys_lost_per_case_mrf 

  df["Qalys_lost_discounted"] =  df["Qalys_lost"] * 0.97 ** (df["Year"]-2017)

  df["DiscountedPopulation"] =  df["Population"] * 0.97 ** (df["Year"]-2017)
  df["Risk_of_prog_total_discounted"] = df["Risk_of_prog_total"] * 0.97 ** (df["Year"]-2017)


  df["Elim"] = (df["Population"] * Run_adjustment) / 1000000
  df["PreElim"] = (df["Population"] * Run_adjustment) / 100000

  df["Undiscounted_costs"] = 0
  df["Undiscounted_costs"] = df["Costs"] * 1/0.97 ** (df["Year"]-2017)


  # leavers 

  df["leaving_rate_usb"] = 0.001390 # see "QALYS saved from leaving ... worksheet"
  df["leaving_rate_fb"] = 0.001035 # see "QALYS saved from leaving ... worksheet"
  # df["left_cures"] = 21000000* df["leaving_rate_usb"] + 10000000 * df["leaving_rate_fb"]
  # df["left_cures"] = df["Population_us"]* df["leaving_rate_usb"]*Run_adjustment + df["Population_fb"] * df["leaving_rate_fb"]*Run_adjustment
  df["total_left_ca"] = df["Population_us"]* df["leaving_rate_usb"] * Run_adjustment + df["Population_fb"] * df["leaving_rate_fb"] * Run_adjustment

  # can't us this because consolidated version drops USB/FB distinction. Will assume fb leave rate.
  # KEEP 



  in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
  fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
  
  threeHpStates = [ 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3', "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3"]

  active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
  testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]



  intervention_names = []
  for intervention_id in intervention_ids:
    intervention_names.append(pd.unique(df[df.Intervention_id == intervention_id].Intervention_name)[0])

  iterations = np.unique(df.Iteration_num)

  arrays = [np.array([i for i in iterations]),np.array([i for i in intervention_names])]
  mindex = pd.MultiIndex.from_product(arrays, names=["iteration","intervention"])
  results_df = pd.DataFrame(index=mindex,columns=["hi"])


  fr = pd.DataFrame(index=[i for i in intervention_names])
  raw_df = pd.DataFrame(index=[i for i in intervention_names])


  for intervention_id in intervention_ids:
    for iteration in iterations:
      intervention_name = intervention_names[int(intervention_id)]
      print intervention_name
      print iteration

      bdf = df[(df.Intervention_id == 0) & (df.Iteration_num == iteration)]
      ldf = df[(df.Intervention_id == int(intervention_id)) & (df.Iteration_num == int(iteration))]

      # calculate end cases (post 2065, when simulation ends) - because of different life expectancies, needs to be done for MRF and non-MRF
      # embed()
      lastCycle = max(ldf.Cycle_id)

      # ---------------------- mrf
      
      # hanging cases (cases after 2065)
      months_remaining = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "Medical risk factor")].Months_life_remaining_total.mean()
      population = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "Medical risk factor")].Population.mean()
      age = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "Medical risk factor")].Age.mean() / population
      risk_of_prog_total = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "Medical risk factor")].Risk_of_prog_total.mean() # this is sum
      results_df.loc[(iteration,intervention_name), "hanging_cases_mrf_base"] = months_remaining * risk_of_prog_total/population * secondary_cases_per_primary

      # cost of hanging cases
      # for discount rates, see Jim's SS "CAPE TB adding CEA to elimination modeling some calculations v1"
      results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_mrf_discounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_mrf_base"] * 31400.00 * 0.170  # 0.170 is the discounting for mrf cases (occur sooner)
      results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_mrf_undiscounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_mrf_base"] * 31400.00 # 0.170 is the discounting for mrf cases (occur sooner)

      results_df.loc[(iteration,intervention_name), "qalys_lost_mrf_discounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_mrf_base"] * qalys_lost_per_case_mrf * 0.170  # 0.170 is the discounting for mrf cases (occur sooner)
      results_df.loc[(iteration,intervention_name), "qalys_lost_mrf_undiscounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_mrf_base"] * qalys_lost_per_case_mrf # 0.170 is the discounting for mrf cases (occur sooner)

      # ---------------------- no mrf
      months_remaining = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "No medical risk factor")].Months_life_remaining_total.mean()
      population = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "No medical risk factor")].Population.mean()
      age = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "No medical risk factor")].Age.mean() / population

      risk_of_prog_total = ldf[(ldf.Cycle_id == lastCycle) & (ldf.State_name == "No medical risk factor")].Risk_of_prog_total.mean()

      results_df.loc[(iteration,intervention_name), "hanging_cases_no_mrf_base"] = months_remaining * risk_of_prog_total/population * secondary_cases_per_primary

      results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_no_mrf_discounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_no_mrf_base"] * 31400.00 * 0.138 # 0.138 is the discounting for no mrf cases (occur later)
      results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_no_mrf_undiscounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_no_mrf_base"] * 31400.00 # 0.138 is the discounting for no mrf cases (occur later)

      results_df.loc[(iteration,intervention_name), "qalys_lost_no_mrf_discounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_no_mrf_base"] * qalys_lost_per_case_no_mrf * 0.138 
      results_df.loc[(iteration,intervention_name), "qalys_lost_no_mrf_undiscounted_base"] = results_df.loc[(iteration,intervention_name), "hanging_cases_no_mrf_base"] * qalys_lost_per_case_no_mrf

      # --------------------  all hanging cases
      results_df.loc[(iteration,intervention_name), "hanging_cases_total"] = (results_df.loc[(iteration,intervention_name), "hanging_cases_no_mrf_base"] + results_df.loc[(iteration,intervention_name), "hanging_cases_mrf_base"]) * Run_adjustment

      results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_discounted_total"] = (results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_mrf_discounted_base"] + results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_no_mrf_discounted_base"]) * Run_adjustment

      results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_undiscounted_total"] = (results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_mrf_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_no_mrf_undiscounted_base"]) * Run_adjustment

      # add mrf and no mrf QALYs for hanging cases
      results_df.loc[(iteration,intervention_name), "qalys_lost_hanging_cases_discounted_base"] = (results_df.loc[(iteration,intervention_name), "qalys_lost_no_mrf_discounted_base"] + results_df.loc[(iteration,intervention_name), "qalys_lost_mrf_discounted_base"]) * Run_adjustment
      results_df.loc[(iteration,intervention_name), "qalys_lost_hanging_cases_undiscounted_base"] = (results_df.loc[(iteration,intervention_name), "qalys_lost_no_mrf_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "qalys_lost_mrf_undiscounted_base"]) * Run_adjustment

      # Total tests administered
      results_df.loc[(iteration,intervention_name), "tests_administered_base"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Population.sum().mean() * Run_adjustment

      # adverse events - note: always discounted with current set up.
      results_df.loc[(iteration,intervention_name), "total_months_3hp_dc"] = ldf[ldf.State_name.isin(threeHpStates)].groupby("Iteration_num").DiscountedPopulation.sum().mean() * Run_adjustment
      results_df.loc[(iteration,intervention_name), "episodes_dih_dc"] = results_df.loc[(iteration,intervention_name), "total_months_3hp_dc"]/3.0 * 0.003 # Sterling NEJM 2011
      results_df.loc[(iteration,intervention_name), "dih_fatalities_dc"] = results_df.loc[(iteration,intervention_name), "episodes_dih_dc"] * 0.01 

      results_df.loc[(iteration,intervention_name), "morbidity_dih"] = results_df.loc[(iteration,intervention_name), "episodes_dih_dc"] * 0.15 # assume 1m x 0.85 hsu
      results_df.loc[(iteration,intervention_name), "mortality_dih"] = results_df.loc[(iteration,intervention_name), "dih_fatalities_dc"] * 30.0 # assume 30 qalys lost per death

      results_df.loc[(iteration,intervention_name), "qalys_lost_to_ae"] = results_df.loc[(iteration,intervention_name), "morbidity_dih"] + results_df.loc[(iteration,intervention_name), "mortality_dih"]

      # Active TB cases (stopping at 2065)
      results_df.loc[(iteration,intervention_name), "active_cases_m2_pre65_base"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment

      # Active cases in 2025
      results_df.loc[(iteration,intervention_name), "active_cases_in_2025"] = ldf[(ldf.State_name == "Life") & (ldf.Year == 2025)].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment

      # Active cases in 2065
      results_df.loc[(iteration,intervention_name), "active_cases_in_2065"] = ldf[(ldf.State_name == "Life") & (ldf.Year == 2065)].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment

      # Total active TB cases (plus hanging cases)
      results_df.loc[(iteration,intervention_name), "active_cases_m2_base_total"] = results_df.loc[(iteration,intervention_name), "active_cases_m2_pre65_base"] + results_df.loc[(iteration,intervention_name), "hanging_cases_total"] 

      # Total active TB cases discounted (plus hanging cases)
      results_df.loc[(iteration,intervention_name), "active_cases_m2_base_total_discounted"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total_discounted.sum().mean() * Run_adjustment + results_df.loc[(iteration,intervention_name), "hanging_cases_total"] * 0.218065375

      # Total QALYs lost

      results_df.loc[(iteration,intervention_name), "qalys_lost_discounted_base"] = ldf.groupby("Iteration_num").Qalys_lost_discounted.sum().mean() * Run_adjustment + results_df.loc[(iteration,intervention_name), "qalys_lost_hanging_cases_discounted_base"] + results_df.loc[(iteration,intervention_name), "qalys_lost_to_ae"]
       
      results_df.loc[(iteration,intervention_name), "qalys_lost_undiscounted_base"] = ldf.groupby("Iteration_num").Qalys_lost.sum().mean() * Run_adjustment + results_df.loc[(iteration,intervention_name), "qalys_lost_hanging_cases_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "qalys_lost_to_ae"]
       
      # Active cases averted compared to basecase (including hanging cases)
      results_df.loc[(iteration,intervention_name), "active_cases_averted"] =  results_df.loc[(iteration,"Basecase"), "active_cases_m2_base_total"] - results_df.loc[(iteration,intervention_name), "active_cases_m2_base_total"] 

      # Active cases averted compared to basecase (incremental)
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted"] =  results_df.loc[(iteration,intervention_names[intervention_id-1]), "active_cases_m2_base_total"] - results_df.loc[(iteration,intervention_name), "active_cases_m2_base_total"]

      # Active cases averted (discounted) (incremental)
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted_discounted"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted_discounted"] =  results_df.loc[(iteration,intervention_names[intervention_id-1]), "active_cases_m2_base_total_discounted"] - results_df.loc[(iteration,intervention_name), "active_cases_m2_base_total_discounted"]


      # Percent reduction in annual case count by 2035
      l_active_cases_in_2035 = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
      b_active_cases_in_2035 = bdf[(bdf.State_name == "Life") & (bdf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
      results_df.loc[(iteration,intervention_name), "Percent reduction in annual case count by 2035"] = 1.0 - (l_active_cases_in_2035 / b_active_cases_in_2035)

      # Percent reduction in annual case count by 2050
      l_active_cases_in_2050 = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
      b_active_cases_in_2050 = bdf[(bdf.State_name == "Life") & (bdf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum().mean()
      results_df.loc[(iteration,intervention_name), "Percent reduction in annual case count by 2050"] = 1.0 - (l_active_cases_in_2050 / b_active_cases_in_2050)

      # cases per M by 2035
      results_df.loc[(iteration,intervention_name), "Cases per M by 2035"] = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum() * 1000000 / ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Population.mean())

      # cases per M by 2050
      results_df.loc[(iteration,intervention_name), "Cases per M by 2050"] = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum() * 1000000 / ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Population.mean())


      # did meet pre-elimination by 2035
      total_case_count_2035 = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum()) * Run_adjustment
      pre_elim_cuttoff = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].PreElim.mean())
      if total_case_count_2035 < pre_elim_cuttoff:
        results_df.loc[(iteration,intervention_name), "Met pre-elimination by 2035"] = 1
      else:
        results_df.loc[(iteration,intervention_name), "Met pre-elimination by 2035"] = 0


      # did meet pre-elimination by 2065
      total_case_count_2065 = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2065)].groupby("Iteration_num").Risk_of_prog_total.sum()) * Run_adjustment
      pre_elim_cuttoff = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2065)].PreElim.mean())
      if total_case_count_2065 < pre_elim_cuttoff:
        results_df.loc[(iteration,intervention_name), "Met pre-elimination by 2065"] = 1
      else:
        results_df.loc[(iteration,intervention_name), "Met pre-elimination by 2065"] = 0


      # did meet elimination by 2050
      total_case_count_2050 = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum()) * Run_adjustment
      elim_cuttoff = float(ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].Elim.mean())
      if total_case_count_2050 < elim_cuttoff:
        results_df.loc[(iteration,intervention_name), "Met elimination by 2050"] = 1
      else:
        results_df.loc[(iteration,intervention_name), "Met elimination by 2050"] = 0


    # # % of simulations meeting PE by 2035
    # tmp = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum() * Run_adjustment
    # tmp = tmp.to_frame()
    # results_df.loc[(iteration,intervention_name), "Percent of simulations meeting PE by 2035"] = float(tmp[tmp.Risk_of_prog_total <= pre_elim_cuttoff].count() / tmp.count())

    # # % of simulations meeting E by 2050
    # tmp = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum() * Run_adjustment
    # tmp = tmp.to_frame()
    # results_df.loc[(iteration,intervention_name), "Percent of simulations meeting E by 2050"] = float(tmp[tmp.Risk_of_prog_total <= elim_cuttoff].count() / tmp.count())


      # # Average year of pre-elimination

      # lmin  = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.PreElim)].groupby("Iteration_num").Year.min().min())
      # lmean  = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.PreElim)].groupby("Iteration_num").Year.min().mean())
      # lmax  = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.PreElim)].groupby("Iteration_num").Year.min().max())

      # results_df.loc[(iteration,intervention_name), "Year of pre-elimination, min"] =  float('NaN') if np.isnan(lmin) else lmin
      # results_df.loc[(iteration,intervention_name), "Year of pre-elimination, mean"] = float('NaN') if np.isnan(lmean) else lmean
      # results_df.loc[(iteration,intervention_name), "Year of pre-elimination, max"] =  float('NaN') if np.isnan(lmax) else lmax

      # # Average year of elimination

      # lmin = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.Elim)].groupby("Iteration_num").Year.min().min())
      # lmean = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.Elim)].groupby("Iteration_num").Year.min().mean())
      # lmax = float(ldf[(ldf.State_name == "Life") & (ldf.Risk_of_prog_total * Run_adjustment * 12 <  ldf.Elim)].groupby("Iteration_num").Year.min().max())

      # results_df.loc[(iteration,intervention_name), "Year of elimination, min"] =  float('NaN') if np.isnan(lmin) else lmin
      # results_df.loc[(iteration,intervention_name), "Year of elimination, mean"] = float('NaN') if np.isnan(lmean) else lmean
      # results_df.loc[(iteration,intervention_name), "Year of elimination, max"] =  float('NaN') if np.isnan(lmax) else lmax

      # ================================================================== Costs

      # ============================== Undiscounted
      # Treatment costs
      results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_undiscounted_base"] = ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Undiscounted_costs.sum().mean() * Run_adjustment

      # FP Treatment costs
      results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_undiscounted_base"] = ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Undiscounted_costs.sum().mean() * Run_adjustment

      results_df.loc[(iteration,intervention_name), "total_treatment_costs_undiscounted_base"] = results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_undiscounted_base"]

      # Testing costs
      results_df.loc[(iteration,intervention_name), "testing_costs_undiscounted_base"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Undiscounted_costs.sum().mean() * Run_adjustment


      # Active disease costs -- todo add other post '65 active costs
      results_df.loc[(iteration,intervention_name), "active_disease_costs_undiscounted_base"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Active_disease_costs_undiscounted.sum().mean() * Run_adjustment + results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_undiscounted_total"]

      # Total costs - undiscounted
      results_df.loc[(iteration,intervention_name), "total_costs_undiscounted_base"] = results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "testing_costs_undiscounted_base"] + results_df.loc[(iteration,intervention_name), "active_disease_costs_undiscounted_base"]

      # Cost compared to control - undiscounted
      results_df.loc[(iteration,intervention_name), "cost_compared_to_control_undiscounted"] =  results_df.loc[(iteration,intervention_name), "total_costs_undiscounted_base"] - results_df.loc[(iteration,"Basecase"), "total_costs_undiscounted_base"] 

      # Cost, incremental
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_undiscounted"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_undiscounted"] = results_df.loc[(iteration,intervention_name), "total_costs_undiscounted_base"] - results_df.loc[(iteration,intervention_names[intervention_id-1]), "total_costs_undiscounted_base"] 

      # QALYs saved - undiscounted
      results_df.loc[(iteration,intervention_name), "qalys_saved_undiscounted_base"]=  results_df.loc[(iteration,"Basecase"), "qalys_lost_undiscounted_base"] - results_df.loc[(iteration,intervention_name), "qalys_lost_undiscounted_base"]

      # QALYs incremental - undiscounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_undiscounted_base"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_undiscounted_base"] = results_df.loc[(iteration,intervention_names[intervention_id-1]), "qalys_lost_undiscounted_base"]  -  results_df.loc[(iteration,intervention_name), "qalys_lost_undiscounted_base"]

      # Cost per averted case, undiscounted
      results_df.loc[(iteration,intervention_name), "cost_per_case_averted_undiscounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_undiscounted"] / results_df.loc[(iteration,intervention_name), "active_cases_averted"]

      # incremental Cost per averted case , undiscounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_case_averted_undiscounted"] =  0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_case_averted_undiscounted"] =  results_df.loc[(iteration,intervention_name), "incremental_cost_undiscounted"] / results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted"]

      # Cost per QALY saved, undiscounted
      results_df.loc[(iteration,intervention_name), "cost_per_qaly_undiscounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_undiscounted"] / results_df.loc[(iteration,intervention_name), "qalys_saved_undiscounted_base"]

      # incremental Cost per QALY saved, undiscounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_qaly_undiscounted"] =  0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_qaly_undiscounted"] =  results_df.loc[(iteration,intervention_name), "incremental_cost_undiscounted"] / results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_undiscounted_base"]

      # --- leavers


      results_df.loc[(iteration,intervention_name), "qalys_saved_outside_ca_undiscounted"] =  ldf[(ldf.State_name == 'LTBI treated with RTP') & (ldf.Intervention_name == intervention_name)].total_left_ca.sum() * 0.0411 # see "QALYs saved from individuals outside ca" worksheet

      results_df.loc[(iteration,intervention_name), "cost_saved_from_cases_averted_outside_ca_undiscounted"] =  ldf[(ldf.State_name == 'LTBI treated with RTP') & (ldf.Intervention_name == intervention_name)].total_left_ca.sum() * 940.57 # see "QALYs saved from individuals outside ca" worksheet

      # if intervention_name == "2x in FB (QFT/3HP)":
        # embed()
        
      # ====================== Discounted

      # Treatment costs
      results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_discounted_base"] = ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment

      # FP Treatment costs
      results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_discounted_base"] = ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment

      results_df.loc[(iteration,intervention_name), "total_treatment_costs_discounted_base"] = results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_discounted_base"] 

      # Testing costs
      results_df.loc[(iteration,intervention_name), "testing_costs_discounted_base"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment


      # Active disease costs -- todo add other post '65 active costs
      results_df.loc[(iteration,intervention_name), "active_disease_costs_discounted_base"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Active_disease_costs_discounted.sum().mean() * Run_adjustment + results_df.loc[(iteration,intervention_name), "cost_of_hanging_cases_discounted_total"]

      # Total costs - discounted
      results_df.loc[(iteration,intervention_name), "total_costs_discounted_base"] = results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "testing_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "active_disease_costs_discounted_base"]

      # Cost compared to control - discounted
      results_df.loc[(iteration,intervention_name), "cost_compared_to_control_discounted"] =  results_df.loc[(iteration,intervention_name), "total_costs_discounted_base"] - results_df.loc[(iteration,"Basecase"), "total_costs_discounted_base"] 

      # Incremental cost, discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] = results_df.loc[(iteration,intervention_name), "total_costs_discounted_base"] - results_df.loc[(iteration,intervention_names[intervention_id-1]), "total_costs_discounted_base"] 


      # QALYs saved - discounted
      results_df.loc[(iteration,intervention_name), "qalys_saved_discounted_base"]=  results_df.loc[(iteration,"Basecase"), "qalys_lost_discounted_base"] - results_df.loc[(iteration,intervention_name), "qalys_lost_discounted_base"]

      # Cost per averted case, discounted
      results_df.loc[(iteration,intervention_name), "cost_per_case_averted_discounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_discounted"] / results_df.loc[(iteration,intervention_name), "active_cases_averted"]

      # Cost per QALY saved, discounted
      results_df.loc[(iteration,intervention_name), "cost_per_qaly_discounted"] =  results_df.loc[(iteration,intervention_name), "cost_compared_to_control_discounted"] / results_df.loc[(iteration,intervention_name), "qalys_saved_discounted_base"]

      # --- leavers

      results_df.loc[(iteration,intervention_name), "qalys_saved_outside_ca_discounted"] =  ldf[(ldf.State_name == 'LTBI treated with RTP') & (ldf.Intervention_name == intervention_name)].total_left_ca.sum() * 0.0142   # see "QALYs saved from individuals outside ca" worksheet, updated 10/10/17

      results_df.loc[(iteration,intervention_name), "cost_saved_from_cases_averted_outside_ca_discounted"] =  ldf[(ldf.State_name == 'LTBI treated with RTP') & (ldf.Intervention_name == intervention_name)].total_left_ca.sum() * 350.122 # see "QALYs saved from individuals outside ca" worksheet

      # -----------------------
      # Cost, incremental, discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] = results_df.loc[(iteration,intervention_name), "total_costs_discounted_base"] - results_df.loc[(iteration,intervention_names[intervention_id-1]), "total_costs_discounted_base"] 

      # QALYs incremental - discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_discounted_base"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_discounted_base"] = results_df.loc[(iteration,intervention_names[intervention_id-1]), "qalys_lost_discounted_base"]  -  results_df.loc[(iteration,intervention_name), "qalys_lost_discounted_base"]

      # incremental Cost per averted case , discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_case_averted_discounted"] =  0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_case_averted_discounted"] =  results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] / results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted"]

      # incremental Cost per averted case , discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_case_averted_discounted_both"] =  0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_case_averted_discounted_both"] =  results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] / results_df.loc[(iteration,intervention_name), "incremental_active_cases_averted_discounted"]


      # incremental Cost per QALY saved, discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_qaly_discounted"] =  0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_qaly_discounted"] =  results_df.loc[(iteration,intervention_name), "incremental_cost_discounted"] / results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_discounted_base"]


      # --- leavers sub analysis

      results_df.loc[(iteration,intervention_name), "total_left_post_tx"] =  ldf[(ldf.State_name == 'LTBI treated with RTP') & (ldf.Intervention_name == intervention_name)].total_left_ca.sum()

    
      # Total QALYs, discounted, w leavers
      results_df.loc[(iteration,intervention_name), "qalys_lost_discounted_base_w_leavers"] = results_df.loc[(iteration,intervention_name), "qalys_lost_discounted_base"] - results_df.loc[(iteration,intervention_name), "qalys_saved_outside_ca_discounted"]


      # Total costs - discounted w leavers
      results_df.loc[(iteration,intervention_name), "total_costs_discounted_base_w_leavers"] = results_df.loc[(iteration,intervention_name), "true_positive_treatment_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "false_positive_treatment_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "testing_costs_discounted_base"] + results_df.loc[(iteration,intervention_name), "active_disease_costs_discounted_base"] - results_df.loc[(iteration,intervention_name), "cost_saved_from_cases_averted_outside_ca_discounted"]

      # Incremental cost, discounted, w leavers
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_discounted_w_leavers"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_discounted_w_leavers"] = results_df.loc[(iteration,intervention_name), "total_costs_discounted_base_w_leavers"] - results_df.loc[(iteration,intervention_names[intervention_id-1]), "total_costs_discounted_base_w_leavers"] 

      # QALYs incremental - discounted
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_discounted_base_w_leavers"] = 0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_discounted_base_w_leavers"] = results_df.loc[(iteration,intervention_names[intervention_id-1]), "qalys_lost_discounted_base_w_leavers"]  -  results_df.loc[(iteration,intervention_name), "qalys_lost_discounted_base_w_leavers"]

      # incremental cost per QALY, discounted, w leavers
      if intervention_name == "Basecase":
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_qaly_discounted_w_leavers"] =  0
      else:
        results_df.loc[(iteration,intervention_name), "incremental_cost_per_qaly_discounted_w_leavers"] =  results_df.loc[(iteration,intervention_name), "incremental_cost_discounted_w_leavers"] / results_df.loc[(iteration,intervention_name), "incremental_qalys_saved_discounted_base_w_leavers"]

    # for each intervention 

    #not costs
    pdf = results_df.reset_index()





    # # % of simulations meeting PE by 2035
    # pre_elim_cuttoff = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].PreElim.mean()
    # tmp = ldf[(ldf.State_name == "Life") & (ldf.Year == 2035)].groupby("Iteration_num").Risk_of_prog_total.sum() * Run_adjustment
    # tmp = tmp.to_frame()
    # results_df.loc[(iteration,intervention_name), "Percent of simulations meeting PE by 2035"] = float(tmp[tmp.Risk_of_prog_total <= pre_elim_cuttoff].count() / tmp.count())

    # # % of simulations meeting E by 2050
    # elim_cuttoff = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].Elim.mean()
    # tmp = ldf[(ldf.State_name == "Life") & (ldf.Year == 2050)].groupby("Iteration_num").Risk_of_prog_total.sum() * Run_adjustment
    # tmp = tmp.to_frame()
    # results_df.loc[(iteration,intervention_name), "Percent of simulations meeting E by 2050"] = float(tmp[tmp.Risk_of_prog_total <= elim_cuttoff].count() / tmp.count())


    outputs_dict = [{ "label": "Total tests administered", "value": "tests_administered_base" },
    { "label": "QALYs lost to TB, discounted", "value" : "qalys_lost_discounted_base" },
    { "label": "QALYs lost to TB, undiscounted", "value" : "qalys_lost_undiscounted_base" },
    { "label": "Cases of TB", "value" : "active_cases_m2_base_total" },
    { "label": "Cases of TB before 2065", "value" : "active_cases_m2_pre65_base" },
    { "label": "Cases of TB averted*", "value" : "active_cases_averted" },
    { "label": "Percent reduction by 2035", "value" : "Percent reduction in annual case count by 2035" },
    { "label": "Percent reduction by 2050", "value" : "Percent reduction in annual case count by 2050" },
    { "label": "Cases per M by 2035", "value" : "Cases per M by 2035" },
    { "label": "Cases per M by 2050", "value" : "Cases per M by 2050" },
    { "label": "active_cases_in_2025", "value" : "active_cases_in_2025"}, 
    { "label": "active_cases_in_2065", "value" :"active_cases_in_2065"},
    # { "label": "Year of PE", "value" : "Year of pre-elimination, mean" },
    # { "label": "Year of E", "value" : "Year of elimination, mean" },
    { "label": "QALYs saved, undiscounted", "value" : "qalys_saved_undiscounted_base" },
    { "label": "QALYs saved, discounted", "value" : "qalys_saved_discounted_base" },
    { "label": "Testing costs (m), undiscounted", "value" : "testing_costs_undiscounted_base" },
    { "label": "LTBI treatment costs (m), undiscounted", "value" : "total_treatment_costs_undiscounted_base" },
    { "label": "Active disease costs (m), undiscounted", "value" : "active_disease_costs_undiscounted_base" },
    { "label": "Total costs, undiscounted", "value" : "total_costs_undiscounted_base" },
    { "label": "All TB-related costs (m) compared to baseline, undiscounted", "value" : "cost_compared_to_control_undiscounted" },
    { "label": "Cost per case averted, undiscounted", "value" : "cost_per_case_averted_undiscounted" },
    { "label": "Cost per QALY saved, undiscounted", "value" : "cost_per_qaly_undiscounted" },
    { "label": "Testing costs (m), discounted", "value" : "testing_costs_discounted_base" },
    { "label": "LTBI treatment costs (m), discounted", "value" : "total_treatment_costs_discounted_base" },
    { "label": "Active disease costs (m), discounted", "value" : "active_disease_costs_discounted_base" },
    { "label": "Total costs, discounted", "value" : "total_costs_discounted_base" },
    { "label": "All TB-related costs (m) compared to baseline, discounted", "value" : "cost_compared_to_control_discounted" },
    { "label": "Cost per case averted, discounted", "value" : "cost_per_case_averted_discounted" },
    { "label": "QALYs lost to AE", "value" : "qalys_lost_to_ae" },
    { "label": "Cost per QALY saved, discounted", "value" : "cost_per_qaly_discounted" },
    { "label": "incremental_active_cases_averted", "value" : "incremental_active_cases_averted" },
    { "label": "incremental_cost_undiscounted", "value" : "incremental_cost_undiscounted" },
    { "label": "incremental_cost_discounted", "value" : "incremental_cost_discounted" },
    { "label": "incremental_qalys_saved_undiscounted_base", "value" : "incremental_qalys_saved_undiscounted_base" },
    { "label": "incremental_cost_per_case_averted_undiscounted", "value" : "incremental_cost_per_case_averted_undiscounted" },
    { "label": "incremental_cost_per_qaly_undiscounted", "value" : "incremental_cost_per_qaly_undiscounted" },
    { "label": "incremental_cost_discounted", "value" : "incremental_cost_discounted" },
    { "label": "incremental_qalys_saved_discounted_base", "value" : "incremental_qalys_saved_discounted_base" },
    { "label": "incremental_cost_per_case_averted_discounted", "value" : "incremental_cost_per_case_averted_discounted" },
    { "label": "incremental_cost_per_qaly_discounted", "value" : "incremental_cost_per_qaly_discounted" },
    
    { "label": "qalys_lost_discounted_base_w_leavers", "value" : "qalys_lost_discounted_base_w_leavers" },
    { "label": "total_costs_discounted_base_w_leavers", "value" : "total_costs_discounted_base_w_leavers" },
    { "label": "incremental_cost_discounted_w_leavers", "value" : "incremental_cost_discounted_w_leavers" },
    { "label": "incremental_qalys_saved_discounted_base_w_leavers", "value" : "incremental_qalys_saved_discounted_base_w_leavers" },
    { "label": "incremental_cost_per_qaly_discounted_w_leavers", "value" : "incremental_cost_per_qaly_discounted_w_leavers" },

    { "label": "qalys_saved_outside_ca_undiscounted", "value" : "qalys_saved_outside_ca_undiscounted" },
    { "label": "cost_saved_from_cases_averted_outside_ca_undiscounted", "value" : "cost_saved_from_cases_averted_outside_ca_undiscounted" },
    { "label": "qalys_saved_outside_ca_discounted", "value" : "qalys_saved_outside_ca_discounted" },
    { "label": "cost_saved_from_cases_averted_outside_ca_discounted", "value" : "cost_saved_from_cases_averted_outside_ca_discounted" },
    { "label": "incremental_cost_per_case_averted_discounted_both", "value" : "incremental_cost_per_case_averted_discounted_both" },
    { "label": "active_cases_m2_base_total_discounted", "value" : "active_cases_m2_base_total_discounted" },
    { "label": "hanging_cases_total", "value" : "hanging_cases_total" },
    { "label": "total_left_post_tx", "value" : "total_left_post_tx" }

  ]


    for output in outputs_dict:
      print output["label"]
      if output["label"] == "Year of PE" or output["label"] == "Year of E":
        fr.loc[intervention_name, output["label"]] = fmtrYear(mean(pdf[pdf.intervention == intervention_name][output["value"]])) + " (" + fmtrYear(low(pdf[pdf.intervention == intervention_name][output["value"]])) + " - " + fmtrYear(high(pdf[pdf.intervention == intervention_name][output["value"]])) + ")"
      else:
        fr.loc[intervention_name, output["label"]] = fmtr(mean(pdf[pdf.intervention == intervention_name][output["value"]])) + " (" + fmtr(low(pdf[pdf.intervention == intervention_name][output["value"]])) + " - " + fmtr(high(pdf[pdf.intervention == intervention_name][output["value"]])) + ")"

      raw_df.loc[intervention_name, output["label"] + ", mean"] = mean(pdf[pdf.intervention == intervention_name][output["value"]])
      raw_df.loc[intervention_name, output["label"] + ", low"] = low(pdf[pdf.intervention == intervention_name][output["value"]])
      raw_df.loc[intervention_name, output["label"] + ", high"] = high(pdf[pdf.intervention == intervention_name][output["value"]])




    # % meeting thersholds
    total_runs = pdf[pdf.intervention == intervention_name].iteration.count()
    num_met_pre_elim_35 = pdf[(pdf.intervention == intervention_name) & (pdf["Met pre-elimination by 2035"] == 1)].iteration.count()
    num_met_pre_elim_65 = pdf[(pdf.intervention == intervention_name) & (pdf["Met pre-elimination by 2065"] == 1)].iteration.count()
    num_met_elim = pdf[(pdf.intervention == intervention_name) & (pdf["Met elimination by 2050"] == 1)].iteration.count()
    fr.loc[intervention_name, "% met pre-elimination by 2035"] = float(num_met_pre_elim_35) / float(total_runs)
    fr.loc[intervention_name, "% met pre-elimination by 2065"] = float(num_met_pre_elim_65) / float(total_runs)
    fr.loc[intervention_name, "% met elimination by 2050"] = float(num_met_elim) / float(total_runs)
    print ">>>>>>>>>>>>>>>>>>> # met pre-elimination by 2065 {}".format(num_met_pre_elim_65) 

  final_df = final_df.append(fr)
  final_raw_df = final_raw_df.append(raw_df)

final_df.T.to_csv("/hdd/share/" + name + "/results/final_df_" + time.strftime("%Y-%m-%d-%Hh%Mm") + ".csv")
final_raw_df.to_csv("/hdd/share/" + name + "/results/final_raw_df_" + time.strftime("%Y-%m-%d-%Hh%Mm") + ".csv")


print "Done"

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


# from IPython.display import Image
# For later visualizaton scripts

import os
import pandas as pd
import numpy as np
import argparse


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


fdf_final = pd.DataFrame()


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



  arrays = [np.array([i for i in intervention_names]),np.array([i for i in range(2017,2066)])]
  mindex = pd.MultiIndex.from_product(arrays, names=["intervention","year"])
  fdf = pd.DataFrame(index=mindex,columns=["value"])

  for intervention_id in intervention_ids:
    for iteration in iterations:
      intervention_name = intervention_names[int(intervention_id)]
      print intervention_name
      print iteration

      bdf = df[(df.Intervention_id == 0) & (df.Iteration_num == iteration)]
      ldf = df[(df.Intervention_id == int(intervention_id)) & (df.Iteration_num == int(iteration))]

      for year in range(2017,2066):
        fdf.loc[intervention_name,year] = ldf[(ldf.State_name == "Life") * (ldf.Year == year)].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment

  fdf_final = fdf_final.append(fdf)


fdf_final.to_csv("/hdd/share/" + name + "/results/by_year.csv")

print "Done"
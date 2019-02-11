
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


df_locs = ["fb-limited-master.csv"]


for df_loc in df_locs:

  df = pd.read_csv("/hdd/share/" + name + "/masters/" + df_loc)

  # df = pd.read_csv("go/tmp/cycle_state/dec30best_guess/fb-limited-master.csv")

  # limited to basecase and 2x
  df = df[(df.Intervention_id == 0) | (df.Intervention_id == 1)]
  
  # limited to first 50
  ids_for_analysis = pd.unique(df.Iteration_num)[:50]
  df = df[df.Iteration_num.isin(ids_for_analysis)]
  # embed()
  df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
  # remove calib data
  print "CALIB DATA NOT REMOVED"

  intervention_ids = pd.unique(df.Intervention_id)

  # leavers 

  in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
  fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
  
  threeHpStates = [ 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3', "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3"]

  active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
  testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]

  uninfected_states = ["Uninfected TB", "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]

  bdf = df[df.Intervention_id == 0]


  years = range(2001,2020)
  for yoi in years:
    coi = bdf[bdf.Year == yoi].Cycle_id.min()
    fast_latent_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Fast latent")].Population.mean() * Run_adjustment
    print "{}: {}".format(yoi, fast_latent_pop)

  embed()

  # FB LTBI Prevalence 
  # ----------------------------------------------------------------------------------------

  # For 2004
  yoi = 2004 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)


  total_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  number_no_ltbi = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Uninfected TB")].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
  number_ltbi = total_pop - number_no_ltbi

  print "Percent FB latent (includes all) in 2004: "
  print number_ltbi / total_pop

  # For 2018
  yoi = 2018 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)

  total_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
  number_no_ltbi = bdf[(bdf.Cycle_id == coi) & (bdf.State_name.isin(uninfected_states))].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
  number_ltbi = total_pop - number_no_ltbi

  print "Percent FB latent (includes all) in 2018: "
  print number_ltbi / total_pop


  # ------------- exlcusively "fast latent" and "slow latent" states

  yoi = 2004 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)

  total_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  number_ltbi = bdf[(bdf.Cycle_id == coi) & ((bdf.State_name == "Fast latent") | (bdf.State_name == "Slow latent"))].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
  

  print "Percent FB latent (includes just fast and slow latent) in 2004: "
  print number_ltbi / total_pop

  # For 2018
  yoi = 2018 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)

  total_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  number_ltbi = bdf[(bdf.Cycle_id == coi) & ((bdf.State_name == "Fast latent") | (bdf.State_name == "Slow latent"))].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment

  print "Percent FB latent (includes just fast and slow latent) in 2018: "
  print number_ltbi / total_pop







  # Proportion of FB LTBI positive in 2018 who are in fast latent states -- notes includes IMPORTED
  # ----------------------------------------------------------------------------------------
 
  yoi = 2018 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)

  fast_latent_states = [ "Fast latent", "Less than one year"]

  total_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  number_no_ltbi = bdf[(bdf.Cycle_id == coi) & (bdf.State_name.isin(uninfected_states))].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
  number_ltbi = total_pop - number_no_ltbi
  fast_latent_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name.isin(fast_latent_states))].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment

  print "Proportion of FB LTBI positive in 2018 who are in fast latent states (or 'imported')"
  print fast_latent_pop / number_ltbi

  # Population sizes FB and USB, 2004, 2013, 2030
  # ----------------------------------------------------------------------------------------

  yoi = 2004 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  usb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_us.mean() * Run_adjustment
  fb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  print "Population " + str(yoi) + " FB {} USB {}".format(fb_pop, usb_pop)

  yoi = 2013 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  usb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_us.mean() * Run_adjustment
  fb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  print "Population " + str(yoi) + " FB {} USB {}".format(fb_pop, usb_pop)


  yoi = 2030 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  usb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_us.mean() * Run_adjustment
  fb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment
  print "Population " + str(yoi) + " FB {} USB {}".format(fb_pop, usb_pop)

  # Proportion of active cases due to recent transmission, 2004, 2018
  # ----------------------------------------------------------------------------------------

  yoi = 2004 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  total_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Risk_of_prog_total.mean() * Run_adjustment * 12
  cases_recent_fb = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Recent_transmission_fb_rop.mean() * Run_adjustment * 12
  cases_recent_usb = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Recent_transmission_us_rop.mean() * Run_adjustment * 12
  total_cases_recent = cases_recent_fb + cases_recent_usb
  prop_recent = total_cases_recent / total_cases
  print "Proportion recent cases (fast latent only, not imported) {}: {}".format(yoi, prop_recent)

  yoi = 2014 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  total_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Risk_of_prog_total.mean() * Run_adjustment * 12
  cases_recent_fb = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Recent_transmission_fb_rop.mean() * Run_adjustment * 12
  cases_recent_usb = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Recent_transmission_us_rop.mean() * Run_adjustment * 12
  total_cases_recent = cases_recent_fb + cases_recent_usb
  prop_recent = total_cases_recent / total_cases
  print "Proportion recent cases  (fast latent only, not imported) {}: {}".format(yoi, prop_recent)



  yoi = 2018 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  total_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Risk_of_prog_total.mean() * Run_adjustment * 12
  cases_recent_fb = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Recent_transmission_fb_rop.mean() * Run_adjustment * 12
  cases_recent_usb = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Recent_transmission_us_rop.mean() * Run_adjustment * 12
  total_cases_recent = cases_recent_fb + cases_recent_usb
  prop_recent = total_cases_recent / total_cases
  print "Proportion recent cases  (fast latent only, not imported) {}: {}".format(yoi, prop_recent)


  # Number of tests administered to HCW, 2004-2065
  # ----------------------------------------------------------------------------------------

  hcw_tests = bdf[(bdf.Year > 2003) & (bdf.State_name.isin(testing_states))].groupby("Iteration_num").HCW_in_state.sum().mean() * Run_adjustment
  print "Number of tests adminsitered to  HCWs, 2004-2065, basecase: {}".format(hcw_tests)

  # Historical active TB cases total and by MRF, and by FB vs USB  (2004 to 2014, inclusive)
  # ----------------------------------------------------------------------------------------

  print "Historical active TB cases total and by MRF, and by FB vs USB  (2004 to 2014, inclusive)"

  nativties = [ "FB", "USB" ]
  groupings = [ "Life", "Smoker", "ESRD", "Diabetes", "HIV" ]
  hiv_states = ['Infected HIV, no ART', 'Infected HIV, ART']

  for nativity in nativties:
    for grouping in groupings:
      if grouping == "HIV":
        if nativity == "USB":
          pop = bdf[(bdf.Year > 2003) & (bdf.Year < 2015) & (bdf.State_name.isin(hiv_states))].groupby("Iteration_num").Risk_of_prog_us.sum().mean() * Run_adjustment
        else:
          pop = bdf[(bdf.Year > 2003) & (bdf.Year < 2015) & (bdf.State_name.isin(hiv_states))].groupby("Iteration_num").Risk_of_prog_fb.sum().mean() * Run_adjustment
      else: #non-HIV
        if nativity == "USB":
          pop = bdf[(bdf.Year > 2003) & (bdf.Year < 2015) & (bdf.State_name == grouping)].groupby("Iteration_num").Risk_of_prog_us.sum().mean() * Run_adjustment
        else:
          pop = bdf[(bdf.Year > 2003) & (bdf.Year < 2015) & (bdf.State_name == grouping)].groupby("Iteration_num").Risk_of_prog_fb.sum().mean() * Run_adjustment
      print "Cases in {} {}: {}".format(nativity, grouping, pop)


  # Prevalence of MRF 2004, by USB and FB
  # ----------------------------------------------------------------------------------------

  print "Prevalence of MRF 2004, by USB and FB"

  nativties = [ "FB", "USB" ]
  groupings = [ "Smoker", "ESRD", "Diabetes", "HIV" ]
  hiv_states = ['Infected HIV, no ART', 'Infected HIV, ART']

  yoi = 2004 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  usb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_us.mean() * Run_adjustment
  fb_pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].Population_fb.mean() * Run_adjustment

  for nativity in nativties:
    for grouping in groupings:
      if grouping == "HIV":
        if nativity == "USB":
          pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name.isin(hiv_states))].groupby("Iteration_num").Population_us.sum().mean() * Run_adjustment
        else:
          pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name.isin(hiv_states))].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
      else: #non-HIV
        if nativity == "USB":
          pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == grouping)].groupby("Iteration_num").Population_us.sum().mean() * Run_adjustment
        else:
          pop = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == grouping)].groupby("Iteration_num").Population_fb.sum().mean() * Run_adjustment
      print "Cases in {} {}: {}".format(nativity, grouping, pop)

  # Projected cases (FB and US born) in 2025, in 2050 (not cumulative) for current strategy
  # ----------------------------------------------------------------------------------------

  print "Projected cases (FB and US born) in 2025, in 2050 (not cumulative) for current strategy"
  yoi = 2025 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  usb_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_us.sum().mean() * Run_adjustment * 12
  fb_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_fb.sum().mean() * Run_adjustment * 12
  print "Total number of cases {}: US {} FB {}".format(yoi,usb_cases,fb_cases)

  yoi = 2050 # year of interest
  coi = bdf[bdf.Year == yoi].Cycle_id.min() # cycle of interest (first cycle of year)
  usb_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_us.sum().mean() * Run_adjustment * 12
  fb_cases = bdf[(bdf.Cycle_id == coi) & (bdf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_fb.sum().mean() * Run_adjustment * 12
  print "Total number of cases {}: US {} FB {}".format(yoi,usb_cases,fb_cases)

  # FB 2x intervention - cumulative cases through 2065 ("FB 2x" = same rule for HCW, plus 13% of FB, because 6.5% x 2 = 13%)
  # ----------------------------------------------------------------------------------------

  # basecase
  cases = bdf[(bdf.Year > 2003) & (bdf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment
  print "Total number of cases basecase, 2004-2065 inclusive: {}".format(cases)
  
  # intervention df
  idf = df[df.Intervention_id == 1]

  # Base case FB 2x intervention defn (random testing each year)
  # Number of total cases (undisc'd)
  cases = idf[(idf.Year > 2003) & (idf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment
  print "Total number of cases FB 2x fold, 2004-2065 inclusive: {}".format(cases)

  cases_within_calib = bdf[(bdf.Year < 2017) & (bdf.Year > 2003) & (bdf.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment

  print "cases within calib "
  print cases_within_calib


  # Sensitivity Analysis FB 2x intervention defn (single lifetime test per person)
  # Number of total cases (undisc'd)
  # Curve shape

  print "Sensitivity Analysis FB 2x intervention defn (single lifetime test per person)"
  print "total cases: {}".format(cases_within_calib+55000)

  embed()


print "Done"


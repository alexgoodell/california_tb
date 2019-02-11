
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
    return "{:,.0f}".format(float('%.2g' % v))
  else:
    return "{:.2f}".format(float('%.2g' % v))


final_df = pd.DataFrame()


Run_adjustment = 100
# MRF, FB, FB + MRF, All

# df_locs = ["fb-small_output_by_cycle_and_state_full.csv"]

df = pd.read_csv("/hdd/share/larry-summer_best-guess_15-Aug-2017/masters/fb-limited-master.csv")

# remove calib data
df = df[df.Year > 2016]

df = df[df.Intervention_id == 3]

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

total_cases = df[(df.State_name == "Life")].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment


proportion_start_treatment = Variable.query.filter_by(name="Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test").first().value

sensitivty = Variable.query.filter_by(name="USB QFT Sensitivity").first().value

proportion_complete_treatment = Variable.query.filter_by(name="Proportion of started who complete treatment, 3HP").first().value 


## FB vs MRF pops
mrf_pop = df[(df.State_name == "Medical risk factor") & (df.Year == 2017)].Population.mean() * Run_adjustment
fb_pop = df[(df.State_name == "Life") & (df.Year == 2017)].Population_fb.mean() * Run_adjustment


print "FB pop: {} MRF pop: {}".format(fb_pop, mrf_pop)

## FB vs MRF LTBI prev
mrf_prev = (df[(df.State_name == "Medical risk factor") & (df.Year == 2017)].Slow_latents_fb.mean() * Run_adjustment + df[(df.State_name == "Medical risk factor") & (df.Year == 2017)].Slow_latents_us.mean() * Run_adjustment) / (df[(df.State_name == "Medical risk factor") & (df.Year == 2017)].Population.mean() * Run_adjustment)
fb_prev = (df[(df.State_name == "Life") & (df.Year == 2017)].Slow_latents_fb.mean() * Run_adjustment) / (df[(df.State_name == "Life") & (df.Year == 2017)].Population_fb.mean() * Run_adjustment)


print "FB prev: {} MRF prev: {}".format(fb_prev, mrf_prev)




for y in range(2017,2066):
  slow_lats_fb = df[(df.State_name == "Medical risk factor") & (df.Year == y)].Slow_latents_fb.mean() * Run_adjustment
  slow_lats_us = df[(df.State_name == "Medical risk factor") & (df.Year == y)].Slow_latents_us.mean() * Run_adjustment
  uninfected = df[(df.State_name == "Uninfected TB") & (df.Year == y)].Population.mean() * Run_adjustment

  prev = (slow_lats_fb + slow_lats_us) / (uninfected + slow_lats_fb + slow_lats_us)
  risk_of_therapy = prev*sensitivty*proportion_complete_treatment*proportion_start_treatment
  nnt = 1.0 / risk_of_therapy

  print "{} {}".format(y, nnt)


print "Done"
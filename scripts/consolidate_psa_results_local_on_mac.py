import time
import sys
import random
import string
import re
import os
import pandas as pd
import numpy as np
import argparse
from glob import glob

parser = argparse.ArgumentParser(description='s m l')
parser.add_argument("-n", "--name", type=str,
                    help="name of simulation")


mrf_state = [ "No medical risk factor", "Medical risk factor" ]
other = ["Life", "LTBI treated with RTP", "Uninfected TB"]
in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]

states_to_keep = mrf_state + other + in_treatment_states + fp_in_treatment_states + active_disease_states + testing_states 

# Columns to keep 

columns_to_keep = [ "Risk_of_prog_us",  "Risk_of_prog_fb", "Population", "Population_us", "Population_fb", "Year", "Months_life_remaining_us", "Months_life_remaining_fb", "Age", "Cycle_id", "Iteration_num", "Intervention_id", "Intervention_name", "State_name", "Costs", "State_id", "Psa_iteration_num" ] 


df_locs = [ "med-risk-factor_output_by_cycle_and_state_full_psa_iter_", "fb_output_by_cycle_and_state_full_psa_iter_", "fb-and-med-risk-factor_output_by_cycle_and_state_full_psa_iter_", "full-pop_output_by_cycle_and_state_full_psa_iter_" ]

dtype = {"Risk_of_prog_us": float,  
	"Risk_of_prog_fb": float,
	"Population": int,
	"Year": int,
	"Months_life_remaining_us":float,
	"Months_life_remaining_fb":float,
	"Population":float,
	"Age":float,
	"Cycle_id":int,
	"Iteration_num":int,
	"Intervention_id":int,
	"Intervention_name":str,
	"State_name":str,
	"Costs":float,
	"State_id":int,
	"Psa_iteration_num":int,
	}

master_df = pd.DataFrame()

ggl = '/Volumes/Main external/remotes nov 13/fb/*.csv'
print ggl
df_locs = glob(ggl)
i = 0

print df_locs

for df_loc in df_locs:
	print "--------" + str(df_loc) + "--------"
	df = pd.read_csv(df_loc) #, dtype=dtype)
	df = df[df.State_name.isin(states_to_keep)]
	df = df[columns_to_keep]
	unique = int(random.random() * 1000000)
	df["Iteration_num"] = unique
	print unique
	master_df = master_df.append(df)

master_df.to_csv("/Volumes/Main external/remotes nov 13/fb-limited-master.csv")
print "/Volumes/Main external/remotes nov 13/fb-limited-master.csv"




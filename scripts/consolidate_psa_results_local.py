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


args = parser.parse_args()
simulation_name = args.name






# note ------------- grabs all years. can shorten time by removing calib years


# mkdir /hdd/share/dec30_psa; mkdir /hdd/share/dec30_psa/full-pop; mkdir /hdd/share/dec30_psa/fb-and-med-risk-factor; mkdir /hdd/share/dec30_psa/fb; mkdir /hdd/share/dec30_psa/med-risk-factor

# mv /hdd/share/full-pop*.csv /hdd/share/dec30_psa/full-pop/; mv /hdd/share/fb-and-med-risk-factor*.csv /hdd/share/dec30_psa/fb-and-med-risk-factor/; mv /hdd/share/fb*.csv /hdd/share/dec30_psa/fb/; mv /hdd/share/med-risk-factor*.csv /hdd/share/dec30_psa/med-risk-factor/


# python consolidate_psa_results_local.py --name fb; python consolidate_psa_results_local.py --name fb-and-med-risk-factor; python consolidate_psa_results_local.py --name full-pop; python consolidate_psa_results_local.py --name med-risk-factor



# mv /hdd/share/full-pop_*.csv /hdd/share/dec30_psa/full-pop/; mv /hdd/share/fb-and-med-risk-factor_*.csv /hdd/share/dec30_psa/fb-and-med-risk-factor/; mv /hdd/share/fb_*.csv /hdd/share/dec30_psa/fb/; mv /hdd/share/med-risk-factor_*.csv /hdd/share/dec30_psa/med-risk-factor/

# States to keep

rtypes = [ "fb", "fb-and-med-risk-factor", "full-pop", "med-risk-factor" ]
for rtype in rtypes:

	mrf_state = [ "No medical risk factor", "Medical risk factor", "Slow latent", "Fast latent", "Less than one year", "Infected HIV, no ART", "Infected HIV, ART", "Diabetes", "ESRD", "Smoker", "Transplant patient", "TNF-alpha" ]
	other = ["Life", "LTBI treated with RTP", "Uninfected TB" ]
	in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
	fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
	active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
	testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]

	states_to_keep = mrf_state + other + in_treatment_states + fp_in_treatment_states + active_disease_states + testing_states 

	# Columns to keep 

	columns_to_keep = [ "Risk_of_prog_us",  "Risk_of_prog_fb", "Population",  "Year", "Months_life_remaining_us", "Months_life_remaining_fb", "Age", "Cycle_id", "Iteration_num", "Intervention_id", "Intervention_name", "State_name", "Costs", "State_id", "Psa_iteration_num" , "Population_us", "Population_fb",  "Recent_transmission_fb", "Recent_transmission_fb_rop", "Recent_transmission_us", "Recent_transmission_us_rop", "HCW_in_state"] 


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

	ggl = '/hdd/share/'+ simulation_name +'/' + rtype + '/*.csv'
	print ggl
	df_locs = glob(ggl)
	i = 0

	print df_locs

	for df_loc in df_locs:
		print "--------" + str(df_loc) + "--------"
		df = pd.read_csv(df_loc) #, dtype=dtype)
		df = df[df.State_name.isin(states_to_keep)]
		df = df[columns_to_keep]
		df = df[df.Year > 1999]
		unique = int(random.random() * 1000000)
		df["Iteration_num"] = unique
		print unique
		master_df = master_df.append(df)


	master_df.to_csv("/hdd/share/" + simulation_name + '/masters/' + rtype + "-limited-master.csv")
	print "/hdd/share/" + simulation_name + '/masters/' + rtype + "-limited-master.csv"




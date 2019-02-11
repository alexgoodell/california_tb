
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

df_locs = [ "med-risk-factor", "fb", "fb-and-med-risk-factor", "full-pop" ]



for df_loc in df_locs:
	master_df = pd.DataFrame()
	print "============" + df_loc 
	for i in range(0,43):
		df = pd.read_csv("go/tmp/cycle_state/small-psa-results-nov-5/" + df_loc + "_output_by_cycle_and_state_full_psa_iter_" + str(i) + ".csv", dtype=dtype)
		df["Iteration_num"] = i
		master_df = master_df.append(df)
		print "Appended " + str(i)
	master_df.to_csv("go/tmp/cycle_state/master-psa-results/" + df_loc + "-master.csv")
	print "Output " + df_loc + "-master.csv"




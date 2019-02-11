
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


# simulate a PSA by adding randomness to model 

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
	print "============" + df_loc 
	df = pd.read_csv("go/tmp/cycle_state/master-psa-results/" + df_loc + "-master.csv", dtype=dtype)
	df["rand_us"] = np.random.rand(df.shape[0])
	df["rand_fb"] = np.random.rand(df.shape[0])

	df["Risk_of_prog_us"] = df["Risk_of_prog_us"] + df["Risk_of_prog_us"] * (df["rand_us"]-0.5) * 0.2
	df["Risk_of_prog_fb"] = df["Risk_of_prog_fb"] + df["Risk_of_prog_fb"] * (df["rand_fb"]-0.5) * 0.2

	
	embed()


	df.to_csv("go/tmp/cycle_state/master-psuedo-psa-results/" + df_loc + "-master.csv")
	print "Output " + df_loc + "-master.csv"




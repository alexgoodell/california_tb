# LIMCAT Outputs

from IPython.display import Image
# For later visualizaton scripts
import pygraphviz as pgv
import time
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython import embed
import math

#connect to application
from app import * 


# get google drive spreadsheet for TPs

def tp_by_stratum_from_xls(sheetname):
	tp_df = pd.read_excel("raw-data-files/initialization_data.xlsx", sheetname=sheetname)
	for i, row in tp_df.iterrows():
		c_from_state = row["From:"]
		c_to_state = row["To:"]
		c_base = row["Base:"]
		c_stratum_name = row["Stratum name:"]

		if c_base == None:
			print "Empty line"
		elif c_base == "Calculated":
			print "Dynamic transition - calculated - skipping"	
		elif math.isnan(float(c_base)):
			print "Not a number"
		else:
			# Look for interaction
			tp = Transition_probability_by_stratum.query.filter_by(
					from_state_name = c_from_state,
					to_state_name = c_to_state,
					stratum_name = c_stratum_name
				).first()
			if tp == None:
				print "Could not find !!! "
				print ( c_from_state, c_to_state, c_stratum_name)
				sys.exit()
			else:
				tp.base = c_base
				# save
				db.session.add(tp)
				print tp,
				print " saved as ",
				print tp.base
	# final save
	db.session.commit()


# cxn = db.engine.connect()
# engine = db.engine
# df = pd.read_sql_query("SELECT * FROM outputs_by_cycle_state",engine)
# embed()


print " ------------- Costs --------------- "

# url = "https://docs.google.com/spreadsheets/d/1Dkyn0lPRlj-4FjJEH0kKBTNFpL6YeA9GhlC4tLa2cYU/pub?gid=1193911949&single=true&output=csv"

# cost_df = pd.read_csv(url)

cost_df = pd.read_excel("raw-data-files/main_inputs.xlsx", sheetname="Costs")

for i, row in cost_df.iterrows():
	c_name = row["Name"]
	c_base = row["Value"]
	c_low = row["Low"]
	c_high = row["High"]
	print c_name

	if c_base == None:
		print "Empty line"
	elif c_base == "Calculated":
		print "Dynamic transition - calculated - skipping"	
	elif math.isnan(float(c_base)):
		print "Not a number"
	else:
		# Look for cost
		cost = Cost.query.filter_by(
				state_name = c_name
			).first()
		if  cost == None:
			print "Could not find !!! "
			print c_name
			sys.exit()
		else:
			cost.costs = c_base
			cost.low = c_low
			cost.high = c_high
			# save
			db.session.add(cost)
			print cost,
			print " saved as ",
			print cost.costs
# final save
db.session.commit()



print " ------------- Interactions --------------- "

# get google drive spreadsheet for interactions
int_df = pd.read_excel("raw-data-files/main_inputs.xlsx", sheetname="Interactions")

for i, row in int_df.iterrows():
	c_from_state = row["From:"]
	c_to_state = row["To:"]
	c_in_state = row["In:"]
	c_adjustment = row["Adjustment  -base"]

	if c_adjustment == None:
		print "Empty line"
	elif math.isnan(c_adjustment):
		print "Not a number"
	else:
		# Look for interaction
		interaction = Interaction.query.filter_by(
				in_state_name = c_in_state,
				from_state_name = c_from_state,
				to_state_name = c_to_state
			).first()
		if interaction == None:
			print "Could not find !!! "
			print ( c_in_state, c_from_state, c_to_state)
			sys.exit()
		else:
			interaction.adjustment = c_adjustment
			interaction.low = row["Low"]
			interaction.high = row["High"]
			# save
			db.session.add(interaction)
			print interaction,
			print " saved as ",
			print interaction.adjustment
	# final save
	db.session.commit()


print " ------------- Transition probabilities --------------- "

# get google drive spreadsheet for TPs
tp_df = pd.read_excel("raw-data-files/main_inputs.xlsx", sheetname="Transition probabilites")

for i, row in tp_df.iterrows():
	c_from_state = row["From:"]
	c_to_state = row["To:"]
	c_base = row["Base estimate"]

	if c_base == None:
		print "Empty line"
	elif c_base == "Calculated":
		print "Dynamic transition - calculated - skipping"	
	elif math.isnan(float(c_base)):
		print "Not a number"
	else:
		# Look for interaction
		tp = Transition_probability.query.filter_by(
				from_state_name = c_from_state,
				to_state_name = c_to_state
			).first()
		if tp == None:
			print "Could not find !!! "
			print ( c_from_state, c_to_state)
			sys.exit()
		else:
			tp.tp_base = c_base
			tp.low = row["Low"]
			tp.high = row["High"]
			# save
			db.session.add(tp)
			print tp,
			print " saved as ",
			print tp.tp_base
	# final save
	db.session.commit()



print " ------------- Transition probabilities by stratum --------------- "


# hiv
sheet_urls = [ 'HIV' ]

# hiv risk group
sheet_urls += [ 'HIV risk groups' ]

# natural death
sheet_urls += [ 'Natural death' ]

# smoking
sheet_urls += [ 'Smoking' ]

# tnf alpha
sheet_urls += ['TNF alpha' ] 

# homeless
sheet_urls += ['Homeless' ] 

# etoh
sheet_urls += ['Alcohol' ]

# diabetes
sheet_urls += ['Diabetes' ]

# esrd
sheet_urls += ['ESRD' ]

# transplants
sheet_urls += ['Transplants' ]
				
# tb
# sheet_urls += ['raw-data-files/tb.csv']

for sheetname in sheet_urls:
	tp_by_stratum_from_xls(sheetname)	





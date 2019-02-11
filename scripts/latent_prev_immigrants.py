import pandas as pd
import sys
from IPython import embed
from app import *

cxn = db.engine.connect()
engine = db.engine
b_df = pd.read_sql_query("SELECT * FROM base_init_lines",engine)
tp_df = pd.read_sql_query("SELECT * FROM transition_probabilities_by_stratum",engine)

# only interested in 2014 and on
b_df = b_df[b_df.weight_new_people2014 > 0]

# 
tp_df_slow = tp_df[(tp_df.from_state_name == "Uninitialized") & (tp_df.to_state_name == "Slow latent")]
tp_df_fast = tp_df[(tp_df.from_state_name == "Uninitialized") & (tp_df.to_state_name == "Fast latent")]


#Not Foreign-born Afghanistan Male Asian Age 15-19
b_df["stratum"] = b_df["years_in_us"] + " " + b_df["birthplace"] + " " + b_df["sex"] + " " + b_df["race"] + " " + b_df["age_group"]

b_df["slow_latent_prev"] = 0 
b_df["fast_latent_prev"] = 0 

for i, row in b_df.iterrows():
	stratum = row["stratum"]
	pop = row["weight_new_people2014"]

	slow_latent_prev = float(tp_df_slow[tp_df_slow.stratum_name == stratum].base)
	fast_latent_prev = float(tp_df_fast[tp_df_fast.stratum_name == stratum].base)

	b_df.loc[i, "slow_latent_prev"] = slow_latent_prev
	b_df.loc[i, "fast_latent_prev"] = fast_latent_prev

	b_df.loc[i, "slow_latent_pop"] = slow_latent_prev * pop
	b_df.loc[i, "fast_latent_pop"] = fast_latent_prev * pop

total_slow_latent = b_df.slow_latent_pop.sum()
total_fast_latent = b_df.fast_latent_pop.sum()
total_pop = b_df.weight_new_people2014.sum()

print "total_slow_latent: " + str(total_slow_latent)
print "total_fast_latent: " + str(total_fast_latent)
print "total_pop: " + str(total_pop)


embed()
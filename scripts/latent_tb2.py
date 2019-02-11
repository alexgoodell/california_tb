import pandas as pd
import sys
from IPython import embed
from app import *

df = pd.read_excel("new_ltbi_calculations.xlsx", sheetname="Final")

df.loc[df.Birthplace == "Other and Western Pacific Region", "Birthplace"] = "Other Western Pacific Region"


# break LTBI into fast and slow

# assumed LTBI treated with INH 6m (from Miramontes 2015)


# ------ 1999 2000 ----
# LTBI prevalence. Based on our weighted analysis, we estimate
# 4.2% of the civilian, noninstitutionalized U.S. population aged
# 1 year or older, or 11,213,000 individuals, had LTBI in 1999–
# 2000. Based on reported history, we estimate that 25.5% (16.6–
# 37.1%) of those with LTBI had previously been diagnosed with
# LTBI or TB, and 13.2% (8.6–19.7%) of those with LTBI had
# previously been treated for LTBI or TB.

# .255*.132 = .03366


# ---- 2011 2012 -----
# in 2011 2012 NHANES survey respondents, 64.2 percent (61.2 - 67.0) had previously been tested for
# TB infection. Among persons who had been tested previously, 5.9% (5.0-6.9) reported being
# told their test result was positive. Of those individuals, 43.7% (38.9-48.7) were prescribed medicine
# to prevent TB infection from progressing to TB disease and 91.7% (88.1-94.2) completed


# 0.059 * 0.437 * 0.917 = .023643011

proportion_latent_treated =  0.059 * 0.437 * 0.917 



# see "recent transmission.xls"
proportion_fast_latent_usb = 0.014696946
proportion_fast_latent_fb = 0.021340953

# embed()


slow_latent_df = df.copy()
slow_latent_df.To_State = "Slow latent"
for i, row in slow_latent_df.iterrows():
	if row["Birthplace"] == "United States":
		slow_latent_df.loc[i, "Base"] = row["Base"] * (1.0-proportion_fast_latent_usb) * (1.0-proportion_latent_treated)
	else:
		slow_latent_df.loc[i, "Base"] = row["Base"] * (1.0-proportion_fast_latent_fb) * (1.0-proportion_latent_treated)

fast_latent_df = df.copy()
fast_latent_df.To_State = "Fast latent"
for i, row in fast_latent_df.iterrows():
	if row["Birthplace"] == "United States":
		fast_latent_df.loc[i, "Base"] = row["Base"] * proportion_fast_latent_usb
	else:
		fast_latent_df.loc[i, "Base"] = row["Base"] * proportion_fast_latent_fb


treated_latent_df = df.copy()
treated_latent_df.To_State = "LTBI treated with INH 6m"
for i, row in treated_latent_df.iterrows():
	if row["Birthplace"] == "United States":
		treated_latent_df.loc[i, "Base"] = row["Base"] * (1.0 - proportion_fast_latent_usb) * proportion_latent_treated
	else:
		treated_latent_df.loc[i, "Base"] = row["Base"] * (1.0 - proportion_fast_latent_fb) * proportion_latent_treated



# we assume no real active cases imported, just fast latents, which have high chance of conversion within three years

# active_data_df = pd.read_csv("raw-data-files/active_tb_prevalence.csv")


# active_data_df.loc[active_data_df.country == "United States of America", "country"] = "United States"
# active_data_df.loc[active_data_df.country == "Congo", "country"] = "Democratic Republic of Congo"

# active_prev_in_us = float(active_data_df[active_data_df.country == "United States"].tb_per_100k_base)/100000.0


# active_df = df.copy()
# active_df.To_State = "Active - untreated"

# for i, row in active_df.iterrows():
# 	active_prev = active_data_df[active_data_df.country == row['Birthplace']].tb_per_100k_base
# 	active_prev = float(active_prev)/100000.0
# 	active_df.loc[i, "Base"] = active_prev


#composite_df = slow_latent_df.append([fast_latent_df, active_df])


# slow
slow_df_not_fb = slow_latent_df.copy()
slow_df_not_fb["years_in_us"] = 'Not Foreign-born'
slow_df_less_than_one = slow_latent_df.copy()
slow_df_less_than_one["years_in_us"] = 'Less than one year'
slow_df_btwn_one_and_five = slow_latent_df.copy()
slow_df_btwn_one_and_five["years_in_us"] = 'Between one and 5 years'
slow_df_five_or_more = slow_latent_df.copy()
slow_df_five_or_more["years_in_us"] = '5 or more years'


slow_composite_df = slow_df_less_than_one.append([slow_df_not_fb, slow_df_btwn_one_and_five,slow_df_five_or_more])


# fast
fast_df_not_fb = fast_latent_df.copy()
fast_df_not_fb["years_in_us"] = 'Not Foreign-born'
fast_df_less_than_one = fast_latent_df.copy()
fast_df_less_than_one["years_in_us"] = 'Less than one year'
fast_df_btwn_one_and_five = fast_latent_df.copy()
fast_df_btwn_one_and_five["years_in_us"] = 'Between one and 5 years'
fast_df_five_or_more = fast_latent_df.copy()
fast_df_five_or_more["years_in_us"] = '5 or more years'


fast_composite_df = fast_df_less_than_one.append([fast_df_not_fb, fast_df_btwn_one_and_five,fast_df_five_or_more])


# active
treated_latent_df_not_fb = treated_latent_df.copy()
treated_latent_df_not_fb["years_in_us"] = 'Not Foreign-born'
treated_latent_df_less_than_one = treated_latent_df.copy()
treated_latent_df_less_than_one["years_in_us"] = 'Less than one year'
treated_latent_df_btwn_one_and_five = treated_latent_df.copy()
treated_latent_df_btwn_one_and_five["years_in_us"] = 'Between one and 5 years'
treated_latent_df_five_or_more = treated_latent_df.copy()
treated_latent_df_five_or_more["years_in_us"] = '5 or more years'


treated_composite_df = treated_latent_df_less_than_one.append([treated_latent_df_not_fb, treated_latent_df_btwn_one_and_five,treated_latent_df_five_or_more])



# active
# active_df_not_fb = active_df.copy()
# active_df_not_fb["years_in_us"] = 'Not Foreign-born'
# active_df_less_than_one = active_df.copy()
# active_df_less_than_one["years_in_us"] = 'Less than one year'
# active_df_btwn_one_and_five = active_df.copy()
# active_df_btwn_one_and_five["years_in_us"] = 'Between one and 5 years'
# active_df_five_or_more = active_df.copy()
# active_df_five_or_more["years_in_us"] = '5 or more years'

# active_df_not_fb['Base'] = active_prev_in_us
# active_df_btwn_one_and_five['Base'] = active_prev_in_us
# active_df_five_or_more['Base'] = active_prev_in_us

# active_composite_df = active_df_less_than_one.append([active_df_not_fb, active_df_btwn_one_and_five,active_df_five_or_more])


# uninfected
uninfected_composite_df = treated_composite_df.copy()
uninfected_composite_df.To_State = "Uninfected TB"
uninfected_composite_df.Base = 1 - (slow_composite_df.Base+fast_composite_df.Base+treated_composite_df.Base) 


master_df = pd.concat([slow_composite_df, fast_composite_df, treated_composite_df, uninfected_composite_df])


# master_df = composite_df_less_than_one.append([composite_df_btwn_one_and_five, composite_df_five_or_more])

# active prevalence for those who have been here one or more years is assumed to be same as rest of US population


# Other and Western Pacific Region Male Asian Age 20-24
master_df["Stratum"] = master_df.years_in_us + " " + master_df.Birthplace + " " + master_df.Sex + " " + master_df.Race + " " + master_df["Age group"]

#embed()

print "Adding rows to DB"

p = 1000
for i, row in master_df.iterrows():
	if i==p:
		print str(i)  + " rows imported"
		p = p + 1000
	tp = Transition_probability_by_stratum.query.filter_by(stratum_name=row["Stratum"],from_state_name="Uninitialized",to_state_name=row["To_State"]).first()
	tp.base = row['Base']
	db.session.add(tp)
db.session.commit()


print "Done"


























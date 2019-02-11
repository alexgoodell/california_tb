import pandas as pd
import numpy as np
import sys
from IPython import embed
#  using a csv that Sheena prepared for me. 2014 data.
df = pd.read_csv("raw-data-files/chis/2014.csv", thousands=",")


# will apply same prevalence for 'Age 15-19'

age_groups = [
 { 'theirs': '18-25 YEARS', 'ours': 'Age 20-24'},
 { 'theirs': '26-29 YEARS', 'ours': 'Age 25-29'},   
 { 'theirs': '30-34 YEARS', 'ours': 'Age 30-34'},
 { 'theirs': '35-39 YEARS', 'ours': 'Age 35-39'},
 { 'theirs': '40-44 YEARS', 'ours': 'Age 40-44'},
 { 'theirs': '45-49 YEARS', 'ours': 'Age 45-49'},
 { 'theirs': '50-54 YEARS', 'ours': 'Age 50-54'},
 { 'theirs': '55-59 YEARS', 'ours': 'Age 55-59'},
 { 'theirs': '60-64 YEARS', 'ours': 'Age 60-64'},
 { 'theirs': '65-69 YEARS', 'ours': 'Age 65-69'},
 { 'theirs': '70-74 YEARS', 'ours': 'Age 70-74'},
 { 'theirs': '75-79 YEARS', 'ours': 'Age 75-79'},
 { 'theirs': '80-84 YEARS', 'ours': 'Age 80+'},
 { 'theirs': '85+ YEARS'  , 'ours': 'Age 80+'}]

for age_group in age_groups:
    df.loc[df.AGE == age_group["theirs"], "AGE"] = age_group["ours"]


sexes = [
 { 'theirs': 'SRSEX=FEMALE', 'ours': 'Female'},
 { 'theirs': 'SRSEX=MALE', 'ours': 'Male'}]

for sex in sexes:
    df.loc[df.SEX == sex["theirs"], "SEX"] = sex["ours"]


races = [
 { 'theirs': 'racen=HISPANIC', 'ours': 'Hispanic'},
 { 'theirs': 'racen=WHITE', 'ours': 'White'},
 { 'theirs': 'racen=BLACK', 'ours': 'Black'},
 { 'theirs': 'racen=ASIAN,CHINA', 'ours': 'Asian'},
 { 'theirs': 'racen=ASIANONLY', 'ours': 'Asian'},
 { 'theirs': 'racen=ASIAN,PHIL', 'ours': 'Asian'},
 { 'theirs': 'racen=OTHER', 'ours': 'Other'},
 { 'theirs': 'racen=ASIAN,VIET', 'ours': 'Asian'}
]

for race in races:
    df.loc[df.RACE == race["theirs"], "RACE"] = race["ours"]


navitities = [
 { 'theirs': 'BORN IN THE US', 'ours': 'USB'},
 { 'theirs': '5+ YEARS', 'ours': 'FB'},
 { 'theirs': '<5 YEARS', 'ours': 'FB'}
]

# remane annoying column titles
df = df.rename(columns={'BORN WHERE?': 'NATIVITY'})
df = df.rename(columns={' WEIGHTED N ': 'weight'})

for nat in navitities:
    df.loc[df['NATIVITY'] == nat["theirs"], "NATIVITY"] = nat["ours"]


# make float
# df['weight'] = df['weight'].astype("float")


# dm_df = df.groupby(['DIABETES','RACE','AGE','SEX','NATIVITY']).weight.sum().reset_index()

# dm_prev_df = dm_df[dm_df.DIABETES == 'DM=YES']




#reduced df (rdf)

rdf = df[df.DIABETES == 'DM=YES'].groupby(['RACE','AGE','SEX','NATIVITY']).weight.sum().reset_index()

rdf = rdf.drop("weight", axis=1)

# DM
rdf["num DM"] = df[df.DIABETES == 'DM=YES'].groupby(['RACE','AGE','SEX','NATIVITY']).weight.sum().reset_index()["weight"].fillna(0)
rdf["num no DM"] = df[df.DIABETES == 'DM=NO'].groupby(['RACE','AGE','SEX','NATIVITY']).weight.sum().reset_index()["weight"].fillna(0)

# Smoke
rdf["num smoker"] = df[df["CURRENT SMOKE"] == 'SMKCUR=YES'].groupby(['RACE','AGE','SEX','NATIVITY']).weight.sum().reset_index()["weight"].fillna(0)
rdf["num non-smoker"] = df[df["CURRENT SMOKE"] == 'SMKCUR=NO'].groupby(['RACE','AGE','SEX','NATIVITY']).weight.sum().reset_index()["weight"].fillna(0)

rdf = rdf.rename(columns={'RACE': 'race'})
rdf = rdf.rename(columns={'AGE': 'age'})
rdf = rdf.rename(columns={'SEX': 'sex'})
rdf = rdf.rename(columns={'NATIVITY': 'nativity'})


#u'RACE', u'AGE', u'SEX', u'NATIVITY', u'DM', u'No DM', u'year', u'Smoker', u'Non-smoker'],

# 'SMKCUR=NO', 'SMKCUR=YES'





# do the other years (different format)

big_df = pd.DataFrame()

for year in [2001,  2003,  2005,  2007,  2011]:
	qdf = pd.read_csv("raw-data-files/chis/" + str(year) + ".csv")
	qdf["year"] = year
	qdf = qdf.rename(columns={'racehpr2': 'racehpr'})
	big_df = big_df.append(qdf)

big_df = big_df.rename(columns={'racehpr': 'race'})
big_df = big_df.rename(columns={'ab22': 'diabetes'})
big_df = big_df.rename(columns={'smkcur': 'smoking'})
big_df = big_df.rename(columns={'rakedw0': 'weight'})
big_df = big_df.rename(columns={'srsex': 'sex'})
big_df = big_df.rename(columns={'cntrys': 'nativity'})
big_df = big_df.rename(columns={'srage_p': 'age'})

big_df = big_df.drop("ae15a", axis=1)

# age

# make age groups
age_groups = [{'low': 15, 'high': 19 , 'name': 'Age 15-19' },
                {'low': 20, 'high': 24 , 'name': 'Age 20-24' },
                {'low': 25, 'high': 29 , 'name': 'Age 25-29' },
                {'low': 30, 'high': 34 , 'name': 'Age 30-34' },
                {'low': 35, 'high': 39 , 'name': 'Age 35-39' },
                {'low': 40, 'high': 44 , 'name': 'Age 40-44' },
                {'low': 45, 'high': 49 , 'name': 'Age 45-49' },
                {'low': 50, 'high': 54 , 'name': 'Age 50-54' },
                {'low': 55, 'high': 59 , 'name': 'Age 55-59' },
                {'low': 60, 'high': 64 , 'name': 'Age 60-64' },
                {'low': 65, 'high': 69 , 'name': 'Age 65-69' },
                {'low': 70, 'high': 74 , 'name': 'Age 70-74' },
                {'low': 75, 'high': 79 , 'name': 'Age 75-79' },
                {'low': 80, 'high': 1000, 'name': 'Age 80+' }]

# make a new column

big_df["age_group"] = "Young"

# set new column
for age_group in age_groups:
    big_df.loc[(big_df.age >= age_group["low"]) & (big_df.age <= age_group["high"]), "age_group"] = age_group['name']

# race
races = [
 { 'theirs': 'WHITE', 'ours': 'White'},
 { 'theirs': 'AFRICAN AMERICAN', 'ours': 'Black'},
 { 'theirs': 'OTHER SINGLE/MULTIPLE RACE', 'ours': 'Other'},
 { 'theirs': 'LATINO', 'ours': 'Hispanic'},
 { 'theirs': 'ASIAN', 'ours': 'Asian'},
 { 'theirs': 'AIAN', 'ours': 'Other'},
 { 'theirs': 'PACIFIC ISLANDER', 'ours': 'Asian'},
 { 'theirs': 'AMERICAN INDIAN/ALASKAN NATIVE', 'ours': 'Other'},
]

for race in races:
    big_df.loc[big_df.race == race["theirs"], "race"] = race["ours"]


# dm
dm_statuses = [
 { 'theirs': 'NO', 'ours': 'No'},
 { 'theirs': 'YES', 'ours': 'Yes'},
 { 'theirs': 'DON\x92T KNOW', 'ours': 'No'},
 { 'theirs': 'REFUSED', 'ours': 'No'},
 { 'theirs': 'BORDERLINE OR PRE-DIABETES', 'ours': 'No'}]

for dm_status in dm_statuses:
    big_df.loc[big_df.diabetes == dm_status["theirs"], "diabetes"] = dm_status["ours"]

# smoking
smok_statuses = [
 { 'theirs': 'NOT CURRENT SMOKER', 'ours': 'No'},
 { 'theirs': 'CURRENT SMOKER', 'ours': 'Yes'},
 { 'theirs': 'PROXY SKIPPED', 'ours': 'No'},
 { 'theirs': 'NOT ASCERTAINED', 'ours': 'No'}]

for smok_status in smok_statuses:
    big_df.loc[big_df.smoking == smok_status["theirs"], "smoking"] = smok_status["ours"]


# nativity

big_df.loc[big_df.nativity != "UNITED STATES", "nativity"] = "FB"
big_df.loc[big_df.nativity == "UNITED STATES", "nativity"] = "USB"

#sex

big_df.loc[big_df.sex == "MALE", "sex"] = "Male"
big_df.loc[big_df.sex == "FEMALE", "sex"] = "Female"


for col in big_df.columns:
	print " ============ " + col + " ================" 
	print big_df[col].value_counts()


#  -------------------- calculate DM and SMOKING --- not using years

mdf = big_df.groupby(['race','age_group','sex','nativity']).weight.sum().reset_index().set_index(['race','age_group','sex','nativity'])
mdf = mdf.rename(columns={'weight': 'total'})

# DM
mdf["num DM"] = big_df[big_df.diabetes == 'Yes'].groupby(['race','age_group','sex','nativity']).weight.sum()
mdf["num no DM"] = big_df[big_df.diabetes == 'No'].groupby(['race','age_group','sex','nativity']).weight.sum()

# Smoke
mdf["num smoker"] = big_df[big_df.smoking == 'Yes'].groupby(['race','age_group','sex','nativity']).weight.sum()
mdf["num non-smoker"] = big_df[big_df.smoking == 'No'].groupby(['race','age_group','sex','nativity']).weight.sum()

#Total

# mdf["total"] = big_df.groupby(['race','age_group','sex','nativity']).weight.sum().reset_index()["weight"].fillna(0)

mdf = mdf.reset_index()

embed()

# prevalence
for i, row in mdf.iterrows():
	mdf.loc[i, "dm prev"] = row["num DM"] / row["total"]
	mdf.loc[i, "smoking prev"] =  row["num smoker"] / row["total"]

for d in ["num smoker", "num DM"]:
	for n in ["USB", "FB"]:
		print "prev of " + d + " in " + n
		print mdf[mdf.nativity == n][d].sum() / mdf[mdf.nativity == n]["total"].sum()

# get averages
avg_dm_prev_by_age_group = mdf.groupby("age_group")["num DM"].sum() /  mdf.groupby("age_group").total.sum()
avg_smok_prev_by_age_group = mdf.groupby("age_group")["num smoker"].sum() /  mdf.groupby("age_group").total.sum()

# people without a DM prev get assign an average from age group
for i, row in mdf[(np.isnan(mdf['dm prev'])) | (mdf['dm prev'] == 0)].iterrows():
	mdf.loc[i, 'dm prev'] = avg_dm_prev_by_age_group[row['age_group']]

for i, row in mdf[(np.isnan(mdf['smoking prev'])) | (mdf['smoking prev'] == 0)].iterrows():
	mdf.loc[i, 'smoking prev'] = avg_smok_prev_by_age_group[row['age_group']]


# final export

final_dm_df = pd.DataFrame(columns=['Stratum name:','From:','To:','Base:'])
final_smok_df = pd.DataFrame(columns=['Stratum name:','From:','To:','Base:'])

# easiest way to seperate the USB is with the "length of time in US" chain. 
# But need to specify same prevalence for each period since did not analyze seperately.

# dm
for i, row in mdf.iterrows():
	if row["nativity"] == "FB":
		stratum_name = "{} {} {} {}".format(row["sex"], row["race"], row["age_group"], "Not Foreign-born")
		final_dm_df.loc[len(final_dm_df)] = [ stratum_name, "Uninitialized", "Diabetes", row["dm prev"] ]
		final_dm_df.loc[len(final_dm_df)] = [ stratum_name, "Uninitialized", "No diabetes", 1-row["dm prev"] ]
	if row["nativity"] == "USB":
		for x in ['Less than one year', 'Between one and 5 years', '5 or more years']:
			stratum_name = "{} {} {} {}".format(row["sex"], row["race"], row["age_group"], x)
			final_dm_df.loc[len(final_dm_df)] = [ stratum_name, "Uninitialized", "Diabetes", row["dm prev"] ]
			final_dm_df.loc[len(final_dm_df)] = [ stratum_name, "Uninitialized", "No diabetes", 1-row["dm prev"] ]	
# smoking

for i, row in mdf.iterrows():
	if row["nativity"] == "FB":
		stratum_name = "{} {} {} {}".format(row["sex"], row["race"], row["age_group"], "Not Foreign-born")
		final_smok_df.loc[len(final_smok_df)] = [ stratum_name, "Uninitialized", "Smoker", row["smoking prev"] ]
		final_smok_df.loc[len(final_smok_df)] = [ stratum_name, "Uninitialized", "Non-smoker", 1-row["smoking prev"] ]
	if row["nativity"] == "USB":
		for x in ['Less than one year', 'Between one and 5 years', '5 or more years']:
			stratum_name = "{} {} {} {}".format(row["sex"], row["race"], row["age_group"], x)
			final_smok_df.loc[len(final_smok_df)] = [ stratum_name, "Uninitialized", "Smoker", row["smoking prev"] ]
			final_smok_df.loc[len(final_smok_df)] = [ stratum_name, "Uninitialized", "Non-smoker", 1-row["smoking prev"] ]


# final_dm_df.to_csv("dm.csv")
# final_smok_df.to_csv("smok.csv")


      
      
      
      
      
      

















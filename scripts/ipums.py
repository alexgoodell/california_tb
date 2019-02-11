# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 14:13:50 2015

@author: alexgoodell
"""
# import python depedencies (libraries used)
import pandas as pd
import sys
from IPython import embed
from app import *
import argparse


# before you run this, you have to download the .dta
# from the IPUMS website, and follow their instructions to
# put it in stata. Then export to csvs; the defaults is to
# replace the number ids with the label names. This is 
# what we want. Make sure you've only included california, ie
# statefip == "California"

# then I read the CSV into a python "pandas" dataframe
df = pd.read_csv("archive/raw_all_years_ipums_small_new.csv") 


# Age
# ----------
# clean ages
df = df[df.age != 'Less than 1 year old']
df.age[df.age == "90 (90+ in 1980 and 1990)"] = 90

# convert to integer
df.age = df.age.astype(int) 

# remove <15 yo
df = df[df.age > 14]

# make age groups used by model
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

# make a new blank column
df["age_group"] = "Young"

# set new column with the age groups listed from above
for age_group in age_groups:
    df.loc[(df.age >= age_group["low"]) & (df.age <= age_group["high"]), "age_group"] = age_group['name']

# make sure there is nothing left
if len(df[df.age_group == "Young"]) > 0:
    print "Error"
    sys.exit(1)
    

# Race
# ------
# Since we are using "hispanic" as a race, we need to make all people with
# hispanic enthnicity "hispanic" as race

df.loc[df.hispan != "Not Hispanic", "race"] = "Hispanic"

# Now we replace the names used by them with the names used by us
races = [{ 'theirs': 'White', 'ours': 'White'},
{ 'theirs': 'Black/Negro', 'ours': 'Black'},   
{ 'theirs': 'Other Asian or Pacific Islander', 'ours': 'Asian'},
{ 'theirs': 'Chinese', 'ours': 'Asian'},
{ 'theirs': 'Other race, nec', 'ours': 'Other'},
{ 'theirs': 'Japanese', 'ours': 'Asian'},
{ 'theirs': 'Two major races', 'ours': 'Other'},
{ 'theirs': 'Three or more major races', 'ours': 'Other'},
{ 'theirs': 'American Indian or Alaska Native', 'ours': 'Other'}]

for race in races:
    df.loc[df.race == race["theirs"], "race"] = race["ours"]
    

# time in US
# ----------
# replace their categories with ours for over 5 years

yrs_in_us_groups = [{'low': 0, 'high': 1 , 'name': 'Less than one year' },
                {'low': 1, 'high': 6 , 'name': 'Between one and 5 years' },
                {'low': 5, 'high': 1000 , 'name': '5 or more years' }]


# make a new column
df["years_in_us"] = "Placeholder"

# set new column
for years_in_us in yrs_in_us_groups:
    df.loc[(df.yrsusa1 >= years_in_us["low"]) & (df.yrsusa1 < years_in_us["high"]), "years_in_us"] = years_in_us['name']

df.loc[pd.isnull(df.yrsusa2), "years_in_us"] = "Not Foreign-born"


# place of birth
# we keep track of the top 5 + other high burden countries + central america
# everything else is grouped into its WHO region
# make a list of all high-burden countries

hbcs = ["Afghanistan",
"Bangladesh",
"Brazil",
"Cambodia",
"China",
"Democratic Republic of Congo",
"Ethiopia",
"India",
"Indonesia",
"Kenya",
"Mozambique",
"Myanmar",
"Nigeria",
"Pakistan",
"Philippines",
"Russian Federation",
"South Africa",
"United Republic of Tanzania",
"Thailand",
"Uganda",
"Viet Nam",
"Zimbabwe"]

# After comparison, with the below function, i found I needed to change
# some country names

df.loc [df.bpld == "South Africa (Union of)", "bpld"] = "South Africa"
df.loc [df.bpld == "Congo", "bpld"] = "Democratic Republic of Congo"
df.loc [df.bpld == "Vietnam", "bpld"] = "Viet Nam"
df.loc [df.bpld == "Tanzania", "bpld"] = "United Republic of Tanzania"
df.loc [df.bpld == "Russia", "bpld"] = "Russian Federation"
df.loc [df.bpld == "Other USSR/Russia", "bpld"] = "Russian Federation"
df.loc [df.bpld == "USSR ns", "bpld"] = "Russian Federation"
df.loc [df.bpld == "Burma (Myanmar)", "bpld"] = "Myanmar"
df.loc [df.bpld == "Cambodia (Kampuchea)", "bpld"] = "Cambodia"
df.loc[df.bpld == "Belize/British Honduras", "bpld"] = "Belize"

for hbc in hbcs:
    print hbc
    print hbc in pd.unique(df.bpld).tolist()
    # all "true" except mozambique
    
ca_and_mex_countries = ["Mexico",
"Belize",
"Guatemala",
"El Salvador",
"Honduras",
"Nicaragua",
"Costa Rica",
"Panama"]

# group other countries

country_replace = [ { 'theirs': 'Iran', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Portugal', 'ours': 'Other European Region'},
{ 'theirs': 'Puerto Rico', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'North America, ns', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Germany', 'ours': 'Other European Region'},
{ 'theirs': 'Netherlands', 'ours': 'Other European Region'},
{ 'theirs': 'Latvia', 'ours': 'Other European Region'},
{ 'theirs': 'Chile', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Japan', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Hong Kong', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Hungary', 'ours': 'Other European Region'},
{ 'theirs': 'Taiwan', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Macau', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Korea', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Canada', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Laos', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Nepal', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'France', 'ours': 'Other European Region'},
{ 'theirs': 'Wales', 'ours': 'Other European Region'},
{ 'theirs': 'Western Europe, ns', 'ours': 'Other European Region'},
{ 'theirs': 'Northern Ireland', 'ours': 'Other European Region'},
{ 'theirs': 'Romania', 'ours': 'Other European Region'},
{ 'theirs': 'Venezuela', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Austria', 'ours': 'Other European Region'},
{ 'theirs': 'Norway', 'ours': 'Other European Region'},
{ 'theirs': 'United Kingdom, ns', 'ours': 'Other European Region'},
{ 'theirs': 'England', 'ours': 'Other European Region'},
{ 'theirs': 'Italy', 'ours': 'Other European Region'},
{ 'theirs': 'Morocco', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Guam', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Ireland', 'ours': 'Other European Region'},
{ 'theirs': 'Cuba', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Ukraine', 'ours': 'Other European Region'},
{ 'theirs': 'Fiji', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Armenia', 'ours': 'Other European Region'},
{ 'theirs': 'USSR, ns', 'ours': 'Other European Region'},
{ 'theirs': 'Bosnia', 'ours': 'Other European Region'},
{ 'theirs': 'Singapore', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Bolivia', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Finland', 'ours': 'Other European Region'},
{ 'theirs': 'Africa, ns/nec', 'ours': 'Other African Region'},
{ 'theirs': 'Denmark', 'ours': 'Other European Region'},
{ 'theirs': 'Lithuania', 'ours': 'Other European Region'},
{ 'theirs': 'Greece', 'ours': 'Other European Region'},
{ 'theirs': 'Tonga', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Trinidad and Tobago', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Ghana', 'ours': 'Other African Region'},
{ 'theirs': 'Israel/Palestine', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Croatia', 'ours': 'Other European Region'},
{ 'theirs': 'Asia, nec/ns', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Southwest Asia, nec/ns', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'East Asia, ns', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Asia Minor, ns', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Egypt/United Arab Rep.', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Sweden', 'ours': 'Other European Region'},
{ 'theirs': 'Estonia', 'ours': 'Other European Region'},
{ 'theirs': 'Jordan', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Lebanon', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Czechoslovakia', 'ours': 'Other European Region'},
{ 'theirs': 'Poland', 'ours': 'Other European Region'},
{ 'theirs': 'Scotland', 'ours': 'Other European Region'},
{ 'theirs': 'Ecuador', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Malaysia', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Argentina', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Sierra Leone', 'ours': 'Other African Region'},
{ 'theirs': 'Colombia', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Moldavia', 'ours': 'Other European Region'},
{ 'theirs': 'Turkey', 'ours': 'Other European Region'},
{ 'theirs': 'Byelorussia', 'ours': 'Other European Region'},
{ 'theirs': 'Iraq', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Peru', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Algeria', 'ours': 'Other African Region'},
{ 'theirs': 'Switzerland', 'ours': 'Other European Region'},
{ 'theirs': 'Marshall Islands', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Oceania, ns/nec', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Bermuda', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Australia', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Belgium', 'ours': 'Other European Region'},
{ 'theirs': 'Kuwait', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Sudan', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Syria', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Azerbaijan', 'ours': 'Other European Region'},
{ 'theirs': 'Serbia', 'ours': 'Other European Region'},
{ 'theirs': 'Uzbekistan', 'ours': 'Other European Region'},
{ 'theirs': 'Sri Lanka (Ceylon)', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'Czech Republic', 'ours': 'Other European Region'},
{ 'theirs': 'South America ns', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Uruguay', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Spain', 'ours': 'Other European Region'},
{ 'theirs': 'Americas, ns', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Libya', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Europe, ns.', 'ours': 'Other European Region'},
{ 'theirs': 'Dominican Republic', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Jamaica', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Haiti', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'New Zealand', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Liberia', 'ours': 'Other African Region'},
{ 'theirs': 'North Korea', 'ours': 'Other African Region'},
{ 'theirs': 'South Korea', 'ours': 'Other African Region'},
{ 'theirs': 'Bulgaria', 'ours': 'Other European Region'},
{ 'theirs': 'Cameroon', 'ours': 'Other African Region'},
{ 'theirs': 'Eritrea', 'ours': 'Other African Region'},
{ 'theirs': 'Cape Verde', 'ours': 'Other African Region'},
{ 'theirs': 'Central Africa', 'ours': 'Other African Region'},
{ 'theirs': 'Guinea', 'ours': 'Other African Region'},
{ 'theirs': 'Togo', 'ours': 'Other African Region'},
{ 'theirs': 'St. Kitts-Nevis', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Barbados', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Paraguay', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Yemen Arab Republic (North)', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Republic of Georgia', 'ours': 'Other European Region'},
{ 'theirs': 'Kazakhstan', 'ours': 'Other European Region'},
{ 'theirs': 'American Samoa', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'United Arab Emirates', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Samoa, 1940-1950', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Azores', 'ours': 'Other European Region'},
{ 'theirs': 'Cyprus', 'ours': 'Other European Region'},
{ 'theirs': 'Saudi Arabia', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'St. Vincent', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Guyana/British Guiana', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Grenada', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Yugoslavia', 'ours': 'Other European Region'},
{ 'theirs': 'Other, nec', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Western Africa, ns', 'ours': 'Other African Region'},
{ 'theirs': 'North Africa, ns', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'U.S. Virgin Islands', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Eastern Africa, nec/ns', 'ours': 'Other African Region'},
{ 'theirs': 'Slovakia', 'ours': 'Other European Region'},
{ 'theirs': 'Albania', 'ours': 'Other European Region'},
{ 'theirs': 'Iceland', 'ours': 'Other European Region'},
{ 'theirs': 'Micronesia', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'West Indies, ns', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Zaire', 'ours': 'Other African Region'},
{ 'theirs': 'Senegal', 'ours': 'Other African Region'},
{ 'theirs': 'Bahamas', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Somalia', 'ours': 'Other Eastern Mediterranean Region'},
{ 'theirs': 'Northern Mariana Islands', 'ours': 'Other Western Pacific Region'},
{ 'theirs': 'Caribbean, ns', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Dominica', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Macedonia', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Zambia', 'ours': 'Other African Region'},
{ 'theirs': 'Montenegro', 'ours': 'Other European Region'},
{ 'theirs': 'Bhutan', 'ours': 'Other South-East Asia Region'},
{ 'theirs': 'St. Lucia', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'South America, ns', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Antigua-Barbuda', 'ours': 'Other Region of the Americas'},
{ 'theirs': 'Gambia', 'ours': 'Other African Region'} ]

# replace their names with our names
for country_name in country_replace:
    print country_name["theirs"]
    df.loc [df.bpld == country_name["theirs"], "bpld"] = country_name["ours"]

# USA
df.loc[df.years_in_us == "Not Foreign-born", "bpld"] = "United States"

# make a list of all acceptable birthplaces
acceptable_birthplaces = ca_and_mex_countries + hbcs + ["United States"] + ["Other European Region", "Other Region of the Americas", "Other African Region",
     "Other Eastern Mediterranean Region", "Other Western Pacific Region","Other South-East Asia Region"]

# check to make sure there are no remaining odd countries
for bp in pd.unique(df.bpld):
    if bp not in acceptable_birthplaces:
        print bp + " is not acceptable country"
        sys.exit(1)
    else:
        print bp + " is acceptable"


# citizenship
df.loc[pd.isnull(df.citizen), "citizen"] = "Born in US"

# convert person weight to integer
df.perwt = df.perwt.astype('int')


# I print out some information about the population in 2001; this is used in another
# excel analysis

birthplace_breakdown_needed = False
if birthplace_breakdown_needed:
    print "Birthplaces of population in 2001:"
    cs = ["Afghanistan", "Bangladesh", "Belize", "Brazil", "Cambodia", "China", "Costa Rica", "Democratic Republic of Congo", "El Salvador", "Ethiopia", "Guatemala", "Honduras", "India", "Indonesia", "Kenya", "Mexico", "Myanmar", "Nicaragua", "Nigeria", "Pakistan", "Panama", "Philippines", "Russian Federation", "South Africa", "Thailand", "Uganda", "United Republic of Tanzania", "Viet Nam", "Zimbabwe", "Other African Region", "Other Region of the Americas", "Other South-East Asia Region", "Other European Region", "Other Eastern Mediterranean Region", "Other Western Pacific Region", "Mozambique"]
    for c in cs:
        tot = df[(df.year == 2001) & (df.bpld == c)].perwt.sum()
        print '"{}":{}'.format(c, str(tot))
    races = ["Black", "White", "Hispanic", "Asian", "Other"]
    cs = ["Afghanistan", "Bangladesh", "Belize", "Brazil", "Cambodia", "China", "Costa Rica", "Democratic Republic of Congo", "El Salvador", "Ethiopia", "Guatemala", "Honduras", "India", "Indonesia", "Kenya", "Mexico", "Myanmar", "Nicaragua", "Nigeria", "Pakistan", "Panama", "Philippines", "Russian Federation", "South Africa", "Thailand", "Uganda", "United Republic of Tanzania", "Viet Nam", "Zimbabwe", "Other African Region", "Other Region of the Americas", "Other South-East Asia Region", "Other European Region", "Other Eastern Mediterranean Region", "Other Western Pacific Region", "Mozambique"]
    cr_df = pd.DataFrame(columns=["Country", "Black", "White", "Hispanic", "Asian", "Other"])
    for c in cs:
        cr_df.loc[len(cr_df), "Country"] = c
        for race in races:
            tot = df[df.year == 2001][(df.race == race) & (df.bpld == c)].perwt.sum()
            cr_df.loc[len(cr_df)-1, race] = tot
            print '{} {}:{}'.format(c, race, str(tot))

# I print out some information about the population demographics from 2001-2014; 
# this is used in outputs.py 

race_nativitiy_pop_needed = True
if race_nativitiy_pop_needed:
    rn_df = pd.DataFrame(columns=["RN","Year","Population","Source"])
    races = ["Hispanic", "White", "Black", "Asian", "Other"]
    nativities = ["USB", "FB"]
    years = range(2001,2015)
    for year in years:
        for race in races:
            for nativity in nativities:
                race_nativity = race + " " + nativity
                rn_df.loc[len(rn_df), "RN"] = race_nativity
                rn_df.loc[len(rn_df)-1, "Year"] = year
                rn_df.loc[len(rn_df)-1, "Source"] = "IPUMS"
                if nativity == "USB":
                    rn_df.loc[len(rn_df)-1, "Population"] = df[(df.year == year) & (df.race == race) & (df.bpld == "United States")].perwt.sum()
                else:
                    rn_df.loc[len(rn_df)-1, "Population"] = df[(df.year == year) & (df.race == race) & (df.bpld != "United States")].perwt.sum()
    rn_df.to_csv("raw-data-files/race_nativitiy_pop_from_ipums.csv")







# ------ make a consolidated dataframe -----------

r_df = df[['sex', 'race', 'age_group', 'years_in_us', 'citizen', 'perwt', 'bpld']] 

# rename them to the same as the DB
r_df.rename(columns={'perwt': 'weight', 'bpld': 'birthplace'}, inplace=True)

# find the sum of weights for the stratifications of interest
grouped = r_df.groupby([r_df.sex, r_df.race, r_df.age_group, r_df.citizen, r_df.years_in_us, r_df.birthplace]).weight.sum() 
g_df = pd.DataFrame(grouped)
g_df.drop("weight", 1)

## ------ print out # people in each year ----

years = range(2001,2015)
for year in years:
    print year 
    print df[df.year == year].perwt.sum()
df[(df.year == 2014) & (df.bpld != "United States") & (df.years_in_us < 1)].perwt.sum()


## ------ current people 2001 (used for calibration) ------

r_df = df[df.year == 2001][['sex', 'race', 'age_group', 'years_in_us', 'citizen', 'perwt', 'bpld']] #
# rename them to the same as the DB
r_df.rename(columns={'perwt': 'weight', 'bpld': 'birthplace'}, inplace=True)
grouped = r_df.groupby([r_df.sex, r_df.race, r_df.age_group, r_df.citizen, r_df.years_in_us, r_df.birthplace]).weight.sum() 
g_df["weight2001"] = grouped
print "Weight current people 2001"
print g_df.weight2001.sum()


## ------ current people 2014 (used for model run) ------

r_df = df[df.year == 2014][['sex', 'race', 'age_group', 'years_in_us', 'citizen', 'perwt', 'bpld']] #
# rename them to the same as the DB
r_df.rename(columns={'perwt': 'weight', 'bpld': 'birthplace'}, inplace=True)
grouped = r_df.groupby([r_df.sex, r_df.race, r_df.age_group, r_df.citizen, r_df.years_in_us, r_df.birthplace]).weight.sum() #r_df.bpld,
g_df["weight2014"] = grouped
print "Weight current people 2014"
print g_df.weight2014.sum()

## ----------- new arivers and people aging into model ------------------



# not enough people entering with "Less than one year ago" so I made it if you were abroad one year ago that counts
df.loc[(df.migrate1 == "Abroad one year ago") & (df.years_in_us != "Not Foreign-born") ,'years_in_us'] = 'Less than one year'


years = range(2001,2015)
for year in years:

    # we want people who have either been here for less than a year (new arrivers) or aged 15
    r_df = df[df.year == year]
    r_df = r_df[(r_df.migrate1 == "Abroad one year ago") | (r_df.migrate1 == "Moved between states") | (r_df.age == 15)]
    r_df = r_df[['sex', 'race', 'age_group', 'years_in_us', 'citizen', 'perwt', 'bpld']] 
    # rename them to the same as the DB
    r_df.rename(columns={'perwt': 'weight', 'bpld': 'birthplace'}, inplace=True)

    grouped = r_df.groupby([r_df.sex, r_df.race, r_df.age_group, r_df.citizen, r_df.years_in_us, r_df.birthplace]).weight.sum() #r_df.bpld,

    g_df["weight_new_people" + str(year)] = grouped

    print "Weight new people " + str(year)
    print g_df["weight_new_people" + str(year)].sum()

# embed()
# print " ---- Print the # Immigrant adults (<1 yr in US) ---- "
 

# imdf = pd.DataFrame(columns=["Country"])
# central_america = ["Belize", "Guatemala", "El Salvador", "Honduras", "Nicaragua", "Costa Rica", "Panama"]
# cdf = df.copy()
# cdf.loc[cdf.bpld.isin(central_america), "bpld"] = "Central America"
# other_hbc = ["Afghanistan", "Bangladesh", "Brazil", "Cambodia", "Democratic Republic of Congo", "Ethiopia", "Indonesia", "Kenya", "Myanmar", "Nigeria", "Pakistan", "Russian Federation", "South Africa", "United Republic of Tanzania", "Thailand", "Uganda", "Zimbabwe"]
# cdf.loc[cdf.bpld.isin(other_hbc), "bpld"] = "Other WHO High-Burden Countries"
# to_display = [ "India", "Philippines", "Viet Nam", "Mexico", "China", "Other African Region", "Other Region of the Americas", "Other South-East Asia Region", "Other European Region", "Other Eastern Mediterranean Region", "Other Western Pacific Region", "Central America", "Other WHO High-Burden Countries" ]
# for country in to_display:
#     imdf.loc[len(imdf), "Country"] = country
# for year in range(2001,2015):
#     for country in to_display:
#         imdf.loc[imdf.Country == country, year] = cdf[(cdf.year == year) & (cdf.bpld == country) & (cdf.years_in_us == "Less than one year")].perwt.sum()


# add the data to the SQL database

# g_df = g_df.reset_index()


cxn = db.engine.connect()
engine = db.engine
con = engine.raw_connection() 

g_df.to_sql(con=con, name='base_init_lines', if_exists='replace', flavor='sqlite')




import pandas as pd
from IPython import embed

df = pd.read_csv("archive/raw_all_years_ipums_small_new.csv")

df = df[df.age != 'Less than 1 year old']
df.age[df.age == "90 (90+ in 1980 and 1990)"] = 90
df.age = df.age.astype(int) 

print " ---- Adult population ---- "

print "From IPUMS"

for year in range(2001,2015):
    print str(year) + "	" + str(df[(df.year == year) & (df.age > 14)].perwt.sum())



print "From CA Dept of Finance"

cdf = pd.read_excel("archive/california_dept_of_finance_pop_estimates_2001-2010.xls",sheetname="Total")
cdf = cdf[cdf.CountyName == "California"]

for year in range(2001,2011):
	print str(year) + "	" + str(cdf[cdf.Age > 14][year].sum())


print " ---- Less than one year adults (<1 yr in US) ---- "


yrs_in_us_groups = [{'low': 0, 'high': 1 , 'name': 'Less than one year' },
                {'low': 1, 'high': 6 , 'name': 'Between one and 5 years' },
                {'low': 5, 'high': 1000 , 'name': '5 or more years' }]


# make a new column
df["years_in_us"] = "Placeholder"

# set new column
for years_in_us in yrs_in_us_groups:
    df.loc[(df.yrsusa1 >= years_in_us["low"]) & (df.yrsusa1 < years_in_us["high"]), "years_in_us"] = years_in_us['name']

df.loc[pd.isnull(df.yrsusa2), "years_in_us"] = "Not Foreign-born"


for year in range(2001,2015):
    print str(year) + " " + str(df[(df.year == year) & (df.age > 14) & (df.years_in_us == "Less than one year")].perwt.sum())



print " ---- Less than one year, all ages (<=1 yr in US) ---- "

for year in range(2001,2015):
    print str(year) + "	" + str(df[(df.year == year) & (df.years_in_us == "Less than one year")].perwt.sum())







print " ---- Abroad one year ago, all ages ---- "

for year in range(2001,2015):
    print str(year) + "	" + str(df[(df.year == year) & (df.migrate1 == "Abroad one year ago")].perwt.sum())

embed()

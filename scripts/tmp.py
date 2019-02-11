import pandas as pd

df = pd.read_csv("raw-data-files/raw_all_years_ipums_small.csv")

df = df[df.age != 'Less than 1 year old']
df.age[df.age == "90 (90+ in 1980 and 1990)"] = 90
df.age = df.age.astype(int) 


for year in range(2001,2015):
    print str(year) + "	" + str(df[(df.year == year) & (df.age > 14)].perwt.sum())
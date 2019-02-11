import pandas as pd
from app import *

def getStateIdByName(name):
  return State.query.filter_by(name=name).first().id

life_id = getStateIdByName("Life")

df = pd.read_csv("go/tmp/cycle_state/" + "10i-med-risk-factor_output_by_cycle_and_state_full.csv")

#Initial processing
Run_adjustment = 1000
df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
df["Average life expectancy, months"] = df["Months_life_remaining_total"] / df.Population
df["Expected total active cases"] = df["Months_life_remaining_total"] * df["Risk_of_prog_total"] / df.Population
intervention_ids = pd.unique(df.Intervention_id)

df["Elim"] = (df["Population"] * Run_adjustment) / 1000000
df["PreElim"] = (df["Population"] * Run_adjustment) / 1000000

cases_in_2001 = (df[(df.State_id == life_id) & (df.Year == 2001) & (df.Intervention_name == "Basecase")].groupby(["Year", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment).mean()
cases_in_2014 = (df[(df.State_id == life_id) & (df.Year == 2014) & (df.Intervention_name == "Basecase")].groupby(["Year", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment).mean()


cases_in_2063 = (df[(df.State_id == life_id) & (df.Year == 2063) & (df.Intervention_name == "Basecase")].groupby(["Year", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment).mean()
cases_in_2064 = (df[(df.State_id == life_id) & (df.Year == 2064) & (df.Intervention_name == "Basecase")].groupby(["Year", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment).mean()


print ("between 2001 and 2014 there was a {}% reduction annually".format(100.0*((1.0 - cases_in_2014/cases_in_2001)/(2014.0-2001.0))))
print ("between 2063 and 2064 there was a {}% reduction".format((1.0 - cases_in_2064 / cases_in_2063)*100.0))
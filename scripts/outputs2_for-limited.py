
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


import argparse

parser = argparse.ArgumentParser(description='s m l')
parser.add_argument("-s", "--size", type=str,
                    help="size of run")
parser.add_argument("-n", "--name", type=str,
                    help="name of simulation")
parser.add_argument("-i", "--images", type=str,
                    help="name of simulation")
parser.add_argument("-r", "--is_remote", type=int,
                    help="name of simulation")
parser.add_argument("-q", "--is_single", type=int,
                    help="name of simulation")
parser.add_argument("-c", "--comment", type=str,
                    help="  about simulation")
parser.add_argument("-t", "--type", type=str,
                    help="is psa")


args = parser.parse_args()
if args.size == 's':
    Run_adjustment = 1000
if args.size == 'm':
    Run_adjustment = 100
if args.size == 'l':
    Run_adjustment = 10

Run_type = args.type


comment = args.comment



if args.images == 'y' or args.images == 'yes':
  Include_images = True
else:
  Include_images = False

RandomSeq = int(time.time())
Html = ""
Image_dir = "output_figures/" + str(RandomSeq)
Html_dir = "output_html/"
Fig_count = 0
Output_name = args.name


  



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def commas(value):
  if np.isnan(value):
    return np.nan
  if value < 10000:
    return str(np.round(value,2))
  if value > 1000000: 
    value = value / 1000000
    value = np.round(value,1)
    value = "{0}m".format(value)
    return value
  else:
    value = int(np.round(value/1000)*1000)
    value = "{:,}".format(value)
    return str(value) 

def to_html(text):
    global Html
    Html += text

def next_fig_count():
  global Fig_count
  Fig_count = Fig_count + 1
  return Fig_count


def p(text):
    to_html("<p>" + text + "</p>")


def h1(text):
    to_html("<h1>" + text + "</h1>")



def h2(text):
    to_html("<h2>" + text + "</h2>")

def h3(text):
    to_html("<h3>" + text + "</h3>")

def h4(text):
    to_html("<h4>" + text + "</h4>")

def img(src):
    to_html("<img src=\"" + src + "\" />")

def html_figure(name, size, caption):
  global Fig_count
  global Image_dir
  global Html_dir
  filename = name + ".png"
  # plt.figure(figsize=(12,9), dpi=150)
  plt.savefig(Html_dir + Image_dir + filename, bbox_inches='tight', dpi=300)
  plt.clf()
  img_template = '''
          <p> <img src="{0}" alt="{1}" class="{3}" /> 
          <span class="caption"><strong>Figure {2}.</strong> {1} </span> </p>
          '''
  img_template = img_template.format(Image_dir + filename, caption, next_fig_count(), size)
  to_html(img_template)

def get_all_chain_names():
    all_chain_names = list()
    all_chains = Chain.query.all()
    for chain in all_chains:
        all_chain_names.append(chain.name)
    return all_chain_names

def getStateIdByName(name):
  return State.query.filter_by(name=name).first().id

def getChainIdByName(name):
  return Chain.query.filter_by(name=name).first().id

def save_outputs():
  global Html
  global Html_dir
  global Output_name
  f = open("templates/template.html", 'r')
  template = f.read()
  f.close()
  revised_template = re.sub(r'\s{{content}}\s', Html, template)
  f = open(Html_dir + str(RandomSeq) + Output_name + ".html", 'w+')
  f.write(revised_template)
  f.close()
  os.system('open '+ Html_dir + str(RandomSeq) + Output_name + ".html")




def get_state_list_from_chain_name(chain_name):
    chain = Chain.query.filter_by(name=chain_name).first()
    states = chain.states
    state_name_list = list()
    for state in states:
        if state.name != "Death" and state.name != "Uninitialized":
            state_name_list.append(state.name)
    return state_name_list



def prevalence_chart(chain_name, df, groupings, intervention_id, chart_name):
  global Run_adjustment
  chain = Chain.query.filter_by(name=chain_name).first()
  rdf = df[df.Intervention_id == intervention_id]
  rdf["Group_name"] = None

  for group in groupings:
    group_contents = group['contents']
    state_ids = [ State.query.filter_by(name=state_name,chain=chain).first().id for state_name in group['contents'] ]
    group_name = group['name']
    rdf.loc[rdf.State_id.isin(state_ids), "Group_name"] = group_name

  rdf = rdf.groupby(["Group_name", "Cycle_id", 'Iteration_num']).Population.sum() * Run_adjustment
  rdf = rdf.reset_index()
  ax = sns.tsplot(time="Cycle_id", value="Population", unit="Iteration_num", condition="Group_name", data=rdf)



def generate_cdph_table(df, intervention_id, begin_cycle, end_cycle):
  
  cdph_df = pd.read_csv("raw-data-files/cdph_data.csv")

  for x in ['Latents', 'Active', 'Active M2', 'Pop']:
      for y in ['FB', 'US', 'Total']:
        for z in [ 'base', 'low', 'high', 'composite']:

          col_name = '{0} {1} {2} {3}'.format(x,y,z,"limcat")
          cdph_df[col_name] = np.nan



Simulation_name = args.name
Is_remote = args.is_remote




# df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/med_10_runs_output_by_cycle_and_state_full.csv")



# df = pd.read_csv("go/tmp/cycle_state/med_10_runs_16_cycles_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/calib_cure_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/small_rop_100c_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/calib_risk_groups_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/memory_output_by_cycle_and_state_full.csv")
# if Is_remote == 1:
#   df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full.csv", encoding='ascii')
# if Run_type == "psa-1" or Run_type == "psa-2":
#   df = pd.read_csv("go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full_psa_iter_0.csv",  encoding='ascii')
#   for i in range(1, 5):
#     df = df.append(pd.read_csv("go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full_psa_iter_" + str(i) + ".csv",  encoding='ascii'))
# else:
#   df = pd.read_csv("go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full.csv",  encoding='ascii')

df = pd.read_csv("go/tmp/cycle_state/blue-beatle/fb/fb_1495158677665750959.csv" ,  encoding='ascii')



print "Is single? " + str(args.is_single)


# method one for analysis -- average all runs within the PSA, then use each average as the "iteration"
# for the rest of the program 
# ie if  you ran a PSA with 10 iterations and 5 iterations within those,
# you would find average within the 10, and use those as the "iterations"

if Run_type == "psa-1":
  print "Is PSA. First, need to average within each PSA run."

  # make a smaller df from just one Iteration run (we will average everything within these)
  sdf = df[df.Iteration_num == 0]
  sdf.set_index(["Cycle_id", "State_id", "Psa_iteration_num"], inplace=True)
  psa_runs = pd.unique(df.Psa_iteration_num)
  cols_to_average = "Ylls", "Ylds", "Population", "Population_fb", "Population_us", "Costs", "Dalys",  "Fast_latents_fb", "Active_cases_us", "Slow_latents_us", "Fast_latents_us", "Risk_of_prog_us", "Risk_of_prog_fb", "Months_life_remaining_us", "Months_life_remaining_fb", "Age", "Recent_transmission_us", "Recent_transmission_fb", "Recent_transmission_us_rop", "Recent_transmission_fb_rop", "Transmission_within_us", "Risk_of_infection_fb", "Risk_of_infection_us"
  for col in cols_to_average:
    # finds the mean within each PSA
    sdf[col] = df.groupby(["Cycle_id", "State_id", "Psa_iteration_num"])[col].mean()
  sdf.reset_index(inplace=True)
  sdf.drop("Iteration_num", axis=1, inplace=True)
  sdf = sdf.rename(columns={'Psa_iteration_num': 'Iteration_num'})
  df = sdf


# method two - just forget the PSA differentiation, and treat all runs the same
# ie if  you ran a PSA with 10 iterations and 10 iterations within those,
# you would just make a new column with id's 0-100 and use that.
if Run_type == "psa-2":
  sdf = df.set_index(["Psa_iteration_num", "Iteration_num"])
  sdf["index_col"] = sdf.index
  # at this point index_col has lists of the psa and iteratin num, like: (2, 3)
  # we want to replace those with plain numbers
  for i, value in enumerate(pd.unique(sdf["index_col"])):
    sdf.loc[sdf.index_col == value, "index_col"] = i
  sdf.reset_index(inplace=True)
  sdf.drop("Iteration_num", axis=1, inplace=True)
  sdf = sdf.rename(columns={'index_col': 'Iteration_num'})
  # embed()
  df = sdf




# embed()

if args.is_single == 1:
  df_copy = df.copy()
  df_copy.loc[:,"Iteration_num"] = 1
  df = df.append(df_copy)



# df = pd.read_csv("go/tmp/cycle_state/bigbig_output_by_cycle_and_state_full.csv")

# initial processing
df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
df["Average life expectancy, months"] = df["Months_life_remaining_total"] / df.Population
df["Expected total active cases"] = df["Months_life_remaining_total"] * df["Risk_of_prog_total"] / df.Population


# df = pd.read_csv("go/tmp/cycle_state/test120_output_by_cycle_and_state_full.csv")



# active_id = getStateIdByName("Active - untreated")

# int_comparison = df[df.State_id == active_id].groupby(["Intervention_id", "Cycle_id"]).Active_cases.mean()


# ax = sns.tsplot(time="Cycle_id", value="Active_cases", unit="Iteration_num", condition="Intervention_id", data=df[df.State_id == active_id])

# html_figure("test","large","Here is a caption")

intervention_ids = pd.unique(df.Intervention_id)




#  -----------------------------------------  cdph --------------------------------------------------------


begin_cycle = df[df.Year == 2014].Cycle_id.min()
end_cycle = df[df.Year == 2014].Cycle_id.max()

cdph_df = generate_cdph_table(df,intervention_id=0,begin_cycle=begin_cycle,end_cycle=end_cycle)



p(comment)




# ------------------------------- Population ----------------------------------

h3("LTBI prevalence by ethnicity, mid-2001")


lpe = pd.DataFrame(columns=["Race", "USB", "FB"])

races = ["Black", "Asian", "Hispanic", "White", "Other"]

for race in races:
  # FB
  slow = df[(df.State_name == race) & (df.Cycle_id == 5)].Slow_latents_fb.mean()
  fast = df[(df.State_name == race) & (df.Cycle_id == 5)].Fast_latents_fb.mean()
  pop = df[(df.State_name == race) & (df.Cycle_id == 5)].Population_fb.mean()
  total_fb = (slow + fast) / pop

  slow = df[(df.State_name == race) & (df.Cycle_id == 5)].Slow_latents_us.mean()
  fast = df[(df.State_name == race) & (df.Cycle_id == 5)].Fast_latents_us.mean()
  pop = df[(df.State_name == race) & (df.Cycle_id == 5)].Population_us.mean()
  total_us = (slow + fast) / pop

  lpe.loc[len(lpe), "Race"] = race
  lpe.loc[len(lpe)-1, "USB"] = total_us
  lpe.loc[len(lpe)-1, "FB"] = total_fb



to_html(lpe.to_html(classes="table table-striped"))





h3("Initializing the correct population")

p('''

We first need to set the correct population estimates for each of the subgroups 
of interest. Here is a comparison of our estimated population sizes in the model
run compared to estimates from CDPH. Some of the data sources are the same. Note
that 0's may mean "not reported."

''')

# -------- Table -------------


iterables = [['CDPH Estimates', 'LIMCAT estimates'],['US', 'FB', 'Total']]
index = pd.MultiIndex.from_product(iterables)


tmp = cdph_df[["Pop US born CDPH",  "Pop FB CDPH", "Tot Pop CDPH", "Pop US composite limcat", "Pop FB composite limcat", "Pop Total composite limcat"]]
# embed()

tmp[["Pop US born CDPH",  "Pop FB CDPH", "Tot Pop CDPH"]] = tmp[["Pop US born CDPH",  "Pop FB CDPH", "Tot Pop CDPH"]].fillna(0).applymap(commas)

tmp[[ "Pop US composite limcat", "Pop FB composite limcat", "Pop Total composite limcat"]] = tmp[[ "Pop US composite limcat", "Pop FB composite limcat", "Pop Total composite limcat"]].fillna(0)


tdf = pd.DataFrame(tmp.as_matrix(),index=cdph_df["Group"],columns=index)

to_html(tdf.to_html(classes="table table-striped"))



p('''



We can also visualize each sub-group as a bar chart.



''')

# -------- Graph -------------



q = cdph_df[["Tot Pop CDPH", "Pop Total base limcat", "Group"]]
q = q.rename(columns={"Tot Pop CDPH": 'CDPH', "Pop Total base limcat": 'LIMCAT'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={"level_1": 'Model', 0: 'Individuals', 'Group':'Risk group'})

ax = sns.barplot(x="Risk group", y="Individuals", hue="Model", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals (10m)")
plt.tight_layout()

html_figure("test","large","Population estimates")


# -------- Graph for pres-------------


groups_for_pres = ["Homeless", "HIV infected (HIV/AIDS)", "Diabetes", "End-stage renal disease (ESRD)", "Smokers", "Transplant", "TNF-alpha", "Alcohol", "IDU", "Imported cases ie < 1 year in US"]


q = cdph_df[["Pop Total base limcat", "Group"]][cdph_df.Group.isin(groups_for_pres)]
q = q.sort(columns=["Pop Total base limcat"])

q = q.rename(columns={"Pop Total base limcat": 'CAPE'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={0: 'Individuals', 'Group':'Risk group'})

ax = sns.barplot(x="Risk group", y="Individuals", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals (10m)")
plt.tight_layout()

html_figure("test_pres","large","Population estimates")



groups_for_pres = [ "Asian", "Hispanic", "Black", "White", "Other"]


q = cdph_df[["Pop Total base limcat", "Group"]][cdph_df.Group.isin(groups_for_pres)]
q = q.sort(columns=["Pop Total base limcat"])

q = q.rename(columns={"Pop Total base limcat": 'CAPE'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={0: 'Individuals', 'Group':'Risk group'})

ax = sns.barplot(x="Risk group", y="Individuals", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals (10m)")
plt.tight_layout()

html_figure("test_pres2","large","Population estimates")




# ------------------------------- Latent ----------------------------------

p('<div class="break"></div>')
h3("Latent infection")


p('''





''')


# -------- Table -------------

# 'Back-calculated estimates',
iterables = [['CDPH Estimates', 'LIMCAT estimates'],['US', 'FB', 'Total']]
index = pd.MultiIndex.from_product(iterables)



tmp = cdph_df[["Est Latents US born", "Est Latents FB", "Est Latents Total", "Exp Latents US born", "Exp Latents FB", "Exp Latents Total", 'Latents US composite limcat', 'Latents FB composite limcat', 'Latents Total composite limcat']]
# embed()

tmp[["Est Latents US born", "Est Latents FB", "Est Latents Total", "Exp Latents US born", "Exp Latents FB", "Exp Latents Total"]] = tmp[["Est Latents US born", "Est Latents FB", "Est Latents Total", "Exp Latents US born", "Exp Latents FB", "Exp Latents Total"]].fillna(0).applymap(commas)


# removing the expected
tmp = tmp[["Est Latents US born", "Est Latents FB", "Est Latents Total", 'Latents US composite limcat', 'Latents FB composite limcat', 'Latents Total composite limcat']]



tdf = pd.DataFrame(tmp.as_matrix(),index=cdph_df["Group"],columns=index)

to_html(tdf.to_html(classes="table table-striped"))





# -------- Graph -------------




q = cdph_df[["Est Latents Total", "Latents Total base limcat", "Group"]]
# q = q.rename(columns={"Tot Pop CDPH": 'CDPH', "Pop Total base limcat": 'LIMCAT'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={"level_1": 'Model', 0: 'Individuals', 'Group':'Risk group'})


ax2 = sns.barplot(x="Risk group", y="Individuals", hue="Model", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals")
plt.tight_layout()

html_figure("latents_comparison","large","Latent TB infections")

# save_outputs()
# cdph_df.to_csv("output_cdph.csv")



# -------- Graph for presentation -------------

groups_for_pres = ["HIV infected (HIV/AIDS)", "End-stage renal disease (ESRD)", "Transplant", "TNF-alpha", "Diabetes",  "Smokers"]


q = cdph_df[[ "Latents FB base limcat", "Latents US base limcat",  "Group"]][cdph_df.Group.isin(groups_for_pres)]
q = q.sort(columns=["Latents FB base limcat"])
q = q.rename(columns={ "Latents FB base limcat": 'FB', "Latents US base limcat":'US-born'})
# q = q.rename(columns={"Tot Pop CDPH": 'CDPH', "Pop Total base limcat": 'LIMCAT'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={ 0: 'Individuals', 'level_1': 'Nativity', 'Group':'Risk group'})


ax2 = sns.barplot(x="Risk group", hue="Nativity", y="Individuals", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals")
plt.tight_layout()

html_figure("latents_comparison_pres","large","Latent TB infections")



groups_for_pres = [ "Diabetes",  "Smokers", "Alcohol"]


q = cdph_df[[ "Latents FB base limcat", "Latents US base limcat",  "Group"]][cdph_df.Group.isin(groups_for_pres)]
q = q.sort(columns=["Latents FB base limcat"])
q = q.rename(columns={ "Latents FB base limcat": 'FB', "Latents US base limcat":'US-born'})
# q = q.rename(columns={"Tot Pop CDPH": 'CDPH', "Pop Total base limcat": 'LIMCAT'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={ 0: 'Individuals', 'level_1': 'Nativity', 'Group':'Risk group'})


ax2 = sns.barplot(x="Risk group", hue="Nativity", y="Individuals", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals")
plt.tight_layout()

html_figure("latents_comparison_pres213","large","Latent TB infections")






groups_for_pres = [ "Asian", "Hispanic", "Black", "White", "Other"]


q = cdph_df[[ "Latents FB base limcat", "Latents US base limcat",  "Group"]][cdph_df.Group.isin(groups_for_pres)]
q = q.sort(columns=["Latents FB base limcat"])
q = q.rename(columns={ "Latents FB base limcat": 'FB', "Latents US base limcat":'US-born'})
# q = q.rename(columns={"Tot Pop CDPH": 'CDPH', "Pop Total base limcat": 'LIMCAT'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={ 0: 'Individuals', 'level_1': 'Nativity', 'Group':'Risk group'})


ax2 = sns.barplot(x="Risk group", hue="Nativity", y="Individuals", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals")
plt.tight_layout()

html_figure("latents_comparison_pres_2","large","Latent TB infections")




# ------------------- by country 


# ------------------- by country 

r = df[(df.Cycle_id == 0) & (df.Chain_id == 3)][["State_name", "Slow_latents_fb"]]
r.loc[:,"Slow_latents_fb"]= r.loc[:,"Slow_latents_fb"] * Run_adjustment
r = r.groupby("State_name").Slow_latents_fb.mean().reset_index()
r = r[(r.State_name != 'Death') & (r.State_name != "Uninitialized") & (r.State_name != "United States")]

central_america = ["Belize", "Guatemala", "El Salvador", "Honduras", "Nicaragua", "Costa Rica", "Panama"]
other_hbc = ["Afghanistan", "Bangladesh", "Brazil", "Cambodia", "Democratic Republic of Congo", "Ethiopia", "Indonesia", "Kenya", "Myanmar", "Nigeria", "Pakistan", "Russian Federation", "South Africa", "United Republic of Tanzania", "Thailand", "Uganda", "Zimbabwe"]

central_america_sum = r[r.State_name.isin(central_america)].Slow_latents_fb.sum()
other_hbc_sum = r[r.State_name.isin(other_hbc)].Slow_latents_fb.sum()

r = r.reset_index()[["State_name", "Slow_latents_fb"]]

r.loc[len(r)] = ['Central America', central_america_sum]
r.loc[len(r)] = (['Other WHO High-Burden Countries', other_hbc_sum])

r.loc[r.State_name == "Other African Region", "State_name"] = "Other African Region, non-HBC"
r.loc[r.State_name == "Other Region of the Americas", "State_name"] = "Other Region of the Americas, non-HBC"
r.loc[r.State_name == "Other South-East Asia Region", "State_name"] = "Other South-East Asia Region, non-HBC"
r.loc[r.State_name == "Other European Region", "State_name"] = "Other European Region, non-HBC"
r.loc[r.State_name == "Other Eastern Mediterranean Region", "State_name"] = "Other Eastern Mediterranean Region, non-HBC"
r.loc[r.State_name == "Other Western Pacific Region", "State_name"] = "Other Western Pacific Region, non-HBC"


to_display = [ "India", "Philippines", "Viet Nam", "Mexico", "China", "Other African Region, non-HBC", "Other Region of the Americas, non-HBC", "Other South-East Asia Region, non-HBC", "Other European Region, non-HBC", "Other Eastern Mediterranean Region, non-HBC", "Other Western Pacific Region, non-HBC", "Central America", "Other WHO High-Burden Countries" ]
r = r[r.State_name.isin(to_display)]

r.loc[r.State_name == "Viet Nam", "State_name"] = "Vietnam"

r = r.sort(columns=["Slow_latents_fb"])
ax2 = sns.barplot(x="State_name", y="Slow_latents_fb", data=r)
plt.xticks(rotation=-90)
plt.ylabel("Individuals with latent TB")
plt.xlabel("Birthplace")
plt.tight_layout()

html_figure("latenkjljl","large","Latent TB infections")


# r.T.plot(kind="pie", )

# html_figure("latenkjljlpie","large","Latent TB infections")






# save_outputs()
# cdph_df.to_csv("output_cdph.csv")


# ------------------------------- Active ----------------------------------

# embed()
p('<div class="break"></div>')
h3("Active cases - control")


p('''


There are two methods shown here for the calculation of yearly cases. There
is a "randomized" method, which shows how many TB infections actually occured
at a certain time-point, versus the "non-randomized" method that shows the 
sum of the probabilities of getting an active case. The second method is more
accurate but is discongruent with how active cases are propogated within the 
model.


''')


# -------- Table -------------





# embed()



iterables = [['CDPH Reports', 'LIMCAT estimates randomized method', 'LIMCAT estimates non-randomized method'],['US', 'FB', 'Total']]
index = pd.MultiIndex.from_product(iterables)




tmp = cdph_df[["Active US born CDPH", "Active FB CDPH", "Active Total CDPH",  'Active US composite limcat', 'Active FB composite limcat', 'Active Total composite limcat' ,  'Active M2 US composite limcat', 'Active M2 FB composite limcat', 'Active M2 Total composite limcat' ]]
# embed()

tmp[["Active US born CDPH", "Active FB CDPH", "Active Total CDPH"]] = tmp[["Active US born CDPH", "Active FB CDPH", "Active Total CDPH"]].fillna(0).applymap(commas)

tdf = pd.DataFrame(tmp.as_matrix(),index=cdph_df["Group"],columns=index)

to_html(tdf.to_html(classes="table table-striped"))



# -------------------------- Figure



q = cdph_df[["Group", "Active Total CDPH", 'Active Total base limcat']]
q = q.rename(columns={"Active Total CDPH": 'CDPH', "Active Total base limcat": 'CAPE'})
q = q.set_index("Group").stack().reset_index()
q = q.rename(columns={"level_1": 'Model', 0: 'Individuals', 'Group':'Risk group'})


ax2 = sns.barplot(x="Risk group", y="Individuals", hue="Model", data=q)
plt.xticks(rotation=-90)
plt.ylabel("Individuals")
plt.tight_layout()

html_figure("test2","large","Active cases by subgroup")


# ------------ active by year

h1("Active by year")

p('''
Comparison of the interventions using method one. Note, the intervention is 
more-or-less a placeholder.
''')



active_id = getStateIdByName("Active - untreated")

# for cycle in Cycle.query.all():
#   df.loc[df.Cycle_id == cycle.id, "Year"] = cycle.year


df["Active_cases_total"] = df.Risk_of_prog_total 




# & (df.Year > 2015)
qdf = df[(df.State_id == active_id) & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"]).Active_cases_total.sum() * Run_adjustment
qdf = qdf.reset_index()

ax = sns.tsplot(time="Year", value="Active_cases_total", unit="Iteration_num", condition="Intervention_name", data=qdf)
plt.xlabel('Year')
plt.ylabel('Active cases (annual)')
ax.get_xaxis().get_major_formatter().set_useOffset(False)


html_figure("comparison_of_interventions_year","large","Comparison of interventions with method 1")



p('''
Comparison of the interventions using method two.
''')

df[(df.State_name == "Life") & (df.Iteration_num == 0) & (df.Intervention_id == 0)][["Year","Population"]]

life_id = getStateIdByName("Life")

max_year = df.Year.max()

qdf = df[(df.State_id == life_id) & (df.Year > 2000) & (df.Year < 2055)].groupby(["Year", "Intervention_name", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment
qdf = qdf.reset_index()

# qdf = qdf.set_index(["Intervention_name", "Year", "Iteration_num"])

# colors = ["windows blue", "amber", "greyish", "faded green", "dusty purple"]
# plt.figure(figsize=(20,10))
# sns.palplot(sns.xkcd_palette(colors))


# from ---------- (to below) is specific for the CDC presentation

if Simulation_name == "med-risk-factor":
  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "1) Base case"
  qdf.loc[qdf.Intervention_name == "2x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "2) 2x the recruitment rate in those with medical risk factor, QFT/3PH"
  qdf.loc[qdf.Intervention_name == "4x in those with medical risk factors  (QFT/3HP)", "Intervention_name"] = "3) 4x the recruitment rate in those with medical risk factor, QFT/3PH"
  qdf.loc[qdf.Intervention_name == "10x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "4) 10x the recruitment rate in those with medical risk factor, QFT/3PH"

  colors = {
    "1) Base case" : 'Black',
    "2) 2x the recruitment rate in those with medical risk factor, QFT/3PH": '#d95f02',
    "3) 4x the recruitment rate in those with medical risk factor, QFT/3PH": '#7570b3',
    "4) 10x the recruitment rate in those with medical risk factor, QFT/3PH": '#e7298a'
  }

  qdf = qdf.sort("Intervention_name")

  labs = [ "Basecase", "2x the recruitment rate in those with medical risk factor", "4x the recruitment rate in those with medical risk factor", "10x the recruitment rate in those with medical risk factor"]

  ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", color=colors, data=qdf) # color={ 'Basecase': 'Black'},
  # plt.legend(labels=labs)


if Simulation_name == "fb":
  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "1) Base case"
  qdf.loc[qdf.Intervention_name == "2x in FB (QFT/3HP)", "Intervention_name"] = "2) 2x the recruitment rate in FB, QFT/3PH"
  qdf.loc[qdf.Intervention_name == "4x in FB (QFT/3HP)", "Intervention_name"] = "3) 4x the recruitment rate in FB, QFT/3PH"
  qdf.loc[qdf.Intervention_name == "10x in FB (QFT/3HP)", "Intervention_name"] = "4) 10x the recruitment rate in FB, QFT/3PH"

  colors = {
    "1) Base case" : 'Black',
    "2) 2x the recruitment rate in FB, QFT/3PH": '#d95f02',
    "3) 4x the recruitment rate in FB, QFT/3PH": '#7570b3',
    "4) 10x the recruitment rate in FB, QFT/3PH": '#e7298a'
  }

  qdf = qdf.sort("Intervention_name")

  ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", color=colors, data=qdf) # color={ 'Basecase': 'Black'},
  # plt.legend(labels=labs)


if Simulation_name == "full-pop":
  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "1) Base case"
  qdf.loc[qdf.Intervention_name == "2x in general population (QFT/3HP)", "Intervention_name"] = "2) 2x the recruitment rate, QFT/3PH"
  qdf.loc[qdf.Intervention_name == "4x in general population (QFT/3HP)", "Intervention_name"] = "3) 4x the recruitment rate, QFT/3PH"
  qdf.loc[qdf.Intervention_name == "10x in general population (QFT/3HP)", "Intervention_name"] = "4) 10x the recruitment rate, QFT/3PH"


  colors = {
    "1) Base case" : 'Black',
    "2) 2x the recruitment rate, QFT/3PH": '#d95f02',
    "3) 4x the recruitment rate, QFT/3PH": '#7570b3',
    "4) 10x the recruitment rate, QFT/3PH": '#e7298a'
  }

  qdf = qdf.sort("Intervention_name")

  ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", color=colors, data=qdf) # color={ 'Basecase': 'Black'},
  # plt.legend(labels=labs)

  # ---------- to here

else:
  ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", data=qdf)

plt.axhline(y= 39*3/2, color='black', linestyle=':', linewidth=2, alpha=0.5)

plt.legend(title="Interventions")
plt.xlabel('Year')
plt.ylabel('Active cases (annual)')
ax.get_xaxis().get_major_formatter().set_useOffset(False)

html_figure("comparison_of_interventions_2_year","large","Comparison of interventions with method 2")


# ------------ active by cycle

h1("Active by cycle")

p('''
Comparison of the interventions using method one. Note, the intervention is 
more-or-less a placeholder.
''')




active_id = getStateIdByName("Active - untreated")

# for cycle in Cycle.query.all():
#   df.loc[df.Cycle_id == cycle.id, "Year"] = cycle.year

maxYear = df.Year.max()



df["Active_cases_total"] = df.Risk_of_prog_total


# & (df.Year > 2015)
qdf = df[(df.State_id == active_id) & (df.Cycle_id > 0)].groupby(["Cycle_id", "Intervention_name", "Iteration_num"]).Active_cases_total.sum() * Run_adjustment
qdf = qdf.reset_index()


ax = sns.tsplot(time="Cycle_id", value="Active_cases_total", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)

html_figure("comparison_of_interventions","large","Comparison of interventions with method 1")



p('''
Comparison of the interventions using method two.
''')


life_id = getStateIdByName("Life")

df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb

qdf = df[(df.State_id == life_id) & (df.Cycle_id > 0)].groupby(["Cycle_id", "Intervention_name", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment
qdf = qdf.reset_index()

ax = sns.tsplot(time="Cycle_id", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)

html_figure("comparison_of_interventions_2","large","Comparison of interventions with method 2")


# --------------- transmission ---------------------------

# recent transmission
df.loc[:, "Prop Active FB RT"] = df.Recent_transmission_fb_rop / df.Risk_of_prog_fb
df.loc[:, "Prop Active US RT"] = df.Recent_transmission_us_rop / df.Risk_of_prog_us



# ------- by year
h3("Transmission - by year")


p("within us")

# within US transmission

  
qdf = df[(df.State_name == "Fast latent") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"]).Transmission_within_us.sum() * Run_adjustment
qdf = qdf.reset_index()

# embed()

ax = sns.tsplot(time="Year", value="Transmission_within_us", unit="Iteration_num", condition="Intervention_name",  data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("transmission within us by year","large","Comparison of interventions with method 1")


qdf = df[df.State_name == "Life"].fillna(0)
# embed()


# ------- by year
h3("Transmission - cases due to RT (within CA infection)")

qdf = df[(df.State_name == "Life") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"])["Recent_transmission_fb_rop"].sum() * Run_adjustment
qdf = qdf.reset_index()
p("cases due to RT (within CA infection) fb - defined by <36 mo")
ax = sns.tsplot(time="Year", value="Recent_transmission_fb_rop", unit="Iteration_num", condition="Intervention_name", data=qdf) # err_style="unit_traces",
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("total RT cases fb by year","large","Comparison of interventions with method 1")


qdf = df[(df.State_name == "Life") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"])["Recent_transmission_us_rop"].sum() * Run_adjustment
qdf = qdf.reset_index()
p("cases due to RT (within CA infection) usb - defined by <36 mo")
ax = sns.tsplot(time="Year", value="Recent_transmission_us_rop", unit="Iteration_num", condition="Intervention_name", data=qdf) #err_style="unit_traces", 
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("total RT cases us by year","large","Comparison of interventions with method 1")




h3("Transmission - % cases due to RT (within CA infection)")


qdf = df[(df.State_name == "Life") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"])["Prop Active FB RT"].mean()
qdf = qdf.reset_index()
p("prop active RT fb - defined by <36 mo")
ax = sns.tsplot(time="Year", value="Prop Active FB RT", unit="Iteration_num", condition="Intervention_name", data=qdf) # err_style="unit_traces",
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("prop recent fb by year","large","Comparison of interventions with method 1")


qdf = df[(df.State_name == "Life") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"])["Prop Active US RT"].mean()
qdf = qdf.reset_index()
p("prop active RT usb - defined by <36 mo")
ax = sns.tsplot(time="Year", value="Prop Active US RT", unit="Iteration_num", condition="Intervention_name", data=qdf) #err_style="unit_traces", 
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("prop recent us by year","large","Comparison of interventions with method 1")






h3("Risk of infection")


qdf = df[(df.State_name == "Uninfected TB") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"])["Risk_of_infection_fb"].sum() * Run_adjustment
qdf = qdf.reset_index()

p("risk of infection fb")
ax = sns.tsplot(time="Year", value="Risk_of_infection_fb", unit="Iteration_num", condition="Intervention_name",  data=qdf) #err_style="unit_traces",
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("roi fb by year","large","Comparison of interventions with method 1")

qdf = df[(df.State_name == "Uninfected TB") & (df.Year > 2000)].groupby(["Year", "Intervention_name", "Iteration_num"])["Risk_of_infection_us"].sum() * Run_adjustment
qdf = qdf.reset_index()
p("risk of infection usb")
ax = sns.tsplot(time="Year", value="Risk_of_infection_us", unit="Iteration_num", condition="Intervention_name",  data=qdf) #err_style="unit_traces",
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("roi us by year","large","Comparison of interventions with method 1")


# -------- by cycle



# --------------- ROP
# THESE AREN'T RIGHT BECAUSE THE DENOMINATOR IS SLOW PLUS FAST BUT THATS NOT EVERYONE THAT IS INFECTED (treated, in treatment)


# ----- all infected

h3("Average ROP - by cycle - all infecteds")

p("usb - all infecteds")

df.loc[:, "Avg ROP usb"] = df["Risk_of_prog_us"] * 12 * 100000.0 / (df["Slow_latents_us"] + df["Fast_latents_us"])
qdf = df[df.State_name == "Life"].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Avg ROP usb"].mean().reset_index()
ax = sns.tsplot(time="Cycle_id", value="Avg ROP usb", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.ylabel('ROP per 100,000 PY')
html_figure("averge_rop_usb","large","averge_rop_usb")


p("fb - all infecteds")

df.loc[:, "Avg ROP fb"] = df["Risk_of_prog_fb"] * 12 * 100000.0 / (df["Slow_latents_fb"] + df["Fast_latents_fb"])
qdf = df[df.State_name == "Life"].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Avg ROP fb"].mean().reset_index()
ax = sns.tsplot(time="Cycle_id", value="Avg ROP fb", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.ylabel('ROP per 100,000 PY')
html_figure("averge_rop_fb","large","averge_rop_fb")


# ----- slow latent only

h3("Average ROP - by cycle - slow latent  (remote infection)")

p("usb - slow latent  (remote infection)")

df.loc[:, "Avg ROP usb"] = df["Risk_of_prog_us"] * 12 * 100000.0 / (df["Slow_latents_us"] + df["Fast_latents_us"])
qdf = df[df.State_name == "Slow latent"].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Avg ROP usb"].mean().reset_index()
ax = sns.tsplot(time="Cycle_id", value="Avg ROP usb", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.ylabel('ROP per 100,000 PY')
html_figure("averge_rop_usb_slow","large","averge_rop_usb_slow")


p("fb - slow latents (remote infection)")

df.loc[:, "Avg ROP fb"] = df["Risk_of_prog_fb"] * 12 * 100000.0 / (df["Slow_latents_fb"] + df["Fast_latents_fb"])
qdf = df[df.State_name == "Slow latent"].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Avg ROP fb"].mean().reset_index()
ax = sns.tsplot(time="Cycle_id", value="Avg ROP fb", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.ylabel('ROP per 100,000 PY')
html_figure("averge_rop_fb_slow","large","averge_rop_fb_slow")






h3("Transmission - by cycle")


p("within us")

# within US transmission


qdf = df[(df.State_name == "Fast latent")].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Transmission_within_us"].mean().reset_index()

ax = sns.tsplot(time="Cycle_id", value="Transmission_within_us", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("transmission within us","large","Comparison of interventions with method 1")




# qdf = df[df.State_name == "Life"].fillna(0)
# embed()

qdf = df[(df.State_name == "Life")].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Prop Active FB RT"].mean().reset_index()
p("prop active RT fb")
ax = sns.tsplot(time="Cycle_id", value="Prop Active FB RT", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("prop recent fb","large","Comparison of interventions with method 1")

qdf = df[(df.State_name == "Life")].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Prop Active US RT"].mean().reset_index()
p("prop active RT usb")
ax = sns.tsplot(time="Cycle_id", value="Prop Active US RT", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("prop recent us","large","Comparison of interventions with method 1")

qdf = df[(df.State_name == "Uninfected TB")].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Risk_of_infection_fb"].mean().reset_index()
# qdf = df[df.State_name == "Uninfected TB"].fillna(0)
p("risk of infection fb")
ax = sns.tsplot(time="Cycle_id", value="Risk_of_infection_fb", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("roi fb","large","Comparison of interventions with method 1")

qdf = df[(df.State_name == "Uninfected TB")].groupby(["Cycle_id", "Intervention_name", "Iteration_num"])["Risk_of_infection_us"].mean().reset_index()
p("risk of infection usb")
ax = sns.tsplot(time="Cycle_id", value="Risk_of_infection_us", unit="Iteration_num", condition="Intervention_name", data=qdf)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
html_figure("roi us","large","Comparison of interventions with method 1")





# --------------- costs ---------------------------

h3("Cost effectiveness summary")


in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]


# embed()

intervention_names = []
for intervention_id in intervention_ids:
  intervention_names.append(pd.unique(df[df.Intervention_id == intervention_id].Intervention_name)[0])


results_df = pd.DataFrame(index=[i for i in intervention_names])



# if Is_closed_cohort:
#   Run_adjustment = 1


for intervention_id in intervention_ids:

  intervention_name = intervention_names[intervention_id]


  ldf = df[(df.Intervention_id == intervention_id)]

  # embed()

  # Treatment costs
  results_df.loc[intervention_name, "true_positive_treatment_costs_base"] = ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
  results_df.loc[intervention_name, "true_positive_treatment_costs_low"] =  ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
  results_df.loc[intervention_name, "true_positive_treatment_costs_high"] = ldf[ldf.State_name.isin(in_treatment_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

  # FP Treatment costs
  results_df.loc[intervention_name, "false_positive_treatment_costs_base"] = ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
  results_df.loc[intervention_name, "false_positive_treatment_costs_low"] =  ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
  results_df.loc[intervention_name, "false_positive_treatment_costs_high"] = ldf[ldf.State_name.isin(fp_in_treatment_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

  # Testing costs
  results_df.loc[intervention_name, "testing_costs_base"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
  results_df.loc[intervention_name, "testing_costs_low"] =  ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
  results_df.loc[intervention_name, "testing_costs_high"] = ldf[ldf.State_name.isin(testing_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

  # Active disease costs
  results_df.loc[intervention_name, "active_disease_costs_base"] = ldf[ldf.State_name.isin(active_disease_states)].groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
  results_df.loc[intervention_name, "active_disease_costs_low"] =  ldf[ldf.State_name.isin(active_disease_states)].groupby("Iteration_num").Costs.sum().min() * Run_adjustment
  results_df.loc[intervention_name, "active_disease_costs_high"] = ldf[ldf.State_name.isin(active_disease_states)].groupby("Iteration_num").Costs.sum().max() * Run_adjustment

  # Total costs
  results_df.loc[intervention_name, "total_costs_base"] = ldf.groupby("Iteration_num").Costs.sum().mean() * Run_adjustment
  results_df.loc[intervention_name, "total_costs_low"] =  ldf.groupby("Iteration_num").Costs.sum().min() * Run_adjustment
  results_df.loc[intervention_name, "total_costs_high"] = ldf.groupby("Iteration_num").Costs.sum().max() * Run_adjustment

  # Total active TB cases
  results_df.loc[intervention_name, "active_cases_m2_base"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().mean() * Run_adjustment
  results_df.loc[intervention_name, "active_cases_m2_low"] =  ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().min() * Run_adjustment
  results_df.loc[intervention_name, "active_cases_m2_high"] = ldf[ldf.State_name == "Life"].groupby("Iteration_num").Risk_of_prog_total.sum().max() * Run_adjustment

  # Cost compared to control
  results_df.loc[intervention_name, "cost_compared_to_control"] =  results_df.loc[intervention_name, "total_costs_base"] - results_df.loc["Basecase", "total_costs_base"] 

  # Active cases averted
  results_df.loc[intervention_name, "active_cases_averted"] =  results_df.loc["Basecase", "active_cases_m2_base"] - results_df.loc[intervention_name, "active_cases_m2_base"] 

  # Cost per averted case
  results_df.loc[intervention_name, "cost_per_case_averted"] =  results_df.loc[intervention_name, "cost_compared_to_control"] / results_df.loc[intervention_name, "active_cases_averted"]


to_html(results_df.T.to_html(classes="table table-striped"))


# embed()




h3("Costs by cycle")



in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]
fp_in_treatment_states = [ "FP LBTI 9m INH - Month 1", "FP LBTI 9m INH - Month 2", "FP LBTI 9m INH - Month 3", "FP LBTI 9m INH - Month 4", "FP LBTI 9m INH - Month 5", "FP LBTI 9m INH - Month 6", "FP LBTI 9m INH - Month 7", "FP LBTI 9m INH - Month 8", "FP LBTI 9m INH - Month 9", "FP LTBI 6m INH - Month 1", "FP LTBI 6m INH - Month 2", "FP LTBI 6m INH - Month 3", "FP LTBI 6m INH - Month 4", "FP LTBI 6m INH - Month 5", "FP LTBI 6m INH - Month 6", "FP LTBI RIF - Month 1", "FP LTBI RIF - Month 2", "FP LTBI RIF - Month 3", "FP LTBI RIF - Month 4", "FP LTBI RTP - Month 1", "FP LTBI RTP - Month 2", "FP LTBI RTP - Month 3" ]
active_disease_states = [ "Active Treated Month 1", "Active Treated Month 2", "Active Treated Month 3", "Active Treated Month 4", "Active Treated Month 5", "Active Treated Month 6"] 
testing_states = [ "Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT", "Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT" ]

groupings =[ 
                { 
                    'name' : 'LTBI treatment costs', 
                    'contents' : in_treatment_states
                },
                { 
                    'name' : 'False positive treatment costs', 
                    'contents' : fp_in_treatment_states
                },
                { 
                    'name' : 'Active disease treatment', 
                    'contents' : active_disease_states
                },
                { 
                    'name' : 'Testing costs', 
                    'contents' : testing_states
                },
            ]

# cdf = df.copy()



for intervention_id in intervention_ids:
  results_df = pd.DataFrame(columns=[ group['name'] for group in groupings ])
  h4(intervention_names[intervention_id])
  for group in groupings:
    cdf = df.copy()
    cdf = cdf[cdf.State_name.isin(group['contents'])]
    piv = pd.pivot_table(cdf[cdf.Intervention_id == intervention_id], values="Costs", index="Cycle_id", columns=['State_name'], aggfunc=np.mean)
    results_df.loc[:,group['name']] = piv.T.sum()
  results_df.plot(kind="area")
  plt.xlabel("Month")
  plt.ylabel("Costs (monthly, USD)")
  html_figure(str(intervention_id) + "costs over time","large",str(intervention_id) + "costs over time")






# -------------- treatment --------------------------

h3("Prevalence of LTBI")




in_treatment_states = [ 'LBTI 9m INH - Month 1', 'LBTI 9m INH - Month 2', 'LBTI 9m INH - Month 3', 'LBTI 9m INH - Month 4', 'LBTI 9m INH - Month 5', 'LBTI 9m INH - Month 6', 'LBTI 9m INH - Month 7', 'LBTI 9m INH - Month 8', 'LBTI 9m INH - Month 9', 'LTBI 6m INH - Month 1', 'LTBI 6m INH - Month 2', 'LTBI 6m INH - Month 3', 'LTBI 6m INH - Month 4', 'LTBI 6m INH - Month 5', 'LTBI 6m INH - Month 6', 'LTBI RIF - Month 1', 'LTBI RIF - Month 2', 'LTBI RIF - Month 3', 'LTBI RIF - Month 4', 'LTBI RTP - Month 1', 'LTBI RTP - Month 2', 'LTBI RTP - Month 3' ]

in_completion_states = ['LTBI treated with INH 9m', 'LTBI treated with INH 6m', 'LTBI treated with RIF', 'LTBI treated with RTP' ] 

groupings =[ 
                { 
                    'name' : 'LTBI Fast (RT)', 
                    'contents' : ['Fast latent']
                },
                { 
                    'name' : 'LTBI Slow', 
                    'contents' : ['Slow latent']
                },
                { 
                    'name' : 'In LTBI Treatment', 
                    'contents' : in_treatment_states
                },
                { 
                    'name' : 'Completed LTBI Treatment', 
                    'contents' : in_completion_states
                },
                { 
                    'name' : 'Uninitialized', 
                    'contents' : ['Uninitialized']
                }

            ]


for intervention_id in intervention_ids:
  p("intervention " + str(intervention_id))
  prevalence_chart("TB disease and treatment", df, groupings, intervention_id, "Treatment and Active Cases")
  html_figure("ltbi_treatment_prev_control"+str(intervention_id),"large","Caption")


h3("Prevalence of treated LTBI")


in_completion_states = ['LTBI treated with INH 9m', 'LTBI treated with INH 6m', 'LTBI treated with RIF', 'LTBI treated with RTP' ] 

groupings =[ 
                { 
                    'name' : 'Completed LTBI Treatment', 
                    'contents' : in_completion_states
                }

            ]



p("In control")
prevalence_chart("TB disease and treatment", df, groupings, 0, "Treatment and Active Cases")
html_figure("ltbi_treatment_prev_control_treated","large","Caption")


h3("proportion of LTBI treated w 6m INH")


for i in range(0,df.Cycle_id.max()):
  if i % 12 == 0:
    slow_lats = float(df[(df.Cycle_id == i) & (df.Intervention_id == 0) & (df.Iteration_num == 0) & (df.State_name == "Slow latent")]["Population"])
    fast_lats = float(df[(df.Cycle_id == i) & (df.Intervention_id == 0) & (df.Iteration_num == 0) & (df.State_name == "Fast latent")]["Population"])
    treated = float(df[(df.Cycle_id == i) & (df.Intervention_id == 0) & (df.Iteration_num == 0) & (df.State_name == "LTBI treated with INH 6m")]["Population"])
    p(" cycle " + str(i) + ":" + str(treated/(slow_lats+fast_lats)))


h3("Prevalence of fast latent")


groupings =[ 
                { 
                    'name' : 'Fast latent (RT)', 
                    'contents' : ['Fast latent']
                }

            ]


prevalence_chart("TB disease and treatment", df, groupings, 0, "Treatment and Active Cases")
html_figure("ltbi_treatment_prev_control_fast","large","Caption")

# p("In intervention 1")
# prevalence_chart("TB disease and treatment", df, groupings, 1, "Treatment and Active Cases")
# html_figure("ltbi_treatment_prev_intervention1","large","Caption")

# p("In intervention")
# prevalence_chart(df, groupings, 1, "Treatment and Active Cases")
# html_figure("ltbi_treatment_prev_intervention","large","Caption")




print "Replacing"
for state in State.query.all():
  print state.name
  df.loc[ df.State_id == state.id, "State_name"] = state.name
print "FINISHED replacing"








# -------- Graph -------------


if Include_images:

  # column description in YAML, my favorite way of showing structured data
  g = """
      - Total:
        chain_name: Natural death
        state_names: 
          - Life

      - HIV:
        chain_name: HIV
        state_names:
          - Infected HIV, no ART
          - Infected HIV, ART
      - Diabetes:
        chain_name: Diabetes
        state_names:
          - Diabetes
      - ESRD:
        chain_name: ESRD
        state_names:
          - ESRD
      - Smoking:
        chain_name: Smoking
        state_names:
          - Smoker
      - Transplants:
        chain_name: Transplants
        state_names:
          - Transplant patient
      - TNF-aplha:
        chain_name: TNF-alpha
        state_names:
          - TNF-alpha
  """

  groupings = yaml.load(g)


  # excluded for now
  '''
      - Asian:
        chain_name: Race
        state_names:
          - Asian
          - Hispanic
          - Black
          - White
          - Other
      - Male:
        chain_name: Sex
        state_names:
          - Male
          - Female
      - Homeless:
        chain_name: Homeless
        state_names: 
          - Homeless
      - Alcohol:
        chain_name: Alcohol
        state_names:
          - Alcohol
      - IDU:
        chain_name: HIV risk groups
        state_names:
          - IDU
          - MSM
      - IDU:
        chain_name: Medical risk factor
        state_names:
          - Medical risk factor
  '''

  h3("Risk factor prevalence")

  for group in groupings:
    chain_name = group["chain_name"]
    state_names = group["state_names"]
    print chain_name
    h4(chain_name)
    state_ids = [ State.query.filter_by(name=state_name).first().id for state_name in state_names ]
    rdf = df[(df.State_id.isin(state_ids)) & (df.Intervention_id == 0)]
    rdf["Population"] = rdf["Population"] * Run_adjustment

    rdf2 = rdf[(rdf.Year > 2000)].groupby(["Year","Iteration_num"]).Population.mean().reset_index()
    rdf2["Source"] = "CAPE"

    rdf3 = rdf2[rdf2.Iteration_num == 0].copy()
    rdf3["Source"] = "Calibration"

    calib_df = pd.read_csv("raw-data-files/risk_factor_calib.csv")


    for i, row in rdf3.iterrows():
      if int(row["Year"]) < 2015:
        rdf3.loc[i, "Population"] = float(calib_df[calib_df.Year == row["Year"]][chain_name])
      else:
        rdf3.loc[i, "Population"] = 0

    full = rdf2.append(rdf3)

    ax = sns.tsplot(time="Year", value="Population", unit="Iteration_num", condition="Source", data=full) #, err_style="unit_traces")
    html_figure("groups_in_"+chain_name,"large",chain_name + " prevalence")


  # chain_names = get_all_chain_names()
  # for chain_name in chain_names:
  #   print chain_name
  #   h3(chain_name)
  #   state_ids = [ state.id for state in Chain.query.filter_by(name=chain_name).first().states ]
  #   rdf = df[(df.State_id.isin(state_ids)) & (df.Intervention_id == 0)]
  #   ax = sns.tsplot(time="Cycle_id", value="Population", unit="Iteration_num", condition="State_name", data=rdf)
  #   html_figure("prev_in_"+chain_name,"large","Here is a caption")

h3("Population by race nativity")

rn_df = pd.read_csv("raw-data-files/race_nativitiy_pop_from_ipums.csv")
races = ["Hispanic", "White", "Black", "Asian", "Other"]
nativities = ["USB", "FB"]
years = range(2001,2015)
for year in years:
    for race in races:
        for nativity in nativities:
            race_nativity = race + " " + nativity
            rn_df.loc[len(rn_df), "RN"] = race_nativity
            rn_df.loc[len(rn_df)-1, "Year"] = year
            rn_df.loc[len(rn_df)-1, "Source"] = "CAPE"
            if nativity == "USB":
                rn_df.loc[len(rn_df)-1, "Population"] = df[(df.Year == year) & (df.State_name == race)].Population_us.mean() * Run_adjustment
            else:
                rn_df.loc[len(rn_df)-1, "Population"] = df[(df.Year == year) & (df.State_name == race)].Population_fb.mean() * Run_adjustment
rn_df["Dummy"] = 1

for race in races:
  for nativity in nativities:
      rn = race + " " + nativity
      h4(rn)
      plt.clf()
      ax = sns.tsplot(time="Year", value="Population", unit="Dummy", condition="Source", data=rn_df[(rn_df.RN == rn)])
      html_figure("rn_"+race+"_"+nativity,"large","Here is a caption")


#  TODO CAN modify to use same method as above, not use the json -------------------------------------------

h3("Active TB cases in risk groups in basecase")

# embed()

# -------- model data

# old (faster) way - but does not show error bars!
# m_df = pd.read_json("go/tmp/model_calib_results.json")
# # sum all the CaseAverages (so as reported by year not month)
# model_df = pd.DataFrame()
# model_df["CasesAverage"] = m_df.groupby(["Nativity", "Year", "Group"]).CasesAverage.sum()
# model_df = model_df.reset_index()
# model_df["Source"] = "CAPE"
# # model_df[(model_df.Group == "HIV") & (model_df.Nativity == "USB")]

m_df = pd.DataFrame(columns=['Nativity', 'Year', 'Group', 'CasesAverage', 'Source', 'Iteration'])

for i, row in df[df.Intervention_id == 0].iterrows():
  states_of_interest = ["Life", "Homeless", "Infected HIV, no ART", "Infected HIV, ART", "Diabetes", "ESRD", "Smoker", "Transplant patient", "TNF-alpha", "Asian", "Black", "Hispanic", "Other", "White", "Male", "Female", "Less than one year", "Fast latent"]
  if row["State_name"] in (states_of_interest):
    # convert state names to match data sources
    group = row["State_name"] 
    group = group.replace("Life", "Total")
    group = group.replace("Infected HIV, no ART", "HIV")
    group = group.replace("Infected HIV, ART", "HIV")
    group = group.replace("Smoker", "Smokers")
    group = group.replace("Transplant patient", "Transplant")
    group = group.replace("Less than one year", "Imported")
    group = group.replace("Fast latent", "Recent transmission")


    year = row["Year"]
    source = "CAPE"

    usb_cases = row["Risk_of_prog_us"]
    fb_cases = row["Risk_of_prog_fb"]

    iteration = row["Iteration_num"]

    # USB
    m_df.loc[len(m_df)] = ["USB", year, group, usb_cases, source, iteration]
    # FB
    m_df.loc[len(m_df)] = ["FB", year, group, fb_cases, source, iteration]


model_df = m_df.groupby(["Nativity", "Year", "Group", "Iteration"]).CasesAverage.sum().reset_index()


model_df["CasesAverage"] = model_df["CasesAverage"] * Run_adjustment
model_df["Source"] = "CAPE"




rvct_df = pd.read_excel("raw-data-files/rvct_calib_data.xlsx", sheetname="Final")
rvct_df["Iteration"] = 0
 
full_df = model_df.append(rvct_df).convert_objects(convert_numeric=True)


full_df["Label"] = full_df.apply(lambda x: x["Source"] + " " + x["Nativity"], axis=1)
full_df = full_df.reset_index(drop=True)
full_df["Dummy"] = 0
# full_df = full_df[full_df.Year > 2000]




groups = pd.unique(rvct_df.Group).tolist()
groups.remove('Homeless')
groups.remove('Alcohol')
groups.remove('IDU')

# embed()
for group in groups:
  plt.clf()
  h4(group)
  ax = sns.tsplot(time="Year", value="CasesAverage", unit="Iteration", interpolate=True, condition="Label", data=full_df[(full_df.Group == group) & (full_df.Year > 2000)])#, err_style="unit_traces")
  html_figure("calib_"+group,"large","Here is a caption")



# ------------ attributable cases


h3("Atributable cases over time")

tnf_rr = 4.7
dm_rr = 1.6
trans_rr = 2.4
hiv_rr = 5.4
esrd_rr = 11.0
smoking_rr = 2.5

ar_df = model_df.copy()
ar_df.CasesAverage = 0

groups = [ 'Diabetes', 'HIV', 'Transplant', 'ESRD', 'Smokers', 'TNF-alpha', 'Recent transmission', 'Imported', 'Total']
group_risks = [ dm_rr, hiv_rr, trans_rr, esrd_rr, smoking_rr, tnf_rr]
for i in range(0,len(groups)):
  if groups[i] == "Recent transmission" or groups[i] ==  "Imported" or groups[i] == 'Total':
    ar_df.loc[ar_df.Group == groups[i], "CasesAverage"] = model_df[model_df.Group == groups[i]].CasesAverage
  else:
    ar_df.loc[ar_df.Group == groups[i], "CasesAverage"] = model_df[model_df.Group == groups[i]].CasesAverage * ((group_risks[i] - 1.0)/group_risks[i])

ar_df2 = ar_df[ar_df.Nativity == "USB"]
ar_df2.loc[:, "Nativity"] = "Total"

ar_df2 = ar_df.groupby(["Group","Iteration","Year"]).CasesAverage.sum().reset_index()

ar_df3 = ar_df2.groupby(["Group","Year"]).CasesAverage.mean().reset_index()

ar_df3 = ar_df3[ar_df3.Group.isin(groups)]
ar_df3 = ar_df3[(ar_df3.Year > 2000) & (ar_df3.Year < 2015)]

piv = pd.pivot_table(ar_df3, values="CasesAverage", index="Year", columns="Group")
piv["Remaining"] = piv["Total"] - (piv["Diabetes"] + piv["ESRD"] + piv["HIV"] + piv["Imported"] + piv["Recent transmission"] + piv["Smokers"] + piv["TNF-alpha"] + piv["Transplant"])
piv.to_csv("piv.csv")

# ax = sns.tsplot(time="Year", value="CasesAverage", unit="Iteration", interpolate=True, condition="Group", data=ar_df3[(ar_df3.Year > 2000) & (ar_df2.Year < 2015)])

# html_figure("ar_chart","large","Here is a caption")





# -------- rvct data


print "Ploted data!"

# also, dump calibration CSV into YAML format so that Go can use it for calibration
# i've set up calibration in Go to use tree-based data (arrays of arrays)
# instead of tabular-based data (array of complex objects) since it is faster


groups = pd.unique(full_df.Group)
years = pd.unique(rvct_df.Year)
nativites = pd.unique(rvct_df.Nativity)

# create dictionary
year_group_nativity = {}


# for y, year in enumerate(years):
#   year_group_nativity[str(year)] = {}
#   for g, group in enumerate(groups):
#     year_group_nativity[str(year)][group] = {}
#     for n, nativity in enumerate(nativites):
#       q = full_df[(full_df.Source == "RVCT") &
#         (full_df.Year == year) & 
#         (full_df.Group == group) & 
#         (full_df.Nativity == nativity)].CasesAverage
#       print year, group, nativity, q
#       year_group_nativity[str(year)][group][nativity] = float(q)

# #full_df[(full_df.Source == "RVCT") & (full_df.Year == "2000") & (full_df.Group == "Recent transmission") & (full_df.Nativity == "USB")].CasesAverage

# fo = open("rvct.yaml", "w+")
# fo.write(yaml.dump(year_group_nativity))

print "Dumped calibration data! Done"









save_outputs()

embed()

# Html = ""

# def slide(txt):
#   global Html
#   to_add = '''
#   <div class="break"></div>
#   <div class="slide_outer">
#     <div class="slide_middle">
#       <div class="slide_inner">
#         {0}
#       </div>
#     </div>
#   </div>
#   '''
#   to_add = to_add.format(txt)
#   Html += to_add


# q = cdph_df[["Exp Latents Total", "Est Latents Total", "Latents Total base limcat", "Group"]]
# # q = q.rename(columns={"Tot Pop CDPH": 'CDPH', "Pop Total base limcat": 'LIMCAT'})
# q = q.set_index("Group").stack().reset_index()
# q = q.rename(columns={"level_1": 'Model', 0: 'Individuals', 'Group':'Risk group'})


# ax2 = sns.barplot(x="Risk group", y="Individuals", hue="Model", data=q)
# plt.xticks(rotation=-90)
# plt.ylabel("Individuals")
# plt.tight_layout()


# filename = "slide" + ".png"
# plt.savefig(Html_dir + Image_dir + filename, bbox_inches='tight',  figsize=(8, 6), dpi=200)
# plt.clf()
# img_template = '''
#         <p> <img src="{0}" class="{1}"/> 
#         '''
# img_template = img_template.format(Image_dir + filename, "large")




# slide("hello world")
# slide("hello world2")
# slide("<h3> Title </h3> " +img_template)
# slide("<h3> Title </h3> " +img_template)



# f = open("templates/slide_template.html", 'r')
# template = f.read()
# f.close()
# revised_template = re.sub(r'\s{{content}}\s', Html, template)
# f = open(Html_dir + Output_name + "_slides.html", 'w+')
# f.write(revised_template)
# f.close()






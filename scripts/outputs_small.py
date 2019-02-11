
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



   

def add_to_cdph_table(cdph_df, df, group, intervention_id, begin_cycle, end_cycle):
  
  
  global Run_adjustment

  cdph_col_name = group["cdph_col_name"]
  limcat_col_name  = group["limcat_col_name"]
  limcat_state_names  = group["limcat_state_names"]
  limcat_state_ids = [ getStateIdByName(name) for name in limcat_state_names]

  
  
  latent_id = getStateIdByName("Slow latent")
  active_id = getStateIdByName("Active - untreated")
  # not_fb_id = getStateIdByName("Not Foreign-born")
  # fb1_id = getStateIdByName("Less than one year")
  # fb2_id = getStateIdByName("Between one and 5 years")
  # fb3_id = getStateIdByName("5 or more years")
  # fb = [ fb1_id, fb2_id, fb3_id ]
  # total = [ not_fb_id, fb1_id, fb2_id, fb3_id ]

  # embed()
  conv = {}


  first_cycle_of_2014 = df[df.Year == 2014].Cycle_id.min()
  last_cycle_of_2014 = df[df.Year == 2014].Cycle_id.max()

  begin_cycle = first_cycle_of_2014
  end_cycle = last_cycle_of_2014

  #  Active disease is based on cycles 4-15 cycles (representing one year)
  #  We skip the first few cycles since they are often odd (ie, incldue imported cases etc)
  qdf = df[(df.Cycle_id <= end_cycle) & (df.Cycle_id >= begin_cycle)  & (df.Intervention_id == intervention_id) & (df.State_id.isin(limcat_state_ids))]

  conv['Active'] = {}
  conv['Active']['FB'] = qdf.groupby("Iteration_num").Active_cases_fb.sum()
  conv['Active']['US'] = qdf.groupby("Iteration_num").Active_cases_us.sum()
  conv['Active']['Total'] = qdf.groupby("Iteration_num").Active_cases_fb.sum() + qdf.groupby("Iteration_num").Active_cases_us.sum()


  conv['Active M2'] = {}
  conv['Active M2']['FB'] = qdf.groupby("Iteration_num").Risk_of_prog_fb.sum()
  conv['Active M2']['US'] = qdf.groupby("Iteration_num").Risk_of_prog_us.sum()
  conv['Active M2']['Total'] = qdf.groupby("Iteration_num").Risk_of_prog_fb.sum() + qdf.groupby("Iteration_num").Risk_of_prog_us.sum()

  # Population and latent are reported from first cycle of 2014
  rdf = df[(df.Cycle_id == first_cycle_of_2014) & (df.Intervention_id == 0) & (df.State_id.isin(limcat_state_ids))]


  conv['Latents'] = {}
  conv['Latents']['FB']    = rdf.Slow_latents_fb
  conv['Latents']['US']    = rdf.Slow_latents_us
  conv['Latents']['Total'] = rdf.Slow_latents_fb + rdf.Slow_latents_us

  conv['Pop'] = {}
  conv['Pop']['FB'] = rdf.Population_fb
  conv['Pop']['US'] = rdf.Population_us
  conv['Pop']['Total'] = rdf.Population_fb + rdf.Population_us

  for x in ['Latents', 'Active', 'Active M2', 'Pop']:
    for y in ['FB', 'US', 'Total']:
      for z in [ 'base', 'low', 'high', 'composite']:



        col_name = '{0} {1} {2} {3}'.format(x,y,z,"limcat")
        p = conv[x][y]


        ########### !!!!!!!!!!!!!!!!!!!! Can't get mean when mutliple lines ??
        r = {}
        r["base"] = float(p.mean()) * Run_adjustment # used to be p.mean().sum()
        r["low"] = float(p.min()) * Run_adjustment
        r["high"] = float(p.max()) * Run_adjustment

        r["composite"] = "{0} ({1} - {2})".format(commas(r["base"]), commas(r["low"]), commas(r["high"]))

        cdph_df.loc[cdph_df["Group"] == cdph_col_name, col_name] = r[z]
    

  return cdph_df

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


  # column description in YAML, my favorite way of showing structured data
  g = """
      - Total:
        cdph_col_name: Total
        limcat_col_name: Natural death
        limcat_state_names: 
          - Life
      - Homeless:
        cdph_col_name: Homeless
        limcat_col_name: Homeless
        limcat_state_names: 
          - Homeless
      - HIV:
        cdph_col_name: HIV infected (HIV/AIDS)
        limcat_col_name: HIV
        limcat_state_names:
          - Infected HIV, no ART
          - Infected HIV, ART
      - Diabetes:
        cdph_col_name: Diabetes
        limcat_col_name: Diabetes
        limcat_state_names:
          - Diabetes
      - ESRD:
        cdph_col_name: End-stage renal disease (ESRD)
        limcat_col_name: ESRD
        limcat_state_names:
          - ESRD
      - Smoking:
        cdph_col_name: Smokers
        limcat_col_name: Smoking
        limcat_state_names:
          - Smoker
      - Transplants:
        cdph_col_name: Transplant
        limcat_col_name: Transplants
        limcat_state_names:
          - Transplant patient
      - TNF-aplha:
        cdph_col_name: TNF-alpha
        limcat_col_name: TNF-alpha
        limcat_state_names:
          - TNF-alpha
      - Asian:
        cdph_col_name: Asian
        limcat_col_name: Race
        limcat_state_names:
          - Asian
      - Hispanic:
        cdph_col_name: Hispanic
        limcat_col_name: Race
        limcat_state_names:
          - Hispanic
      - Black:
        cdph_col_name: Black
        limcat_col_name: Race
        limcat_state_names:
          - Black
      - White:
        cdph_col_name: White
        limcat_col_name: Race
        limcat_state_names:
          - White
      - Other:
        cdph_col_name: Other
        limcat_col_name: Race
        limcat_state_names:
          - Other
      - Male:
        cdph_col_name: Male
        limcat_col_name: Sex
        limcat_state_names:
          - Male
      - Female:
        cdph_col_name: Female
        limcat_col_name: Sex
        limcat_state_names:
          - Female
      - Alcohol:
        cdph_col_name: Alcohol
        limcat_col_name: Alcohol
        limcat_state_names:
          - Alcohol
      - IDU:
        cdph_col_name: IDU
        limcat_col_name: HIV risk groups
        limcat_state_names:
          - IDU
      - Imported TB:
        cdph_col_name: Imported cases ie < 1 year in US
        limcat_col_name: Length of time in US
        limcat_state_names:
          - Less than one year
  """


  groupings = yaml.load(g)

  cdph_rows = list()

  for group in groupings:
      print group["cdph_col_name"]
      cdph_rows.append(group["cdph_col_name"])
      add_to_cdph_table(cdph_df, df, group, intervention_id, begin_cycle, end_cycle)

  return cdph_df



Simulation_name = args.name
Is_remote = args.is_remote




# df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/med_10_runs_output_by_cycle_and_state_full.csv")



# df = pd.read_csv("go/tmp/cycle_state/med_10_runs_16_cycles_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/calib_cure_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/small_rop_100c_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/calib_risk_groups_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/memory_output_by_cycle_and_state_full.csv")
if Is_remote == 1:
  df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full.csv", encoding='ascii')
else:
  df = pd.read_csv("go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full.csv",  encoding='ascii')

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
  cols_to_average = "Ylls", "Ylds", "Population", "Population_fb", "Population_us", "Costs", "Dalys", "Active_cases_fb", "Slow_latents_fb", "Fast_latents_fb", "Active_cases_us", "Slow_latents_us", "Fast_latents_us", "Risk_of_prog_us", "Risk_of_prog_fb", "Months_life_remaining_us", "Months_life_remaining_fb", "Age", "Recent_transmission_us", "Recent_transmission_fb", "Recent_transmission_us_rop", "Recent_transmission_fb_rop", "Transmission_within_us", "Risk_of_infection_fb", "Risk_of_infection_us"
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
intervention_ids = pd.unique(df.Intervention_id)

df["Elim"] = (df["Population"] * Run_adjustment) / 1000000
df["PreElim"] = (df["Population"] * Run_adjustment) / 100000

#  -----------------------------------------  cdph --------------------------------------------------------


begin_cycle = df[df.Year == 2014].Cycle_id.min()
end_cycle = df[df.Year == 2014].Cycle_id.max()


# ------------ active by year

h1("Active by year")

p('''
Comparison of the interventions using method one. Note, the intervention is 
more-or-less a placeholder.
''')



active_id = getStateIdByName("Active - untreated")

# for cycle in Cycle.query.all():
#   df.loc[df.Cycle_id == cycle.id, "Year"] = cycle.year


df["Active_cases_total"] = df.Active_cases_us + df.Active_cases_fb




# & (df.Year > 2015)
qdf = df[(df.State_id == active_id) & (df.Year > 2014)].groupby(["Year", "Intervention_name", "Iteration_num"]).Active_cases_total.sum() * Run_adjustment
qdf = qdf.reset_index()

ax = sns.tsplot(time="Year", value="Active_cases_total", unit="Iteration_num", condition="Intervention_name", data=qdf)
plt.xlabel('Year')
plt.ylabel('Active cases (annual)')
ax.get_xaxis().get_major_formatter().set_useOffset(False)


html_figure("comparison_of_interventions_year","large","Comparison of interventions with method 1")



p('''
Comparison of the interventions using method two.
''')


life_id = getStateIdByName("Life")

max_year = df.Year.max()

qdf = df[(df.State_id == life_id)].groupby(["Year", "Intervention_name", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment
qdf = qdf.reset_index()

# qdf = qdf.set_index(["Intervention_name", "Year", "Iteration_num"])

# colors = ["windows blue", "amber", "greyish", "faded green", "dusty purple"]
# plt.figure(figsize=(20,10))
# sns.palplot(sns.xkcd_palette(colors))


# from ---------- (to below) is specific for the CDC presentation

# if Simulation_name == "med-risk-factor":
#   qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "1) Base case"
#   qdf.loc[qdf.Intervention_name == "2x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "2) 2x the recruitment rate in those with medical risk factor, QFT/3PH"
#   qdf.loc[qdf.Intervention_name == "4x in those with medical risk factors  (QFT/3HP)", "Intervention_name"] = "3) 4x the recruitment rate in those with medical risk factor, QFT/3PH"
#   qdf.loc[qdf.Intervention_name == "10x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "4) 10x the recruitment rate in those with medical risk factor, QFT/3PH"

#   colors = {
#     "1) Base case" : 'Black',
#     "2) 2x the recruitment rate in those with medical risk factor, QFT/3PH": '#d95f02',
#     "3) 4x the recruitment rate in those with medical risk factor, QFT/3PH": '#7570b3',
#     "4) 10x the recruitment rate in those with medical risk factor, QFT/3PH": '#e7298a'
#   }

#   qdf = qdf.sort("Intervention_name")

#   labs = [ "Basecase", "2x the recruitment rate in those with medical risk factor", "4x the recruitment rate in those with medical risk factor", "10x the recruitment rate in those with medical risk factor"]

#   ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", color=colors, data=qdf) # color={ 'Basecase': 'Black'},
#   # plt.legend(labels=labs)


# if Simulation_name == "fb":
#   qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "1) Base case"
#   qdf.loc[qdf.Intervention_name == "2x in FB (QFT/3HP)", "Intervention_name"] = "2) 2x the recruitment rate in FB, QFT/3PH"
#   qdf.loc[qdf.Intervention_name == "4x in FB (QFT/3HP)", "Intervention_name"] = "3) 4x the recruitment rate in FB, QFT/3PH"
#   qdf.loc[qdf.Intervention_name == "10x in FB (QFT/3HP)", "Intervention_name"] = "4) 10x the recruitment rate in FB, QFT/3PH"

#   colors = {
#     "1) Base case" : 'Black',
#     "2) 2x the recruitment rate in FB, QFT/3PH": '#d95f02',
#     "3) 4x the recruitment rate in FB, QFT/3PH": '#7570b3',
#     "4) 10x the recruitment rate in FB, QFT/3PH": '#e7298a'
#   }

#   qdf = qdf.sort("Intervention_name")

#   ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", color=colors, data=qdf) # color={ 'Basecase': 'Black'},
#   # plt.legend(labels=labs)


# if Simulation_name == "full-pop":
#   qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "1) Base case"
#   qdf.loc[qdf.Intervention_name == "2x in general population (QFT/3HP)", "Intervention_name"] = "2) 2x the recruitment rate, QFT/3PH"
#   qdf.loc[qdf.Intervention_name == "4x in general population (QFT/3HP)", "Intervention_name"] = "3) 4x the recruitment rate, QFT/3PH"
#   qdf.loc[qdf.Intervention_name == "10x in general population (QFT/3HP)", "Intervention_name"] = "4) 10x the recruitment rate, QFT/3PH"


#   colors = {
#     "1) Base case" : 'Black',
#     "2) 2x the recruitment rate, QFT/3PH": '#d95f02',
#     "3) 4x the recruitment rate, QFT/3PH": '#7570b3',
#     "4) 10x the recruitment rate, QFT/3PH": '#e7298a'
#   }

#   qdf = qdf.sort("Intervention_name")

#   ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", color=colors, data=qdf) # color={ 'Basecase': 'Black'},
#   # plt.legend(labels=labs)

#   # ---------- to here

# else:



elim = qdf[qdf.Intervention_name == "Basecase"]
pre_elim = qdf[qdf.Intervention_name == "Basecase"]

elim = elim.set_index(["Year", "Intervention_name", "Iteration_num"])
pre_elim = pre_elim.set_index(["Year", "Intervention_name", "Iteration_num"])


elim.loc[:,"Risk_of_prog_total"] = df[(df.State_id == life_id) & (df.Intervention_name == "Basecase")].groupby(["Year", "Intervention_name", "Iteration_num"])["Elim"].mean()

pre_elim.loc[:,"Risk_of_prog_total"] = df[(df.State_id == life_id) & (df.Intervention_name == "Basecase")].groupby(["Year", "Intervention_name", "Iteration_num"]).PreElim.mean()


elim = elim.reset_index()
pre_elim = pre_elim.reset_index()

elim.loc[:,"Intervention_name"] = "Elimination"
pre_elim.loc[:,"Intervention_name"] = "Pre-elimination"


# qdf = qdf.append([elim, pre_elim])

# ax2 = sns.pointplot(y="Risk_of_prog_total", x="Year", data=elim)


ax = sns.tsplot(time="Year", value="Risk_of_prog_total", unit="Iteration_num", condition="Intervention_name", data=qdf)


# plt.axhline(y= 39*3/2,
plt.legend(title="Interventions")
plt.xlabel('Year')
plt.ylabel('Active cases (annual)')

plt.plot(pre_elim["Year"],pre_elim["Risk_of_prog_total"], marker="None", color='black', linestyle='-', linewidth=2, alpha=0.5)
plt.plot(elim["Year"],elim["Risk_of_prog_total"], marker="None", color='black', linestyle=':', linewidth=2, alpha=0.5)


ax.get_xaxis().get_major_formatter().set_useOffset(False)




html_figure("comparison_of_interventions_2_year","large","Comparison of interventions with method 2")




# ///////////////////////// TABLE


# Strategy
# Cost 
# Incremental Cost
# Cases of TB 
# Incremental Cases of TB 
# Cost per case averted



### Formatted results table






to_html(results_df.T.to_html(classes="table table-striped", float_format='%.0f'))



save_outputs()



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






from scipy import interpolate
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

matplotlib.rcParams['lines.linewidth'] = 0.2

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
Run_adjustment = 1000


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

font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 36 }

plt.rc('font', **font)



# df_locs = [ "med-risk-factor_output_by_cycle_and_state_full.csv", "fb_output_by_cycle_and_state_full.csv", "fb-and-med-risk-factor_output_by_cycle_and_state_full.csv", "full-pop_output_by_cycle_and_state_full.csv" ]

# df_locs = [ "med-risk-factor_output_by_cycle_and_state_full_psa_iter_1.csv", "fb_output_by_cycle_and_state_full_psa_iter_1.csv", "fb-and-med-risk-factor_output_by_cycle_and_state_full_psa_iter_1.csv", "full-pop_output_by_cycle_and_state_full_psa_iter_1.csv" ]

 # "fb-master.csv", "fb-and-med-risk-factor-master.csv", "full-pop-master.csv" ]

df_locs = [ "med-risk-factor-limited-master.csv", "fb-limited-master.csv", "fb-and-med-risk-factor-limited-master.csv", "full-pop-limited-master.csv" ]

f, axarr = plt.subplots(2,2, figsize=(7, 5), sharex=True, sharey=True)
i = 0

for df_loc in df_locs:
  print df_loc
  df = pd.read_csv("/hdd/share/" + "w-leavers-main-analysis_psa_17-Oct-2017" +"/masters/" + df_loc)
  # initial processing
  df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
  df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
  df["Average life expectancy, months"] = df["Months_life_remaining_total"] / df.Population
  df["Expected total active cases"] = df["Months_life_remaining_total"] * df["Risk_of_prog_total"] / df.Population
  intervention_ids = pd.unique(df.Intervention_id)
  df["Elim"] = (df["Population"] * Run_adjustment) / 1000000
  df["PreElim"] = (df["Population"] * Run_adjustment) / 100000
  begin_cycle = df[df.Year == 2014].Cycle_id.min()
  end_cycle = df[df.Year == 2014].Cycle_id.max()
  life_id = getStateIdByName("Life")
  max_year = df.Year.max()
  qdf = df[(df.State_id == life_id)].groupby(["Year", "Intervention_name", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment
  qdf = qdf.reset_index()
  elim = qdf[qdf.Intervention_name == "Basecase"]
  pre_elim = qdf[qdf.Intervention_name == "Basecase"]
  elim = elim.set_index(["Year", "Intervention_name", "Iteration_num"])
  pre_elim = pre_elim.set_index(["Year", "Intervention_name", "Iteration_num"])
  elim.loc[:,"Risk_of_prog_total"] = df[(df.State_id == life_id) & (df.Intervention_name == "Basecase")].groupby(["Year", "Intervention_name", "Iteration_num"])["Elim"].mean()
  pre_elim.loc[:,"Risk_of_prog_total"] = df[(df.State_id == life_id) & (df.Intervention_name == "Basecase")].groupby(["Year", "Intervention_name", "Iteration_num"]).PreElim.mean()
  elim = elim.reset_index()
  pre_elim = pre_elim.reset_index()

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in those with medical risk factors  (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in FB (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in FB (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in FB (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in FB + Med risk factor (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in FB + Med risk factor (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in FB + Med risk factor (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in general population (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in general population (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in general population (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf['Intervention_name'] = pd.Categorical(qdf['Intervention_name'], ["Base case", "2x the recruitment rate, QFT/3HP", "4x the recruitment rate, QFT/3HP", "10x the recruitment rate, QFT/3HP"])
  qdf = qdf.sort("Intervention_name")
  colors = {
    "Base case" : 'Black',
    "2x the recruitment rate, QFT/3HP": '#d95f02',
    "4x the recruitment rate, QFT/3HP": '#7570b3',
    "10x the recruitment rate, QFT/3HP": '#e7298a'
  }
  using_interpolation = True
  if using_interpolation:
    means = qdf[(qdf.Year > 2014)].groupby(["Year", "Intervention_name"]).Risk_of_prog_total.mean().reset_index()
    std = qdf[(qdf.Year > 2014)].groupby(["Year", "Intervention_name"]).Risk_of_prog_total.std().reset_index()
    highs = std.copy()
    lows = std.copy()
    highs.loc[:, "Risk_of_prog_total"] = means["Risk_of_prog_total"] + 2.0 * std["Risk_of_prog_total"]
    lows.loc[:, "Risk_of_prog_total"] = means["Risk_of_prog_total"] - 2.0 * std["Risk_of_prog_total"]

    for intr in pd.unique(means["Intervention_name"]):
      itp = interpolate.UnivariateSpline(means[means.Intervention_name == intr]["Year"],means[means.Intervention_name == intr]["Risk_of_prog_total"],s=3000)
      yy_sg = itp(means[means.Intervention_name == intr]["Year"])
      means.loc[means.Intervention_name == intr, "Risk_of_prog_total"] = yy_sg

      itp = interpolate.UnivariateSpline(lows[lows.Intervention_name == intr]["Year"],lows[lows.Intervention_name == intr]["Risk_of_prog_total"],s=3000)
      yy_sg = itp(lows[lows.Intervention_name == intr]["Year"])
      lows.loc[means.Intervention_name == intr, "Risk_of_prog_total"] = yy_sg

      itp = interpolate.UnivariateSpline(highs[highs.Intervention_name == intr]["Year"],highs[highs.Intervention_name == intr]["Risk_of_prog_total"],s=3000)
      yy_sg = itp(highs[highs.Intervention_name == intr]["Year"])
      highs.loc[highs.Intervention_name == intr, "Risk_of_prog_total"] = yy_sg

    o, t = 0 , 0

    if i == 0:
      o, t = 0 , 0
    if i == 1:
      o, t = 0 , 1
    if i == 2:
      o, t = 1 , 0
    if i == 3:
      o, t = 1 , 1

    for intr in pd.unique(means["Intervention_name"]):
      # axarr[o][t].plot(means[means.Intervention_name == intr]["Year"], means[means.Intervention_name == intr]["Risk_of_prog_total"], label=intr, color=colors[intr])
      axarr[o][t].fill_between(means[means.Intervention_name == intr]["Year"], lows[lows.Intervention_name == intr]["Risk_of_prog_total"], highs[highs.Intervention_name == intr]["Risk_of_prog_total"],color=colors[intr],alpha=0.1)
    axarr[o][t].plot(pre_elim[pre_elim.Year > 2014]["Year"],pre_elim[pre_elim.Year > 2014]["Risk_of_prog_total"], marker="None", color='black', linestyle='--', linewidth=1, alpha=0.8, label="Pre-elimination")
    axarr[o][t].plot(elim[elim.Year > 2014]["Year"],elim[elim.Year > 2014]["Risk_of_prog_total"], marker="None", color='black', linestyle=':', linewidth=1, alpha=0.8, label="Elimination")
    axarr[o][t].set_xlim([elim[elim.Year > 2014]["Year"].min(),elim[elim.Year > 2014]["Year"].max()])

    i = i+1



## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## ----------------------- BEST GUESSS             -----------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------


best_guess_df_locs = [ "med-risk-factor-limited-master.csv", "fb-limited-master.csv", "fb-and-med-risk-factor-limited-master.csv", "full-pop-limited-master.csv" ]

i = 0

for df_loc in best_guess_df_locs:
  print df_loc + " best guess"
  df = pd.read_csv("/hdd/share/" + Output_name + "/masters/" + df_loc)
  # initial processing
  df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
  df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
  df["Average life expectancy, months"] = df["Months_life_remaining_total"] / df.Population
  df["Expected total active cases"] = df["Months_life_remaining_total"] * df["Risk_of_prog_total"] / df.Population
  intervention_ids = pd.unique(df.Intervention_id)
  df["Elim"] = (df["Population"] * Run_adjustment) / 1000000
  df["PreElim"] = (df["Population"] * Run_adjustment) / 100000
  begin_cycle = df[df.Year == 2014].Cycle_id.min()
  end_cycle = df[df.Year == 2014].Cycle_id.max()
  life_id = getStateIdByName("Life")
  max_year = df.Year.max()
  qdf = df[(df.State_id == life_id)].groupby(["Year", "Intervention_name", "Iteration_num"]).Risk_of_prog_total.sum() * Run_adjustment
  qdf = qdf.reset_index()
  elim = qdf[qdf.Intervention_name == "Basecase"]
  pre_elim = qdf[qdf.Intervention_name == "Basecase"]
  elim = elim.set_index(["Year", "Intervention_name", "Iteration_num"])
  pre_elim = pre_elim.set_index(["Year", "Intervention_name", "Iteration_num"])
  elim.loc[:,"Risk_of_prog_total"] = df[(df.State_id == life_id) & (df.Intervention_name == "Basecase")].groupby(["Year", "Intervention_name", "Iteration_num"])["Elim"].mean()
  pre_elim.loc[:,"Risk_of_prog_total"] = df[(df.State_id == life_id) & (df.Intervention_name == "Basecase")].groupby(["Year", "Intervention_name", "Iteration_num"]).PreElim.mean()
  elim = elim.reset_index()
  pre_elim = pre_elim.reset_index()

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in those with medical risk factors  (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in those with medical risk factors (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in FB (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in FB (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in FB (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in FB + Med risk factor (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in FB + Med risk factor (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in FB + Med risk factor (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf.loc[qdf.Intervention_name == "Basecase", "Intervention_name"] = "Base case"
  qdf.loc[qdf.Intervention_name == "2x in general population (QFT/3HP)", "Intervention_name"] = "2x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "4x in general population (QFT/3HP)", "Intervention_name"] = "4x the recruitment rate, QFT/3HP"
  qdf.loc[qdf.Intervention_name == "10x in general population (QFT/3HP)", "Intervention_name"] = "10x the recruitment rate, QFT/3HP"

  qdf['Intervention_name'] = pd.Categorical(qdf['Intervention_name'], ["Base case", "2x the recruitment rate, QFT/3HP", "4x the recruitment rate, QFT/3HP", "10x the recruitment rate, QFT/3HP"])
  qdf = qdf.sort("Intervention_name")
  colors = {
    "Base case" : 'Black',
    "2x the recruitment rate, QFT/3HP": '#d95f02',
    "4x the recruitment rate, QFT/3HP": '#7570b3',
    "10x the recruitment rate, QFT/3HP": '#e7298a'
  }
  using_interpolation = False
  if using_interpolation:
    means = qdf[(qdf.Year > 2014)].groupby(["Year", "Intervention_name"]).Risk_of_prog_total.mean().reset_index()
    std = qdf[(qdf.Year > 2014)].groupby(["Year", "Intervention_name"]).Risk_of_prog_total.std().reset_index()
    highs = std.copy()
    lows = std.copy()
    highs.loc[:, "Risk_of_prog_total"] = means["Risk_of_prog_total"] + 2.0 * std["Risk_of_prog_total"]
    lows.loc[:, "Risk_of_prog_total"] = means["Risk_of_prog_total"] - 2.0 * std["Risk_of_prog_total"]

    for intr in pd.unique(means["Intervention_name"]):
      itp = interpolate.UnivariateSpline(means[means.Intervention_name == intr]["Year"],means[means.Intervention_name == intr]["Risk_of_prog_total"],s=3000)
      yy_sg = itp(means[means.Intervention_name == intr]["Year"])
      means.loc[means.Intervention_name == intr, "Risk_of_prog_total"] = yy_sg

      itp = interpolate.UnivariateSpline(lows[lows.Intervention_name == intr]["Year"],lows[lows.Intervention_name == intr]["Risk_of_prog_total"],s=3000)
      yy_sg = itp(lows[lows.Intervention_name == intr]["Year"])
      lows.loc[means.Intervention_name == intr, "Risk_of_prog_total"] = yy_sg

      itp = interpolate.UnivariateSpline(highs[highs.Intervention_name == intr]["Year"],highs[highs.Intervention_name == intr]["Risk_of_prog_total"],s=3000)
      yy_sg = itp(highs[highs.Intervention_name == intr]["Year"])
      highs.loc[highs.Intervention_name == intr, "Risk_of_prog_total"] = yy_sg

    o, t = 0 , 0

    if i == 0:
      o, t = 0 , 0
    if i == 1:
      o, t = 0 , 1
    if i == 2:
      o, t = 1 , 0
    if i == 3:
      o, t = 1 , 1

    for intr in pd.unique(means["Intervention_name"]):
      # axarr[o][t].plot(means[means.Intervention_name == intr]["Year"], means[means.Intervention_name == intr]["Risk_of_prog_total"], label=intr, color=colors[intr])
      axarr[o][t].fill_between(means[means.Intervention_name == intr]["Year"], lows[lows.Intervention_name == intr]["Risk_of_prog_total"], highs[highs.Intervention_name == intr]["Risk_of_prog_total"],color=colors[intr],alpha=0.1)
    axarr[o][t].plot(pre_elim[pre_elim.Year > 2014]["Year"],pre_elim[pre_elim.Year > 2014]["Risk_of_prog_total"], marker="None", color='black', linestyle='--', linewidth=1, alpha=0.8, label="Pre-elimination")
    axarr[o][t].plot(elim[elim.Year > 2014]["Year"],elim[elim.Year > 2014]["Risk_of_prog_total"], marker="None", color='black', linestyle=':', linewidth=1, alpha=0.8, label="Elimination")
    axarr[o][t].set_xlim([elim[elim.Year > 2014]["Year"].min(),elim[elim.Year > 2014]["Year"].max()])

    i = i+1

  else:

    error_style = None #"unit_traces" #

    if i == 0:
      sns.tsplot(time="Year", value="Risk_of_prog_total", interpolate=True, unit="Iteration_num", linewidth=1, err_style=error_style, ci=[5, 95], condition="Intervention_name", color=colors, data=qdf[qdf.Year > 2014], ax=axarr[0][0])
    if i == 1:
      sns.tsplot(time="Year", value="Risk_of_prog_total", interpolate=True, unit="Iteration_num", linewidth=1, err_style=error_style, ci=[5, 95], condition="Intervention_name", color=colors, data=qdf[qdf.Year > 2014], ax=axarr[0][1])
    if i == 2:
      sns.tsplot(time="Year", value="Risk_of_prog_total", interpolate=True, unit="Iteration_num", linewidth=1, err_style=error_style, ci=[5, 95], condition="Intervention_name", color=colors, data=qdf[qdf.Year > 2014], ax=axarr[1][0])
    if i == 3:
      sns.tsplot(time="Year", value="Risk_of_prog_total", interpolate=True, unit="Iteration_num", linewidth=1, err_style=error_style, ci=[5, 95], condition="Intervention_name", color=colors, data=qdf[qdf.Year > 2014], ax=axarr[1][1])

    i = i+1


axarr[0][0].legend_.remove()
axarr[0][1].legend_.remove()
axarr[1][0].legend_.remove()

axarr[0][0].set_xlabel("")
axarr[0][1].set_xlabel("")
axarr[0][1].set_ylabel("")
axarr[1][1].set_ylabel("")

axarr[0][0].set_ylabel("Annual active cases")
axarr[1][0].set_ylabel("Annual active cases")

axarr[1][0].set_xlabel("Year")
axarr[1][1].set_xlabel("Year")

axarr[0][0].set_title('Medical risk factor')
axarr[0][1].set_title('Foreign-born')
axarr[1][0].set_title('Foreign-born and medical risk factor')
axarr[1][1].set_title('All')

axarr[1][1].legend(title="Interventions")
axarr[1][1].legend(bbox_to_anchor=(1.05, 1.5), loc=2, borderaxespad=0.)


print "saving as " + "/hdd/share/" + Output_name + "/results/major_figure_" + time.strftime("%Y-%m-%d-%Hh%Mm") + ".png"

plt.savefig("/hdd/share/" + Output_name + "/results/major_figure_" + time.strftime("%Y-%m-%d-%Hh%Mm") + ".svg", bbox_inches='tight', dpi=300, format="svg")


print "done"







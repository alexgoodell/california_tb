
from IPython.display import Image
# For later visualizaton scripts
import pygraphviz as pgv
import time
import sys
import re
import os
import pandas as pd
import numpy as np
import scipy as scipy
import scikits.bootstrap as bootstrap
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt, mpld3
import seaborn as sns
import random as random
from matplotlib import pyplot as plt

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
parser.add_argument("-t", "--run_type", type=str,
                    help="type of run: single or psa or dsa")
parser.add_argument("-q", "--num_simulations", type=int,
                    help="number of simulations for psa, integer")
parser.add_argument("-c", "--is_closed_cohort", type=str,
                    help="y or n")

number_of_people_to_simulate = 38000

args = parser.parse_args()
if args.size == 's':
    number_of_people_to_simulate = 38000
if args.size == 'm':
    number_of_people_to_simulate = 380000
if args.size == 'l':
    number_of_people_to_simulate = 3800000


if args.images == 'y' or args.images == 'yes':
  Include_images = True
else:
  Include_images = False


Is_closed_cohort = args.is_closed_cohort

print "is closed cohort? " + Is_closed_cohort

RandomSeq = int(time.time())
Html = ""
Image_dir = "output_figures/"
Html_dir = "output_html/"
Fig_count = 0
Output_name = str(RandomSeq) + args.name

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
    return str(int(value))
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
  filename = str(RandomSeq) + name + ".png"
  plt.savefig(Html_dir + Image_dir + filename, bbox_inches='tight', dpi = 300)
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
  f = open(Html_dir + Output_name + "_ttt.html", 'w+')
  f.write(revised_template)
  f.close()
  os.system('open '+ Html_dir + Output_name + "_ttt.html")




def get_state_list_from_chain_name(chain_name):
    chain = Chain.query.filter_by(name=chain_name).first()
    states = chain.states
    state_name_list = list()
    for state in states:
        if state.name != "Death" and state.name != "Uninitialized":
            state_name_list.append(state.name)
    return state_name_list



  
Simulation_name = args.name


Run_adjustment = 30733353.0 / number_of_people_to_simulate


# df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/med_10_runs_output_by_cycle_and_state_full.csv")



# df = pd.read_csv("go/tmp/cycle_state/med_10_runs_16_cycles_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/calib_cure_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("http://52.21.208.113/limcat/limcat/go/tmp/cycle_state/small_rop_100c_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/calib_risk_groups_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/memory_output_by_cycle_and_state_full.csv")
df = pd.read_csv("go/tmp/cycle_state/" + Simulation_name + "_output_by_cycle_and_state_full.csv")
# df = pd.read_csv("go/tmp/cycle_state/bigbig_output_by_cycle_and_state_full.csv")

# initial processing
# df["Risk_of_prog_total"] = df.Risk_of_prog_us + df.Risk_of_prog_fb
# df["Months_life_remaining_total"] = df.Months_life_remaining_us + df.Months_life_remaining_fb
df["Average life expectancy, months"] = df["Months_life_remaining_us"] / df.Population_us + df["Months_life_remaining_fb"] / df.Population_fb
df["Expected total active cases"] = df["Months_life_remaining_us"] * df["Risk_of_prog_us"] / df.Population_us + df["Months_life_remaining_fb"] * df["Risk_of_prog_fb"] / df.Population_fb



# Sensitivity of TST
# Specificity of TST
# TST specificity BCG vaccinated
# Sensitivity of QFT
# Specificity of QFT
# Sensitivity of TSPOT
# Specificity of TSPOT
# Sensitivity of TST+TSPOT
# Specificity of TST+TSPOT
# Sensitivity of TST+QFT
# Specificity of TST+QFT
# Proportion of individuals that enroll in treatment after a positive TST LTBI test
# Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test
# Number of LTBI cases caused by one active case
# Number of secondary TB cases caused by one active case
# Efficacy of 9H
# Efficacy of 6H
# Efficacy of 4R
# Efficacy of 3HP

def run_analysis():

  global Is_closed_cohort

  # --------- tests

  tst = {}
  qft = {}
  tspot = {}
  tst_qft = {}
  tst_tspot = {}


  tst["name"] = "tst"
  qft["name"] = "qft"
  tspot["name"] = "tspot"
  tst_qft["name"] = "tst_qft"
  tst_tspot["name"] = "tst_tspot"

  risk_of_progression_calibrator = Variable.query.filter_by(name="Risk of progression calibrator").first().value

  qalys_gained_per_case_averted = Variable.query.filter_by(name="QALYs gained averting one case of active TB").first().value



  # sensitivity -------------------

  #usb
  tst["usb_sensitivity"] = Variable.query.filter_by(name="USB TST Sensitivity").first().value
  qft["usb_sensitivity"] = Variable.query.filter_by(name="USB QFT Sensitivity").first().value
  tspot["usb_sensitivity"] = Variable.query.filter_by(name="USB TSPOT Sensitivity").first().value

  #fb
  tst["fb_sensitivity"] = Variable.query.filter_by(name="FB TST Sensitivity").first().value
  qft["fb_sensitivity"] = Variable.query.filter_by(name="FB QFT Sensitivity").first().value
  tspot["fb_sensitivity"] = Variable.query.filter_by(name="FB TSPOT Sensitivity").first().value

  #hiv
  tst["hiv_sensitivity"] = Variable.query.filter_by(name="HIV TST Sensitivity").first().value
  qft["hiv_sensitivity"] = Variable.query.filter_by(name="HIV QFT Sensitivity").first().value
  tspot["hiv_sensitivity"] = Variable.query.filter_by(name="HIV TSPOT Sensitivity").first().value

  #esrd
  tst["esrd_sensitivity"] = Variable.query.filter_by(name="ESRD TST Sensitivity").first().value
  qft["esrd_sensitivity"] = Variable.query.filter_by(name="ESRD QFT Sensitivity").first().value
  tspot["esrd_sensitivity"] = Variable.query.filter_by(name="ESRD TSPOT Sensitivity").first().value


  # specificity -------------------

  #usb
  tst["usb_specificity"] = Variable.query.filter_by(name="USB TST Specificity").first().value
  qft["usb_specificity"] = Variable.query.filter_by(name="USB QFT Specificity").first().value
  tspot["usb_specificity"] = Variable.query.filter_by(name="USB TSPOT Specificity").first().value

  #fb
  tst["fb_specificity"] = Variable.query.filter_by(name="FB TST Specificity").first().value
  qft["fb_specificity"] = Variable.query.filter_by(name="FB QFT Specificity").first().value
  tspot["fb_specificity"] = Variable.query.filter_by(name="FB TSPOT Specificity").first().value

  #hiv
  tst["hiv_specificity"] = Variable.query.filter_by(name="HIV TST Specificity").first().value
  qft["hiv_specificity"] = Variable.query.filter_by(name="HIV QFT Specificity").first().value
  tspot["hiv_specificity"] = Variable.query.filter_by(name="HIV TSPOT Specificity").first().value

  #esrd
  tst["esrd_specificity"] = Variable.query.filter_by(name="ESRD TST Specificity").first().value
  qft["esrd_specificity"] = Variable.query.filter_by(name="ESRD QFT Specificity").first().value
  tspot["esrd_specificity"] = Variable.query.filter_by(name="ESRD TSPOT Specificity").first().value

  tst["test_cost"] = Variable.query.filter_by(name="Cost of TST").first().value    
  qft["test_cost"] = Variable.query.filter_by(name="Cost of QFT").first().value    
  tspot["test_cost"] = Variable.query.filter_by(name="Cost of TSPOT").first().value    
  tst_qft["test_cost"] = Variable.query.filter_by(name="Cost of TST+QFT").first().value    
  tst_tspot["test_cost"] = Variable.query.filter_by(name="Cost of TST+TSPOT").first().value    


  tst["proportion_start_treatment"] = Variable.query.filter_by(name="Proportion of individuals that enroll in treatment after a positive TST LTBI test").first().value
  qft["proportion_start_treatment"] = Variable.query.filter_by(name="Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test").first().value
  tspot["proportion_start_treatment"] = Variable.query.filter_by(name="Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test").first().value
  tst_qft["proportion_start_treatment"] = Variable.query.filter_by(name="Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test").first().value
  tst_tspot["proportion_start_treatment"] = Variable.query.filter_by(name="Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test").first().value

  # ---------- treatments

  inh_6 = {}
  inh_9 = {}
  rif_4 = {}
  rpt_3 = {}

  inh_6["name"] = "inh_6"
  inh_9["name"] = "inh_9"
  rif_4["name"] = "rif_4"
  rpt_3["name"] = "rpt_3"

  inh_6["latent_treatment_cost_total"] = Variable.query.filter_by(name="Total cost of LTBI treatment 9H").first().value 
  inh_9["latent_treatment_cost_total"] = Variable.query.filter_by(name="Total cost of LTBI treatment 6H").first().value 
  rif_4["latent_treatment_cost_total"] = Variable.query.filter_by(name="Total cost of LTBI treatment 4R").first().value 
  rpt_3["latent_treatment_cost_total"] = Variable.query.filter_by(name="Total cost of LTBI treatment 3HP").first().value 


  inh_6["proportion_complete_treatment"] = Variable.query.filter_by(name="Proportion of started who complete treatment, 9H").first().value 
  inh_9["proportion_complete_treatment"] = Variable.query.filter_by(name="Proportion of started who complete treatment, 6H").first().value 
  rif_4["proportion_complete_treatment"] = Variable.query.filter_by(name="Proportion of started who complete treatment, 4R").first().value 
  rpt_3["proportion_complete_treatment"] = Variable.query.filter_by(name="Proportion of started who complete treatment, 3HP").first().value 

  inh_6["treatment_efficacy"] = Variable.query.filter_by(name="Efficacy of 9H").first().value 
  inh_9["treatment_efficacy"] = Variable.query.filter_by(name="Efficacy of 6H").first().value 
  rif_4["treatment_efficacy"] = Variable.query.filter_by(name="Efficacy of 4R").first().value 
  rpt_3["treatment_efficacy"] = Variable.query.filter_by(name="Efficacy of 3HP").first().value 




  tests = [tst, qft, tspot] # As per AC email, hold off on these: , tst_qft, tst_tspot]
  treatments = [inh_6, inh_9, rif_4, rpt_3]

  global_qdf = pd.DataFrame()

  for test in tests:
    for treatment in treatments:
      tt_name = test["name"] + " with " + treatment["name"]
      print tt_name 
      h3(tt_name)
      # print tt_name

       # NOTE! proportion_complete_treatment is of those who start treatment

      # should be 2014 in future
      ydf = df[df.Year == 2014].copy()

      # calc USB sensitivty

      ydf.loc[:, "usb_sensitivity"] = test["usb_sensitivity"]
      ydf.loc[(ydf["State_name"] == "Infected HIV, no ART") | (ydf["State_name"] == "Infected HIV, ART"), "usb_sensitivity"] = test["hiv_sensitivity"]
      ydf.loc[ydf["State_name"] == "ESRD", "usb_sensitivity"] = test["esrd_sensitivity"]
      

      # calc FB sensitivty

      ydf.loc[:, "fb_sensitivity"] = test["fb_sensitivity"]
      ydf.loc[(ydf["State_name"] == "Infected HIV, no ART") | (ydf["State_name"] == "Infected HIV, ART"), "fb_sensitivity"] = test["hiv_sensitivity"]
      ydf.loc[ydf["State_name"] == "ESRD", "fb_sensitivity"] = test["esrd_sensitivity"]



      # calc USB specificity
      ydf.loc[:, "usb_specificity"] = test["usb_specificity"]
      ydf.loc[(ydf["State_name"] == "Infected HIV, no ART") | (ydf["State_name"] == "Infected HIV, ART"), "usb_specificity"] = test["hiv_specificity"]
      ydf.loc[ydf["State_name"] == "ESRD", "usb_specificity"] = test["esrd_specificity"]

      # calc FB specificity
      ydf.loc[:, "fb_specificity"] = test["fb_specificity"]
      ydf.loc[(ydf["State_name"] == "Infected HIV, no ART") | (ydf["State_name"] == "Infected HIV, ART"), "fb_specificity"] = test["hiv_specificity"]
      ydf.loc[ydf["State_name"] == "ESRD", "fb_specificity"] = test["esrd_specificity"]


      usb_sensitivity = ydf["usb_sensitivity"]
      fb_sensitivity = ydf["fb_sensitivity"]
      usb_specificity = ydf["usb_specificity"]
      fb_specificity = ydf["fb_specificity"]






      test_cost = test["test_cost"]
      proportion_start_treatment = test["proportion_start_treatment"]

      latent_treatment_cost_total = treatment["latent_treatment_cost_total"]
      proportion_complete_treatment = treatment["proportion_complete_treatment"]
      treatment_efficacy = treatment["treatment_efficacy"]
      raw_cost_per_case = Variable.query.filter_by(name="Cost of active TB case").first().value

      cost_savings_per_case_averted = raw_cost_per_case # previously adjusted for defaulters and mortality with * (1-0.017) * (1-0.12) 

      # p("Here, we assess the costs and effects of screening 1000 people in the following categories. Test = TST; Treatment = INH 6 months")

      # embed()

      #  -------- yeatsiean closed cohort


      ydf = ydf[["State_name", "Months_life_remaining_fb", "Months_life_remaining_us", "Risk_of_prog_fb",  "Risk_of_prog_us","Population_fb" ,  "Population_us" , "Slow_latents_fb", "Slow_latents_us","Fast_latents_fb", "Fast_latents_us", "Cycle_id", "Iteration_num", "Intervention_id", "Year" ]]


      ydf["Average expected total active cases fb"] = ydf["Months_life_remaining_fb"] / ydf.Population_fb * ydf["Risk_of_prog_fb"] * risk_of_progression_calibrator / ydf.Population_fb
      ydf["Average expected total active cases us"] = ydf["Months_life_remaining_us"] / ydf.Population_us * ydf["Risk_of_prog_us"] * risk_of_progression_calibrator / ydf.Population_us


      ydf["Total_infected_fb"] = ydf.Slow_latents_fb + ydf.Fast_latents_fb
      ydf["Total_infected_us"] = ydf.Slow_latents_us + ydf.Fast_latents_us

      ydf["Prev_fb"] = ydf["Total_infected_fb"] / ydf["Population_fb"]
      ydf["Prev_us"] = ydf["Total_infected_us"] / ydf["Population_us"]

      # if using closed cohort, this is for comparing TTT results with Elim results
      # therefore it is useful to use the same number of total people being screened
      # in this module to allow for direct comparision
      if Is_closed_cohort == "y": 
        number_of_iterations = len(pd.unique(df.Iteration_num))
        number_of_people_to_test_fb = float(df[(df.Cycle_id == 3) & (df.Intervention_id == 1)][(df.State_name == "Infected Testing QFT") | (df.State_name == "Uninfected Testing QFT")].Population_fb.sum()) / float(number_of_iterations)
        number_of_people_to_test_us = float(df[(df.Cycle_id == 3) & (df.Intervention_id == 1)][(df.State_name == "Infected Testing QFT") | (df.State_name == "Uninfected Testing QFT")].Population_us.sum()) / float(number_of_iterations)
      else:
        # otherwise, just test 1000 people 
        number_of_people_to_test_fb = 1000
        number_of_people_to_test_us = 1000

      ydf["Cost of testing fb"] = number_of_people_to_test_fb * test_cost
      ydf["Cost of testing us"] = number_of_people_to_test_us * test_cost

      ydf["Infections fb"] = number_of_people_to_test_fb * ydf["Prev_fb"]
      ydf["Infections us"] = number_of_people_to_test_us * ydf["Prev_us"]

      ydf["Infections identified fb"] = number_of_people_to_test_fb * ydf["Prev_fb"] * fb_sensitivity
      ydf["Infections identified us"] = number_of_people_to_test_us * ydf["Prev_us"] * usb_sensitivity

      ydf["False positives fb"] = number_of_people_to_test_fb * (1-ydf["Prev_fb"]) * (1 - fb_specificity) 
      ydf["False positives us"] = number_of_people_to_test_us * (1-ydf["Prev_us"]) * (1 - usb_specificity)

      ydf["Start LTBI treatment fb"] = (ydf["Infections identified fb"])  * proportion_start_treatment
      ydf["Start LTBI treatment us"] = (ydf["Infections identified us"]) * proportion_start_treatment

      ydf["False positive Start LTBI treatment fb"] =  ydf["False positives fb"] * proportion_start_treatment
      ydf["False positive Start LTBI treatment us"] =  ydf["False positives us"] * proportion_start_treatment

      ydf["Average proportion of treatment taken fb"] = proportion_complete_treatment + (1-proportion_complete_treatment)*0.5 # assume drop-outs on average drop out with 50% of course
      ydf["Average proportion of treatment taken us"] = proportion_complete_treatment + (1-proportion_complete_treatment)*0.5 # assume drop-outs on average drop out with 50% of course

      ydf["Treatment costs fb"] = (ydf["Start LTBI treatment fb"] + ydf["False positive Start LTBI treatment fb"]) * ydf["Average proportion of treatment taken fb"] * latent_treatment_cost_total
      ydf["Treatment costs us"] = (ydf["Start LTBI treatment us"] + ydf["False positive Start LTBI treatment us"]) * ydf["Average proportion of treatment taken us"] * latent_treatment_cost_total

      ydf["Complete LTBI treatment fb"] = ydf["Start LTBI treatment fb"] * proportion_complete_treatment
      ydf["Complete LTBI treatment us"] = ydf["Start LTBI treatment us"] * proportion_complete_treatment

      ydf["Average risk of progression fb"] = ydf["Risk_of_prog_fb"] * risk_of_progression_calibrator / ydf["Population_fb"]
      ydf["Average risk of progression us"] = ydf["Risk_of_prog_us"] * risk_of_progression_calibrator / ydf["Population_us"]

      ydf["Proportion infected treated after intervention fb"] = ydf["Complete LTBI treatment fb"] / ydf["Infections fb"] 
      ydf["Proportion infected treated after intervention us"] = ydf["Complete LTBI treatment us"] / ydf["Infections us"] 


      ydf["Active cases after intervention fb"] = (ydf["Proportion infected treated after intervention fb"] * ydf["Average expected total active cases fb"] * (1.0 -treatment_efficacy) + (1-ydf["Proportion infected treated after intervention fb"]) * ydf["Average expected total active cases fb"]) * number_of_people_to_test_fb

      ydf["Active cases after intervention us"] = (ydf["Proportion infected treated after intervention us"] * ydf["Average expected total active cases us"] * (1.0 -treatment_efficacy) + (1-ydf["Proportion infected treated after intervention us"]) * ydf["Average expected total active cases us"]) * number_of_people_to_test_us

      ydf["Active cases control fb"] = ydf["Average expected total active cases fb"] * number_of_people_to_test_fb
      ydf["Active cases control us"] = ydf["Average expected total active cases us"] * number_of_people_to_test_us

      ydf["Cases averted fb"] = ydf["Active cases control fb"] - ydf["Active cases after intervention fb"]
      ydf["Cases averted us"] = ydf["Active cases control us"] - ydf["Active cases after intervention us"]

      ydf["Cost per case averted fb"] = (ydf["Treatment costs fb"] + ydf["Cost of testing fb"]) / ydf["Cases averted fb"] 
      ydf["Cost per case averted us"] = (ydf["Treatment costs us"]+ ydf["Cost of testing us"]) / ydf["Cases averted us"]

      ydf["Cost saves from averted active infection fb"] = ydf["Cases averted fb"] * cost_savings_per_case_averted
      ydf["Cost saves from averted active infection us"] = ydf["Cases averted us"] * cost_savings_per_case_averted

      ydf["Net costs fb"] = (ydf["Treatment costs fb"] + ydf["Cost of testing fb"]) - ydf["Cost saves from averted active infection fb"]
      ydf["Net costs us"] = (ydf["Treatment costs us"]+ ydf["Cost of testing us"])  - ydf["Cost saves from averted active infection us"]

      ydf["Net cost per case averted fb"] = ydf["Net costs fb"] / ydf["Cases averted fb"] 
      ydf["Net cost per case averted us"] = ydf["Net costs us"] / ydf["Cases averted us"]


      proportion_population_is_fb = ydf.Population_fb / (ydf.Population_us + ydf.Population_fb)
      ydf["Net cost per case averted us_and_fb"] =  ydf["Net cost per case averted fb"] * proportion_population_is_fb + ydf["Net cost per case averted us"] * (1-proportion_population_is_fb)


      ydf["Net cost per QALY gained fb"] =  ydf["Net cost per case averted fb"] / qalys_gained_per_case_averted
      ydf["Net cost per QALY gained us"] = ydf["Net cost per case averted us"] / qalys_gained_per_case_averted
      ydf["Net cost per QALY gained us_and_fb"] = ydf["Net cost per case averted us_and_fb"] / qalys_gained_per_case_averted



      # if tt_name == "qft with rpt_3":
        # ydf.to_csv("ttt-results/qft3hp.csv")


      states = [ "China", "India", "Philippines", "Viet Nam", "Mexico", "Belize", "Guatemala", "El Salvador", "Honduras", "Nicaragua", "Costa Rica", "Panama", "Life", "Smoker", "Homeless", "ESRD", "TNF-alpha", "Alcohol", "Not Foreign-born", "Less than one year", "Between one and 5 years", "5 or more years", "Asian", "Hispanic", "Black", "White", "Diabetes", "Infected HIV, no ART", "Infected HIV, ART", "Transplant patient", "No medical risk factor", "Medical risk factor"]

      qdf = ydf[(ydf.State_name.isin(states)) & (ydf.Year == 2014) & (ydf.Intervention_id == 0)][["State_name", "Treatment costs fb", "Treatment costs us", "Cost of testing fb", "Cost of testing us", "Cost saves from averted active infection fb", "Cost saves from averted active infection us", "Infections fb", "Infections us", "Complete LTBI treatment fb", "Complete LTBI treatment us", "Active cases control fb", "Active cases control us", "Active cases after intervention fb", "Active cases after intervention us", "Average risk of progression fb", "Average risk of progression us", "Cases averted fb","Cases averted us","Net costs fb","Net costs us","Net cost per case averted fb","Net cost per case averted us", "Net cost per case averted us_and_fb", "Iteration_num", "Net cost per QALY gained fb", "Net cost per QALY gained us", "Net cost per QALY gained us_and_fb"]].groupby("State_name").mean().reset_index()



      qdf["test_treatment_name"] = tt_name

      global_qdf = global_qdf.append(qdf)

      if args.run_type == "psa" and tt_name == "tst with inh_6":
        print tt_name + ":" + str(qdf.iloc[31]["Net cost per case averted us"])

      if args.run_type == "single":

        # ------- Table --------
        to_html(qdf.to_html(classes="table table-striped"))

        # ------- Chart --------
        costs = qdf[["State_name","Net costs fb", "Net costs us"]].set_index("State_name").stack().reset_index().rename(columns={"level_1": 'content', 0: 'Costs'})
        costs.loc[costs.content == "Net costs fb", "State_name" ] = costs["State_name"] + " FB"
        costs.loc[costs.content == "Net costs us", "State_name" ] = costs["State_name"] + " US"
        costs = costs[["State_name", "Costs"]].set_index("State_name")
        cases_avert = qdf[["State_name","Cases averted fb", "Cases averted us"]].set_index("State_name").stack().reset_index().rename(columns={"level_1": 'content', 0: 'Cases'})
        cases_avert.loc[cases_avert.content == "Cases averted fb", "State_name" ] = cases_avert["State_name"] + " FB"
        cases_avert.loc[cases_avert.content == "Cases averted us", "State_name" ] = cases_avert["State_name"] + " US"
        cases_avert = cases_avert[["State_name", "Cases"]].set_index("State_name")
        r = pd.DataFrame(costs)
        q = pd.DataFrame(cases_avert)
        final = pd.concat([r, q], axis=1).reset_index().rename(columns={"Cases": 'Active cases averted per 1000 screened', "Costs": 'Net cost of test and treat 1000 individuals'})
        # For now, exclude cost-saving
        p("Excluding cost saving:")
        final = final[final["Net cost of test and treat 1000 individuals"] > 0]
        ax = sns.regplot(x="Net cost of test and treat 1000 individuals", y="Active cases averted per 1000 screened", data=final, fit_reg=False)
        for i, row in final.iterrows():
          x = row["Net cost of test and treat 1000 individuals"]
          y = row["Active cases averted per 1000 screened"]
          txt = row["State_name"]
          ax.annotate(txt, (x,y))
        html_figure(tt_name,"large","Population estimates")

  return global_qdf

# -------------------------------- psa --------------------------------------------

if args.run_type == "psa":

  psa_df = pd.DataFrame()
  final_psa_df = pd.DataFrame()

  variable_names_to_vary = [
    "Cost of TST",
    "Cost of QFT",
    "Cost of TSPOT",
    "Cost of TST+QFT",
    "Cost of TST+TSPOT",
    "Proportion of individuals that enroll in treatment after a positive TST LTBI test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Total cost of LTBI treatment 9H",
    "Total cost of LTBI treatment 6H",
    "Total cost of LTBI treatment 4R",
    "Total cost of LTBI treatment 3HP",
    "Proportion of started who complete treatment, 9H",
    "Proportion of started who complete treatment, 6H",
    "Proportion of started who complete treatment, 4R",
    "Proportion of started who complete treatment, 3HP",
    "Efficacy of 9H",
    "Efficacy of 6H",
    "Efficacy of 4R",
    "Efficacy of 3HP",
    "Cost of active TB case",
    "Risk of progression calibrator",
    "QALYs gained averting one case of active TB"]

  print "begin analysis"
  basecase_run_df = run_analysis()
  print "finished analysis"

  original_values = list()
  for variable_name in variable_names_to_vary:
    original_values.append(Variable.query.filter_by(name=variable_name).first().value)

  for i in range(args.num_simulations):
    for p, variable_name in enumerate(variable_names_to_vary):
      mode = original_values[p]    
      low = Variable.query.filter_by(name=variable_name).first().low
      high = Variable.query.filter_by(name=variable_name).first().high
      new_value = random.triangular(low, high, mode)
      if variable_name == "Cost of TST":
        print new_value
      Variable.query.filter_by(name=variable_name).first().value = new_value
    print "simulation " + str(i)
    single_run_df = run_analysis()
    single_run_df.loc[:, "Simulation_id"] = i
    psa_df = psa_df.append(single_run_df)

  cols = ['Treatment costs fb', 'Treatment costs us',
     'Cost of testing fb', 'Cost of testing us',
     'Cost saves from averted active infection fb',
     'Cost saves from averted active infection us', 'Infections fb',
     'Infections us', 'Complete LTBI treatment fb',
     'Complete LTBI treatment us', 'Active cases control fb',
     'Active cases control us', 'Active cases after intervention fb',
     'Active cases after intervention us',
     'Average risk of progression fb', 'Average risk of progression us',
     'Cases averted fb', 'Cases averted us', 'Net costs fb',
     'Net costs us', 'Net cost per case averted fb',
     'Net cost per case averted us',
     'Net cost per case averted us_and_fb', "Net cost per QALY gained fb", "Net cost per QALY gained us", "Net cost per QALY gained us_and_fb"]

  for col in cols:
    # this assumes a normal distribution! bootstrap needed for true 95% CIs
    # this is what I was using for bootstrapping: 
    # f_low = lambda x: bootstrap.ci(data=x.values)[0]
    # f_high = lambda x: bootstrap.ci(data=x.values)[1]
    # psa_df.fillna(0).groupby(["test_treatment_name","State_name"])["Net cost per case averted fb"].apply(lambda x: bootstrap.ci(data=x)[0])
    # but it doesn't work because there are cells with the same value (ie, NaN) for each
    # run, and it produces an error
    mean = psa_df.groupby(["test_treatment_name","State_name"])[col].mean()
    std = psa_df.groupby(["test_treatment_name","State_name"])[col].std()
    low = mean - 2*std
    high = mean + 2*std 

    base = basecase_run_df.set_index(["test_treatment_name","State_name"])[col]

    final_psa_df.loc[:, col + " base number"] = base
    final_psa_df.loc[:, col + " base"] = base.apply(commas)
    final_psa_df.loc[:, col + " low"] = low.apply(commas)
    final_psa_df.loc[:, col + " high"] = high.apply(commas)
    final_psa_df.loc[:, col + " pretty"] = final_psa_df.apply(lambda x: "{} ({} - {})".format(x[col + " base"], x[col + " low"],x[col + " high"]), axis=1)
    # final_psa_df.loc[:, col + " pretty"] = pretty

  final_psa_df = final_psa_df.reset_index()

  final_psa_df.loc[final_psa_df.test_treatment_name == "tst with inh_6", "Pretty treatment name"] = "TST with 6H"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tst with inh_9", "Pretty treatment name"] = "TST with 9H"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tst with rif_4", "Pretty treatment name"] = "TST with 4R"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tst with rpt_3", "Pretty treatment name"] = "TST with 3HP"
  final_psa_df.loc[final_psa_df.test_treatment_name == "qft with inh_6", "Pretty treatment name"] = "QFT with 6H"
  final_psa_df.loc[final_psa_df.test_treatment_name == "qft with inh_9", "Pretty treatment name"] = "QFT with 9H"
  final_psa_df.loc[final_psa_df.test_treatment_name == "qft with rif_4", "Pretty treatment name"] = "QFT with 4R"
  final_psa_df.loc[final_psa_df.test_treatment_name == "qft with rpt_3", "Pretty treatment name"] = "QFT with 3HP"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tspot with inh_6", "Pretty treatment name"] = "TSPOT with 6H"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tspot with inh_9", "Pretty treatment name"] = "TSPOT with 9H"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tspot with rif_4", "Pretty treatment name"] = "TSPOT with 4R"
  final_psa_df.loc[final_psa_df.test_treatment_name == "tspot with rpt_3", "Pretty treatment name"] = "TSPOT with 3HP"

  final_psa_df[final_psa_df["State_name"] == "Life"][["Pretty treatment name", "Net cost per case averted fb base number", "Net cost per case averted fb pretty", "Net cost per case averted us pretty", "Net cost per case averted us_and_fb pretty", "Net cost per QALY gained fb pretty", "Net cost per QALY gained us pretty", "Net cost per QALY gained us_and_fb pretty"]].sort("Net cost per case averted fb base number",ascending=True).to_csv("ttt-results/ttt_psa.csv")



# reduced psa df




# Net cost per case averted fb mean Net cost per case averted fb low  Net cost per case averted fb high Net cost per case averted us mean Net cost per case averted us low  Net cost per case averted us high Net cost per case averted us_and_fb mean  Net cost per case averted us_and_fb low Net cost per case averted us_and_fb high
# -------------------------------- dsa --------------------------------------------

most_ce_test = "QFT"
most_ce_treatment = "3HP" 

most_ce_combo = "qft with rpt_3"

if args.run_type == "dsa":

  dsa_df = pd.DataFrame(columns=['Variable', 'Low', 'High', 'Low result', 'High result'])

  variable_names_to_vary = [
    "Risk of progression calibrator",
    "USB QFT Sensitivity",
    "USB QFT Specificity",
    "FB QFT Sensitivity",
    "FB QFT Specificity",
    "HIV QFT Sensitivity",
    "HIV QFT Specificity",
    "ESRD QFT Sensitivity",
    "ESRD QFT Specificity",
    "Cost of QFT",
    "Proportion of individuals that enroll in treatment after a positive TST LTBI test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Total cost of LTBI treatment 9H",
    "Total cost of LTBI treatment 6H",
    "Total cost of LTBI treatment 4R",
    "Total cost of LTBI treatment 3HP",
    "Proportion of started who complete treatment, 9H",
    "Proportion of started who complete treatment, 6H",
    "Proportion of started who complete treatment, 4R",
    "Proportion of started who complete treatment, 3HP",
    "Efficacy of 9H",
    "Efficacy of 6H",
    "Efficacy of 4R",
    "Efficacy of 3HP",
    "Cost of active TB case",
    "QALYs gained averting one case of active TB"
    ]

  result_tag = "Net cost per case averted fb"

  single_run_df = run_analysis()
  real_base = float(single_run_df[(single_run_df.State_name == "Life") & (single_run_df.test_treatment_name == most_ce_combo)][result_tag])

  for variable_name in variable_names_to_vary:
    original_value = Variable.query.filter_by(name=variable_name).first().value
    low = Variable.query.filter_by(name=variable_name).first().low
    high = Variable.query.filter_by(name=variable_name).first().high



    # low
    print "trying low value of " + variable_name + " : " + str(low)
    new_value = low
    Variable.query.filter_by(name=variable_name).first().value = new_value
    single_run_df = run_analysis()
    low_result = single_run_df[(single_run_df.State_name == "Life") & (single_run_df.test_treatment_name == most_ce_combo)][result_tag]

    # high 
    print "trying high value of " + variable_name + " : " + str(high)
    new_value = high
    Variable.query.filter_by(name=variable_name).first().value = new_value
    single_run_df = run_analysis()
    high_result = single_run_df[(single_run_df.State_name == "Life") & (single_run_df.test_treatment_name == most_ce_combo)][result_tag]

    if float(low_result) - float(high_result) != 0 and not variable_name in dsa_df.Variable.tolist(): 
      dsa_df.loc[len(dsa_df)] = [variable_name, low, high, float(low_result), float(high_result)]

    Variable.query.filter_by(name=variable_name).first().value = original_value



  dsa_df.loc[:, "Effect size"] = abs(dsa_df["High result"] - dsa_df["Low result"])
  dsa_df = dsa_df.sort("Effect size", ascending=False)
  dsa_df = dsa_df.reset_index()

  dsa_df.loc[dsa_df.Variable == "Risk of progression calibrator", "Variable" ] = "Baseline risk of progression"

  dsa_df.to_csv("ttt-results/dsa_results.csv")

  ###############################################################################
  # The actual drawing part

  for i, row in dsa_df.iterrows():
    if row["Low result"] < row["High result"]:
      low = row["Low"]
      high = row["High"]
    else:
      low = row["High"]
      high = row["Low"] 
    low = float('%s' % float('%.2g' % low))
    high = float('%s' % float('%.2g' % high))
    dsa_df.loc[i, "Label"] =  "{} [{} - {}]".format(row["Variable"],float(low),float(high))


  # The y position for each variable
  ys = range(len(dsa_df))[::-1]  # top to bottom

  max_x = max(dsa_df["High result"].max(), dsa_df["Low result"].max())
  min_x = min(dsa_df["High result"].min(), dsa_df["Low result"].min())

  # Plot the bars, one by one
  for i, row in dsa_df.iterrows():
    if row["Low result"] < row["High result"]:
      low = row["Low result"]
      high = row["High result"]
    else:
      low = row["High result"]
      high = row["Low result"] 

    base = (low + high) / 2
    low_width = base - low
    high_width = high - base
    value = row["Variable"]
    y = ys[i]

    # Each bar is a "broken" horizontal bar chart
    plt.broken_barh(
        [(low, low_width), (base, high_width)],
        (y - 0.4, 0.8),
        facecolors=['#90C3D4', '#90C3D4'],  # Try different colors if you like
        edgecolors=['#90C3D4', '#90C3D4'],
        linewidth=1,
    )

    # Display the value as text. It should be positioned in the center of
    # the 'high' bar, except if there isn't any room there, then it should be
    # next to bar instead.
    x = base + high_width / 2
    if x <= base + 50:
        x = base + high_width + 50
    # plt.text(x, y, str(base), va='center', ha='left')

  # Draw a vertical line down the middle
  plt.axvline(real_base, color='black')

  # Position the x-axis on the top, hide all the other spines (=axis lines)
  axes = plt.gca()  # (gca = get current axes)
  axes.spines['left'].set_visible(False)
  axes.spines['right'].set_visible(False)
  axes.spines['bottom'].set_visible(False)
  axes.xaxis.set_ticks_position('bottom')


  # Make the y-axis display the variables
  plt.yticks(ys, dsa_df["Label"].tolist())

  # Set the portion of the x- and y-axes to show
  plt.xlim(min_x - 5000, max_x + 5000)
  plt.ylim(-1, len(dsa_df))

  plt.ylabel("Variables used in sensitivity analysis")
  plt.xlabel("Cost per TB case averted")

  plt.savefig("hello.png", bbox_inches='tight', dpi = 300)

  # html_figure("masterchart","large","Population estimates")

  # global_qdf.to_csv("ttt-results/global_qdf.csv")

  # save_outputs()


# -------------------------------- single run --------------------------------------------

  
if args.run_type == "single":

  global_qdf = run_analysis()

  rdf = global_qdf[global_qdf.State_name == "Life"]

  rdf.loc[rdf.test_treatment_name == "tst with inh_6", "Pretty treatment name"] = "TST with 6H"
  rdf.loc[rdf.test_treatment_name == "tst with inh_9", "Pretty treatment name"] = "TST with 9H"
  rdf.loc[rdf.test_treatment_name == "tst with rif_4", "Pretty treatment name"] = "TST with 4R"
  rdf.loc[rdf.test_treatment_name == "tst with rpt_3", "Pretty treatment name"] = "TST with 3HP"
  rdf.loc[rdf.test_treatment_name == "qft with inh_6", "Pretty treatment name"] = "QFT with 6H"
  rdf.loc[rdf.test_treatment_name == "qft with inh_9", "Pretty treatment name"] = "QFT with 9H"
  rdf.loc[rdf.test_treatment_name == "qft with rif_4", "Pretty treatment name"] = "QFT with 4R"
  rdf.loc[rdf.test_treatment_name == "qft with rpt_3", "Pretty treatment name"] = "QFT with 3HP"
  rdf.loc[rdf.test_treatment_name == "tspot with inh_6", "Pretty treatment name"] = "TSPOT with 6H"
  rdf.loc[rdf.test_treatment_name == "tspot with inh_9", "Pretty treatment name"] = "TSPOT with 9H"
  rdf.loc[rdf.test_treatment_name == "tspot with rif_4", "Pretty treatment name"] = "TSPOT with 4R"
  rdf.loc[rdf.test_treatment_name == "tspot with rpt_3", "Pretty treatment name"] = "TSPOT with 3HP"


  rdf = rdf.sort("Net cost per case averted us_and_fb", ascending=True)

  ax = sns.barplot(y="Pretty treatment name", x="Net cost per case averted us_and_fb", data=rdf)
  plt.xlim([0,300000])
  plt.xlabel('Net cost (USD) of averting one active TB case')
  plt.ylabel('Testing and treating strategy')
  plt.tight_layout()
  html_figure("comparison of different tt us and fb born","large","US born")

  rdf = rdf.sort("Net cost per case averted fb", ascending=True)

  ax = sns.barplot(y="Pretty treatment name", x="Net cost per case averted fb", data=rdf)
  plt.xlabel('Net cost (USD) of averting one active TB case')
  plt.ylabel('Testing and treating strategy')
  plt.xlim([0,300000])
  plt.tight_layout()
  html_figure("comparison of different tt fb born","large","FB born")

  rdf.to_csv("ttt-results/all_ttt_options.csv")
       
  # formatted for excel
  # arrays = [np.array(['', 'Cost per case averted (2014 USD)', 'Cost per case averted (2014 USD)', 'Cost per QALY (2014 USD)', 'Cost per QALY (2014 USD)']),
  #           np.array(['Testing and treatment combination', 'FB', 'USB', 'FB', 'USB'])]

  # df_te = pd.DataFrame(columns=arrays) # dataframe to export

  # for i, row in rdf.iterrows():
  #   index = len(df_te)
  #   df_te.loc[index, ('', 'Testing and treatment combination')] = row["Pretty treatment name"]

  # Cost_effectiveness_of_testing_and_treatment_combinations

  # old version 
  states_to_graph_fb = ["China", "India", "Philippines", "Viet Nam", "Mexico", "Belize", "Guatemala", "El Salvador",
    "Honduras", "Nicaragua", "Costa Rica", "Panama", "Life", "Smoker", "ESRD", "TNF-alpha", "Alcohol", 
    "Not Foreign-born", "Less than one year", "Asian", "Hispanic", "Black", "White", "Diabetes", "Infected HIV, no ART", 
    "Infected HIV, ART", "Transplant patient", "No medical risk factor", "Medical risk factor"]

 # new version, doesn't include nations
  states_to_graph_fb = ["Life", "Smoker", "ESRD", "TNF-alpha", "Alcohol", 
    "Not Foreign-born", "Asian", "Hispanic", "Black", "White", "Diabetes", "Infected HIV, no ART", 
    "Infected HIV, ART", "Transplant patient", "No medical risk factor", "Medical risk factor"]


  wdf = global_qdf[(global_qdf.test_treatment_name == "qft with rpt_3") & (global_qdf.State_name.isin(states_to_graph_fb))]


  central_america = [ "Belize", "Guatemala", "El Salvador", "Honduras", "Nicaragua", "Costa Rica", "Panama"]
  hiv_pos = ["Infected HIV, no ART", "Infected HIV, ART"]

  new_df = pd.DataFrame(columns=["Group", "Net cost per case averted"])

  # new_df.loc[len(new_df)] = { 'Group':  "Born in China", 'Net cost per case averted':  float(wdf[wdf.State_name == "China"]["Net cost per case averted fb"] )  }
  # new_df.loc[len(new_df)] = { 'Group':  "Born in India", 'Net cost per case averted':  float(wdf[wdf.State_name == "India"]["Net cost per case averted fb"] )  }
  # new_df.loc[len(new_df)] = { 'Group':  "Born in the Philippines", 'Net cost per case averted':  float(wdf[wdf.State_name == "Philippines"]["Net cost per case averted fb"] )  }
  # new_df.loc[len(new_df)] = { 'Group':  "Born in Vietnam", 'Net cost per case averted':  float(wdf[wdf.State_name ==  "Viet Nam"]["Net cost per case averted fb"] )  }
  # new_df.loc[len(new_df)] = { 'Group':  "Born in Mexico", 'Net cost per case averted':  float(wdf[wdf.State_name ==  "Mexico"]["Net cost per case averted fb"] )  }
  # new_df.loc[len(new_df)] = { 'Group':  "Born in Central America", 'Net cost per case averted':  float(wdf[wdf.State_name.isin(central_america)]["Net cost per case averted fb"].mean() )  }
  # new_df.loc[len(new_df)] = { 'Group':  "Immigrant arrived within one year", 'Net cost per case averted':  float(wdf[wdf.State_name == "Less than one year"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "Average FB", 'Net cost per case averted':  float(wdf[wdf.State_name == "Life"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "Average USB", 'Net cost per case averted':  float(wdf[wdf.State_name == "Life"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB HIV", 'Net cost per case averted':  float(wdf[wdf.State_name.isin(hiv_pos)]["Net cost per case averted fb"].mean() ) }
  new_df.loc[len(new_df)] = { 'Group':  "USB HIV", 'Net cost per case averted': float(wdf[wdf.State_name.isin(hiv_pos)]["Net cost per case averted us"].mean() )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Smoker", 'Net cost per case averted':  float(wdf[wdf.State_name == "Smoker"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Smoker", 'Net cost per case averted':  float(wdf[wdf.State_name == "Smoker"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB ESRD", 'Net cost per case averted':  float(wdf[wdf.State_name == "ESRD"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB ESRD", 'Net cost per case averted':  float(wdf[wdf.State_name == "ESRD"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB TNF-alpha", 'Net cost per case averted':  float(wdf[wdf.State_name == "TNF-alpha"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB TNF-alpha", 'Net cost per case averted':  float(wdf[wdf.State_name == "TNF-alpha"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Asian", 'Net cost per case averted':  float(wdf[wdf.State_name == "Asian"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Asian", 'Net cost per case averted':  float(wdf[wdf.State_name == "Asian"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Hispanic", 'Net cost per case averted':  float(wdf[wdf.State_name == "Hispanic"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Hispanic", 'Net cost per case averted':  float(wdf[wdf.State_name == "Hispanic"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Black", 'Net cost per case averted':  float(wdf[wdf.State_name == "Black"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Black", 'Net cost per case averted':  float(wdf[wdf.State_name == "Black"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB White", 'Net cost per case averted':  float(wdf[wdf.State_name == "White"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB White", 'Net cost per case averted':  float(wdf[wdf.State_name == "White"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Diabetes", 'Net cost per case averted':  float(wdf[wdf.State_name == "Diabetes"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Diabetes", 'Net cost per case averted':  float(wdf[wdf.State_name == "Diabetes"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Transplant patient", 'Net cost per case averted':  float(wdf[wdf.State_name == "Transplant patient"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Transplant patient", 'Net cost per case averted':  float(wdf[wdf.State_name == "Transplant patient"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB Medical risk factor", 'Net cost per case averted':  float(wdf[wdf.State_name == "Medical risk factor"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB Medical risk factor", 'Net cost per case averted':  float(wdf[wdf.State_name == "Medical risk factor"]["Net cost per case averted us"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "FB No medical risk factor", 'Net cost per case averted':  float(wdf[wdf.State_name == "No medical risk factor"]["Net cost per case averted fb"] )  }
  new_df.loc[len(new_df)] = { 'Group':  "USB No medical risk factor", 'Net cost per case averted':  float(wdf[wdf.State_name == "No medical risk factor"]["Net cost per case averted us"] )  }

  new_df = new_df.sort("Net cost per case averted", ascending=True)
  new_df.loc[new_df["Net cost per case averted"] < 0, "Net cost per case averted"] = -0.1
  new_df.to_csv("ttt-results/ttt.csv")


  ax = sns.barplot(y="Group", x="Net cost per case averted", data=new_df)
  axes = plt.gca()
  axes.set_xlim([-10000,200000])
  plt.ylabel('Subpopulation targeted')
  plt.xlabel('Net cost (USD) of averting one active TB case')



  for q in ax.patches:
    if q.get_x() < 0:
      ax.text(6000, q.get_y()+1.2, "*")
  plt.tight_layout()
  html_figure("comparison of FB groups in qft","large","FB born")

  costs = global_qdf[["State_name","Net costs fb", "Net costs us", "test_treatment_name"]].set_index(["State_name","test_treatment_name"]).stack().reset_index().rename(columns={"level_2": 'content', 0: 'Costs'})
  costs.loc[costs.content == "Net costs fb", "State_name" ] = costs["State_name"] + " FB"
  costs.loc[costs.content == "Net costs us", "State_name" ] = costs["State_name"] + " US"
  costs = costs[["State_name", "Costs", "test_treatment_name"]].set_index("State_name")
  cases_avert = global_qdf[["State_name","Cases averted fb", "Cases averted us", "test_treatment_name"]].set_index(["State_name","test_treatment_name"]).stack().reset_index().rename(columns={"level_2": 'content', 0: 'Cases'})
  cases_avert.loc[cases_avert.content == "Cases averted fb", "State_name" ] = cases_avert["State_name"] + " FB"
  cases_avert.loc[cases_avert.content == "Cases averted us", "State_name" ] = cases_avert["State_name"] + " US"
  cases_avert = cases_avert[["State_name", "Cases"]].set_index("State_name") # only need one test_treatment_name
  r = pd.DataFrame(costs)
  q = pd.DataFrame(cases_avert)
  final = pd.concat([r, q], axis=1).reset_index().rename(columns={"Cases": 'Active cases averted per 1000 screened', "Costs": 'Net cost of test and treat 1000 individuals'})
  p("Excluding cost saving:")
  final = final[final["Net cost of test and treat 1000 individuals"] > 0]
  final.to_csv("ttt-results/final.csv")
  ax = sns.lmplot(x="Net cost of test and treat 1000 individuals", y="Active cases averted per 1000 screened", hue="test_treatment_name", data=final, fit_reg=False)

  html_figure("masterchart","large","Population estimates")

  global_qdf.to_csv("ttt-results/global_qdf.csv")

  save_outputs()



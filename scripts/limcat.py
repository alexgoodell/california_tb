
'''
Hello from Haleh
Hi from Alex
Logs
35 minutes -- TOO LONG
Outline - this is what I'm talking about
Questions moving forward

Calm down on the not being able to 
HIV and 3PH imcompbaitble
practice the beginning


# Additions to TTT
* Add immunomudulation effect on IGRA/TST
* add secondary cases
* Add xray ...
* Add culture ...
* Lifetime risk of reactivation
* 


| --------  | ------------- | ------------ | ------------- | ------------ |
|           | FB            | FB HIV       | FB DM         | FB ESRD      |
| TST sens  | 87%           | 75%          | 87%           | 51%          |
| TST spec  | 95%           | 64%          | 75%           | 64%          |
| IGRA sens | 87%           | 65%          | 58.5%         | 53%          |
| IGRA spec | 98%           | 72%          | 75%           | 69%          |


3HP - NYC 65% 
78.3% - CDC trial
87-89% 3HP post-marketing
10% of FB per year
1990s - DOT, good TB control

add emlin and pre-elim numbers to slides

examples for LTBI by FB
just include the six from the RR table for the graph
table for population risk factors
Put all of the risk facotrs on one chart?
Top countries + CA + High medium low
Why does the order of the tests switch in different groups


same scale for FB
Make the basecase a different look
write pennan



python outputs2.py --images n --name compare_diag_100c5rM  --size s --is_remote 1


Make sure control is realistic

DOES TRANSMISSION ACCOUNT FOR DIFFERNECE??
life tables

-- CHANGE TSPOT SENSITIVITY FROM WAG

415 336 2431


For Sat

* two exits from RTP
* FP LBTI RIF - Month 1


* Check proportion that complete treatment
* Why are <1 year, <5 years so CE to test? Doesn't make sense...
* Jim says: Crude slideset,
    - First glimpse of what we will present
    - With "To Do" at end - ask which things are important?
    - 25 minutes; lots of interruptions, time to talk
* TST reduction
* SMR LE for risk factors
* CHIS - calibration
* 2nd priority: Tracking recent infections, re-structure model
* 2nd priority: Homeless 
* 2nd priority: QALYs
* 3rd: Area charts of risk groups over time
* See if LTBI misspelling have any effect

* Different elimination scenarios


To do tonight

* Cost system - done
* Tracking recent infections, re-structure mode
* Very basic life expenctancy estimate
* CHIS - and/or calibration
* Why do a few people initialize as dead?
* TST FB
* Labeling of the cycle graph
* Testing strageties
    - 10% of subgroups
    - Repeat for less ambitious
* Make sure lines are distiguishable
* Check that elimination and TTT have similar CEA results
* 

* defaulters need to die


Remaining to do


* Sample individuals randomly, don't just grab same people every time
* Include "Slow latents" in ability for new infection
* NOTE: FAST LATENT DOESN'T mean anything anymore - instead we just use the "months from TB infection"
* Check to make sure that there are actually fast latents being imported.... 
* Currently only UNINFECTED can become infected in US. treated/in treatment cannot.
* Treatment effacy, costs
* Life expectance
* Add # treated to the elimation graph 
* Fix calibration targets to reflect age
* Add sources
* Make the output graphs begin at 0
* USE NEW SHEENA DATA
* adjust back-calculation for recent infections
* ask pryia, pennan, dowdy, ac about decreased ltbi from immigrants vs maturing in
* what happens when you change screening
* clarify flawed back-caculation 
* start at 100% FB test, move backwards (best case)
    - what about TNF, DM, etc
    - "what if we increased testing by 10% per year"
    - CEA of subgroup of FB
    - "closed cohort" risk group CEA (yeats)
    - Assume best case
    - Assume with different testing and treatment algr
* doens't matter - whatever is needed, just focus on timeframe to elimiation
* use 3HP for base case
* Recent transmission, incorperate estimates from suzanne's email

Technical (go coding)
* give homeless people more TB
* need method to track "imported cases"
* sync has medical risk factor
* check increase risk of progression
* Transmission model (HIV and TB)
    - 6-10 per active per year
    - 0.8 per month
    - Reduction of transmissability occur (time to sputum convers - 2 months)
    - Assume same infectivity for first two months; after zero
    - new LTBI / suseptible
    - FB trumps ethnicity
    - 80% race+birthplace 20% all other PS can find
    - Email Jim about very, very simple HIV tranmission model
    - 
* Testing / uptake - basically done.
* Interventions - basically done
* Distrbute people into LTBI treatment and treated
    - amount of people treated from CDPH
    - same for active
    - 17% of people with latent have been treated.
* Targeting system - Waiting for JGK/AC
* Include FP in LTBI treatment (separate tunnel) - finished
* Event reporting - have it done (not tested) for TPs
* Costs tracking - __need to link to master.csv__
* Dalys  __need to link to master.csv__
* Calibration
* PSA
* Life expectancy
* Death by age group interactions
* check sync'ing

Previous Bennett NHANES article reported only 13% (I believe) of the positives had been treated. I don't know if that information is in the newer NHANES data.

Data formatting / inference
* LTBI prev / active prev (TB - almost done)
* Smoking, EtOH, and diabetes from CHIS
* Update progression estimates
* HIV prev

# TODO: Remove pre diabetes and treatment
# HIV deaths - keep in


# LIMCAT introduction
_Locally-interacting Markov models for HIV, TB, DM in California_


This is an IPython/Jupyter notebook. It is a method for creating reproducable
research. Essentially, it is a way to show "literate programming", or very well-documented code for scientific processes. It mixes normal text with code blocks that can be run and re-run independently.

The purpose of this IPython notebook is to organize the data that will be used
to creat the Limsa model in Go. Normally, I would complete this "pre-processing"
task in Excel, but I want to try something more detailed and reproducible.

This notebook is connected to a python application and database that will store
all the tables for the Limsa model. As we progress, we will build these tables.
__All changes to the database should be made through this notebook, so a record
of all changes is available__.

The Go model will then use these tables to run the model.


'''
from IPython.display import Image
# For later visualizaton scripts ok
import pygraphviz as pgv
import time
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import math 
from IPython import embed

#connect to application
from app import * 
#this gives us access to the database through a variables "db"

    
# remove any past problematic sessions
db.session.rollback()

# create all tables
db.drop_all()
db.create_all()
    

# destroy any models in db
models_to_destroy = [ Chain, Cost, Cycle, Disability_weight, 
Interaction,  State, Transition_probability, Intervention, Stratum_type, Stratum, Stratum_type_content, Stratum_content, Transition_probability_by_stratum, Variable_by_stratum]

for model in models_to_destroy:
    db.session.query(model).delete()

db.session.commit()
        
'''


# Functions

In order to make it easier to easier to specify transition probabilites, I wrote a function to do so. see app.py


# Chain creation

First, let's create the different chains the model will need.

'''

# currently excluded 'Tourists', 'Age'

# create the chains we need
chain_names = ['TB disease and treatment', 'HIV', 'HIV risk groups', 'Birthplace', 'Diabetes', 'Length of time in US','ESRD', "TNF-alpha", "Alcohol", "Close contacts",  'Citizen', 'Smoking', 'Homeless', 'Age grouping', 'Race', 'Natural death', 'Transplants', 'Sex', 'Medical risk factor']
for chain_name in chain_names:
    the_chain = Chain(name=chain_name)
    save(the_chain)


'''

# TB Disease and Treatment

Great. Now let's work on the TB disease and treatment chain.

## TB variables
    
### Access

'''


variable_names = [
    "Access: monthly proportion of true negatives that are tested",
    "Access: monthly proportion of true positives that are tested",
    "Sensitivity of TST",
    "Specificity of TST",
    "TST specificity BCG vaccinated",
    "Sensitivity of QFT",
    "Specificity of QFT",
    "Sensitivity of TSPOT",
    "Specificity of TSPOT",
    "Sensitivity of TST+TSPOT",
    "Specificity of TST+TSPOT",
    "Sensitivity of TST+QFT",
    "Specificity of TST+QFT",
    "Proportion of individuals that enroll in treatment after a positive TST LTBI test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Number of LTBI cases caused by one active case",
    "Number of secondary TB cases caused by one active case",
    "Efficacy of 9H",
    "Efficacy of 6H",
    "Efficacy of 4R",
    "Efficacy of 3HP",
    "Base risk of progression",
    "Proportion of LTBI treated",
    "Fast latent progression",
    "Slow latent progression",
    "Total cost of LTBI treatment 9H",
    "Total cost of LTBI treatment 6H",
    "Total cost of LTBI treatment 4R",
    "Total cost of LTBI treatment 3HP",
    "Proportion of started who complete treatment, 9H",
    "Proportion of started who complete treatment, 6H",
    "Proportion of started who complete treatment, 4R",
    "Proportion of started who complete treatment, 3HP",
    "Cost of TST",
    "Cost of QFT",
    "Cost of TSPOT",
    "Cost of TST+QFT",
    "Cost of TST+TSPOT",
    "Risk of progression calibrator"
]

# LTBI testing access - positives
for variable_name in variable_names:
    make_var(variable_name, 0.1, 0.005, 0.15)




'''

## TB disease States

First, let's define the different TB states. Here is our state-transition
diagram:

![](docs/diagrams/tb-limcat.jpg)

TODO: Where are treatment failures?

'''

# get TB chain
tb_chain = Chain.query.filter_by(name="TB disease and treatment").first()

# create the chains we need
state_names = ['Uninitialized', 
                'Uninfected TB', 
                'Fast latent', 
                'Slow latent', 
                'Infected Testing TST',
                'Infected Testing QFT',
                'Infected Testing TSPOT',
                'Infected Testing TST+QFT',
                'Infected Testing TST+TSPOT',
                'Uninfected Testing TST',
                'Uninfected Testing QFT',
                'Uninfected Testing TSPOT',
                'Uninfected Testing TST+QFT',
                'Uninfected Testing TST+TSPOT',
                'LBTI 9m INH - Month 1',
                'LBTI 9m INH - Month 2',
                'LBTI 9m INH - Month 3',
                'LBTI 9m INH - Month 4',
                'LBTI 9m INH - Month 5',
                'LBTI 9m INH - Month 6',
                'LBTI 9m INH - Month 7',
                'LBTI 9m INH - Month 8',
                'LBTI 9m INH - Month 9',
                'LTBI treated with INH 9m',
                'LTBI 6m INH - Month 1',
                'LTBI 6m INH - Month 2',
                'LTBI 6m INH - Month 3',
                'LTBI 6m INH - Month 4',
                'LTBI 6m INH - Month 5',
                'LTBI 6m INH - Month 6',
                'LTBI treated with INH 6m',
                'LTBI RIF - Month 1',
                'LTBI RIF - Month 2',
                'LTBI RIF - Month 3',
                'LTBI RIF - Month 4',
                'LTBI treated with RIF',
                'LTBI RTP - Month 1',
                'LTBI RTP - Month 2',
                'LTBI RTP - Month 3',
                'LTBI treated with RTP',
                'FP LBTI 9m INH - Month 1',
                'FP LBTI 9m INH - Month 2',
                'FP LBTI 9m INH - Month 3',
                'FP LBTI 9m INH - Month 4',
                'FP LBTI 9m INH - Month 5',
                'FP LBTI 9m INH - Month 6',
                'FP LBTI 9m INH - Month 7',
                'FP LBTI 9m INH - Month 8',
                'FP LBTI 9m INH - Month 9',
                'FP LTBI 6m INH - Month 1',
                'FP LTBI 6m INH - Month 2',
                'FP LTBI 6m INH - Month 3',
                'FP LTBI 6m INH - Month 4',
                'FP LTBI 6m INH - Month 5',
                'FP LTBI 6m INH - Month 6',
                'FP LTBI RIF - Month 1',
                'FP LTBI RIF - Month 2',
                'FP LTBI RIF - Month 3',
                'FP LTBI RIF - Month 4',
                'FP LTBI RTP - Month 1',
                'FP LTBI RTP - Month 2',
                'FP LTBI RTP - Month 3',
                'LTBI Dropped out',
                'Active - untreated', 
                'Active Treated Month 1',
                'Active Treated Month 2',
                'Active Treated Month 3',
                'Active Treated Month 4',
                'Active Treated Month 5',
                'Active Treated Month 6',
                'Former active TB',
                'Default',
                'Death']

for state_name in state_names:
    the_state = State(name=state_name,chain=tb_chain)
    save(the_state)
    
# print chains from database
print State.query.filter_by(chain=tb_chain).all()

'''

## TB disease transition probabilities

Now, we can fill in the basic transition probabilties for this chain.

Since the Uninitialized state will transition to _all_ states, we can write a function to create those transitions for now (they will be filled in with real values later.


And now, we can create the inidividual TPs we think exist. 

'''

#-------------------

# Infection
desc = "Monthly chance of infection to fast latent"
#make_tp(tb_chain, 'Uninfected TB', 'Fast latent', True, 0.1, desc)

from_state = State.query.filter_by(name="Uninfected TB", chain=tb_chain).first()
to_state = State.query.filter_by(name='Fast latent', chain=tb_chain).first()

tp = Transition_probability(
        from_state_name=from_state.name,
        to_state_name=to_state.name,
        from_state=from_state,
        to_state=to_state,
        description=desc,
        chain=tb_chain,
        is_dynamic = True,
        dynamic_function_name="TB trans to fast latent",
        tp_base=0.01
    )

db.session.add(tp)
db.session.commit()

'''
desc = "Monthly chance of infection to slow latent"

#-------------------

from_state = State.query.filter_by(name="Uninfected TB", chain=tb_chain).first()
to_state = State.query.filter_by(name='Slow latent', chain=tb_chain).first()

tp = Transition_probability(
        from_state_name=from_state.name,
        to_state_name=to_state.name,
        from_state=from_state,
        to_state=to_state,
        description=desc,
        chain=tb_chain,
        is_dynamic = True,
        dynamic_function_name="TB trans to slow latent",
        tp_base=0.01
    )

db.session.add(tp)
db.session.commit()
'''


# Self cure
desc = "Monthly self cure from slow latents"
make_tp(tb_chain, 'Slow latent', 'Uninfected TB',  False, 0.1, desc)

# Progression
desc = "Monthly transition probability from fast latent to active disease"
make_tp(tb_chain, 'Fast latent', 'Active - untreated', False, 0.1, desc)
desc = "Monthly transition probability from slow latent to active disease"
make_tp(tb_chain, 'Slow latent', 'Active - untreated', False, 0.1, desc)

# This is executed within the program, individuals only stay in fast for 36 months max, then move to slow. It doesn't utilize the transition probability system. 
make_tp(tb_chain,'Fast latent', 'Slow latent', False, 0)

# People who drop out of LTBI go back to slow latent
make_tp(tb_chain,'LTBI Dropped out', 'Slow latent', False, 0)

'''

#### Progression during treatment

'''

all_other_LTBI_states = [ 'Infected Testing TST','Infected Testing QFT','Infected Testing TSPOT','Infected Testing TST+QFT','Infected Testing TST+TSPOT','LBTI 9m INH - Month 1','LBTI 9m INH - Month 2','LBTI 9m INH - Month 3','LBTI 9m INH - Month 4','LBTI 9m INH - Month 5','LBTI 9m INH - Month 6','LBTI 9m INH - Month 7','LBTI 9m INH - Month 8','LBTI 9m INH - Month 9','LTBI treated with INH 9m','LTBI 6m INH - Month 1','LTBI 6m INH - Month 2','LTBI 6m INH - Month 3','LTBI 6m INH - Month 4','LTBI 6m INH - Month 5','LTBI 6m INH - Month 6','LTBI treated with INH 6m','LTBI RIF - Month 1','LTBI RIF - Month 2','LTBI RIF - Month 3','LTBI RIF - Month 4','LTBI treated with RIF','LTBI RTP - Month 1','LTBI RTP - Month 2','LTBI RTP - Month 3','LTBI treated with RTP','LTBI Dropped out' ]

for state in all_other_LTBI_states:
    make_tp(tb_chain,state,"Active - untreated", False, 0)

'''
    
#### Infection during FP testing / treatment


Need to add this. 

#### Unifected into testing

Some Uninfected TBs will be false positives and will be tested. We have to set a TP up to each treatement strategy.

'''
testing_option_states = ['Uninfected Testing TST',
                'Uninfected Testing QFT',
                'Uninfected Testing TSPOT',
                'Uninfected Testing TST+QFT',
                'Uninfected Testing TST+TSPOT' ]
for state in testing_option_states:
    desc = "Monthly transition probability from Uninfected TB to " + state
    make_tp(tb_chain, 'Uninfected TB', state, False, 0.01, desc)

'''

#### True negatives back to uninfected


'''
testing_option_states = ['Uninfected Testing TST',
                'Uninfected Testing QFT',
                'Uninfected Testing TSPOT',
                'Uninfected Testing TST+QFT',
                'Uninfected Testing TST+TSPOT' ]
for state in testing_option_states:
    desc = "Monthly transition probability from Uninfected TB to " + state
    make_tp(tb_chain, state, 'Uninfected TB', False, 0.01, desc)

'''


#### False positives into treatment

Some Uninfected TBs will be false positives and will be tested. We have to set a TP up to each treatement strategy.

'''
testing_option_states = ['Uninfected Testing TST',
                'Uninfected Testing QFT',
                'Uninfected Testing TSPOT',
                'Uninfected Testing TST+QFT',
                'Uninfected Testing TST+TSPOT' ]

treatment_option_states = ['FP LBTI 9m INH - Month 1', 'FP LTBI 6m INH - Month 1', 'FP LTBI RIF - Month 1', 'FP LTBI RTP - Month 1']

for testing_state in testing_option_states:
    for treatement_state in treatment_option_states:
        make_tp(tb_chain, testing_state, treatement_state, False, 0.01, desc)

'''

#### True positives into testing

Each latent category can transition to each treatment option

'''


tb_chain = Chain.query.filter_by(name="TB disease and treatment").first()

testing_option_states = ['Infected Testing TST',
                         'Infected Testing QFT',
                         'Infected Testing TSPOT',
                         'Infected Testing TST+QFT',
                         'Infected Testing TST+TSPOT' ]

latent_states = [ 'Fast latent', 'Slow latent']

for latent_state in latent_states:
    for testing_state in testing_option_states:
        make_tp(tb_chain, latent_state, testing_state, False, 0.01, desc)



'''
for treatement_state in treatment_option_states:
    for latent_state in latent_states:
        desc = "Monthly transition probability from" + latent_state + " to " + treatement_state
        #make_tp(tb_chain, latent_state, treatement_state, True, 0.01, desc)

        from_state = State.query.filter_by(name=latent_state, chain=tb_chain).first()
        to_state = State.query.filter_by(name=treatement_state, chain=tb_chain).first()

        tp = Transition_probability(
            from_state_name=from_state.name,
            to_state_name=to_state.name,
            from_state=from_state,
            to_state=to_state,
            description=desc,
            chain=tb_chain,
            is_dynamic = True,
            dynamic_function_name="True positives into testing",
            tp_base=0.01
        )

        db.session.add(tp)
        db.session.commit()
'''

'''

#### False negatives back to latent

'''

tb_chain = Chain.query.filter_by(name="TB disease and treatment").first()

testing_option_states = ['Infected Testing TST',
                         'Infected Testing QFT',
                         'Infected Testing TSPOT',
                         'Infected Testing TST+QFT',
                         'Infected Testing TST+TSPOT' ]

latent_states = [ 'Fast latent', 'Slow latent']

for latent_state in latent_states:
    for testing_state in testing_option_states:
        make_tp(tb_chain, testing_state, latent_state, False, 0.01, desc)

'''

#### True positives into treatment 

'''

testing_option_states = ['Infected Testing TST',
                         'Infected Testing QFT',
                         'Infected Testing TSPOT',
                         'Infected Testing TST+QFT',
                         'Infected Testing TST+TSPOT' ]

treatment_option_states = ['LBTI 9m INH - Month 1', 'LTBI 6m INH - Month 1', 'LTBI RIF - Month 1', 'LTBI RTP - Month 1']

for testing_state in testing_option_states:
    for treatement_state in treatment_option_states:
        make_tp(tb_chain, testing_state, treatement_state, False, 0.01, desc)


'''
    



#### Create transition probabilites within treatement

##### INH 9 month

'''

inh9_states = ['LBTI 9m INH - Month 1','LBTI 9m INH - Month 2','LBTI 9m INH - Month 3','LBTI 9m INH - Month 4','LBTI 9m INH - Month 5','LBTI 9m INH - Month 6','LBTI 9m INH - Month 7','LBTI 9m INH - Month 8','LBTI 9m INH - Month 9','LTBI treated with INH 9m']
for index, state_name in enumerate(inh9_states):
    if index < len(inh9_states)-1:

            # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=inh9_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()


        desc = "Monthly transition probability from " + state_name + " to " + inh9_states[index+1]
        make_tp(tb_chain, state_name, inh9_states[index+1], False, 1, desc)


'''

##### INH 9 month - False positive

'''

inh9_states = ['FP LBTI 9m INH - Month 1','FP LBTI 9m INH - Month 2','FP LBTI 9m INH - Month 3','FP LBTI 9m INH - Month 4','FP LBTI 9m INH - Month 5','FP LBTI 9m INH - Month 6','FP LBTI 9m INH - Month 7','FP LBTI 9m INH - Month 8','FP LBTI 9m INH - Month 9','Uninfected TB']
for index, state_name in enumerate(inh9_states):
    if index < len(inh9_states)-1:

            # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=inh9_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()


        desc = "Monthly transition probability from " + state_name + " to " + inh9_states[index+1]
        make_tp(tb_chain, state_name, inh9_states[index+1], False, 1, desc)


'''

    
##### INH 6 month

'''

inh6_states = ['LTBI 6m INH - Month 1','LTBI 6m INH - Month 2','LTBI 6m INH - Month 3','LTBI 6m INH - Month 4','LTBI 6m INH - Month 5','LTBI 6m INH - Month 6','LTBI treated with INH 6m']
for index, state_name in enumerate(inh6_states):
    if index < len(inh6_states)-1:

        # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=inh6_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()

        desc = "Monthly transition probability from " + state_name + " to " + inh6_states[index+1]
        make_tp(tb_chain, state_name, inh6_states[index+1], False, 1, desc)


'''

##### INH 6 month - false positive

'''

inh6_states = ['FP LTBI 6m INH - Month 1','FP LTBI 6m INH - Month 2','FP LTBI 6m INH - Month 3','FP LTBI 6m INH - Month 4','FP LTBI 6m INH - Month 5','FP LTBI 6m INH - Month 6','Uninfected TB']
for index, state_name in enumerate(inh6_states):
    if index < len(inh6_states)-1:

        # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=inh6_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()

        desc = "Monthly transition probability from " + state_name + " to " + inh6_states[index+1]
        make_tp(tb_chain, state_name, inh6_states[index+1], False, 1, desc)


'''

##### RIF

'''

rif_states = ['LTBI RIF - Month 1','LTBI RIF - Month 2','LTBI RIF - Month 3','LTBI RIF - Month 4','LTBI treated with RIF']
for index, state_name in enumerate(rif_states):
    if index < len(rif_states)-1:

        # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=rif_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()

        desc = "Monthly transition probability from " + state_name + " to " + rif_states[index+1]
        make_tp(tb_chain, state_name, rif_states[index+1], False, 1, desc)


'''

##### RIF -false positive

'''

rif_states = ['FP LTBI RIF - Month 1','FP LTBI RIF - Month 2','FP LTBI RIF - Month 3','FP LTBI RIF - Month 4','Uninfected TB']
for index, state_name in enumerate(rif_states):
    if index < len(rif_states)-1:

        # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=rif_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()

        desc = "Monthly transition probability from " + state_name + " to " + rif_states[index+1]
        make_tp(tb_chain, state_name, rif_states[index+1], False, 1, desc)


'''


##### RTP

'''

rpt_states = ['LTBI RTP - Month 1','LTBI RTP - Month 2','LTBI RTP - Month 3','LTBI treated with RTP']
for index, state_name in enumerate(rpt_states):
    if index < len(rpt_states)-1:

        print(state_name)
        # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=rpt_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()

        desc = "Monthly transition probability from " + state_name + " to " + rpt_states[index+1]
        make_tp(tb_chain, state_name, rpt_states[index+1], False, 1, desc)


'''


##### RTP - false positive

'''

rpt_states = ['FP LTBI RTP - Month 1','FP LTBI RTP - Month 2','FP LTBI RTP - Month 3','Uninfected TB']
for index, state_name in enumerate(rpt_states):
    if index < len(rpt_states)-1:

        print(state_name)
        # these are tunnel states, and need to be saved as such with targets
        from_state = State.query.filter_by(name=state_name).first()
        to_state = State.query.filter_by(name=rpt_states[index+1]).first()
    
        from_state.is_tunnel = True
        from_state.tunnel_target_id = to_state.id
        db.session.add(from_state)
        db.session.commit()

        desc = "Monthly transition probability from " + state_name + " to " + rpt_states[index+1]
        make_tp(tb_chain, state_name, rpt_states[index+1], False, 1, desc)


'''

##### Drop outs

'''

all_treatment_states = ['LBTI 9m INH - Month 1',
                        'LBTI 9m INH - Month 2',
                        'LBTI 9m INH - Month 3',
                        'LBTI 9m INH - Month 4',
                        'LBTI 9m INH - Month 5',
                        'LBTI 9m INH - Month 6',
                        'LBTI 9m INH - Month 7',
                        'LBTI 9m INH - Month 8',
                        'LBTI 9m INH - Month 9',
                        'LTBI 6m INH - Month 1',
                        'LTBI 6m INH - Month 2',
                        'LTBI 6m INH - Month 3',
                        'LTBI 6m INH - Month 4',
                        'LTBI 6m INH - Month 5',
                        'LTBI 6m INH - Month 6',
                        'LTBI RIF - Month 1',
                        'LTBI RIF - Month 2',
                        'LTBI RIF - Month 3',
                        'LTBI RIF - Month 4',
                        'LTBI RTP - Month 1',
                        'LTBI RTP - Month 2',
                        'LTBI RTP - Month 3']

for state in all_treatment_states:
    desc = "Monthly dropout from " + state
    make_tp(tb_chain, state, 'LTBI Dropped out', False, 0.1, desc)

'''

##### Drop outs - false positive

'''


all_treatment_states = ['FP LBTI 9m INH - Month 1',
                'FP LBTI 9m INH - Month 2',
                'FP LBTI 9m INH - Month 3',
                'FP LBTI 9m INH - Month 4',
                'FP LBTI 9m INH - Month 5',
                'FP LBTI 9m INH - Month 6',
                'FP LBTI 9m INH - Month 7',
                'FP LBTI 9m INH - Month 8',
                #'FP LBTI 9m INH - Month 9',
                'FP LTBI 6m INH - Month 1',
                'FP LTBI 6m INH - Month 2',
                'FP LTBI 6m INH - Month 3',
                'FP LTBI 6m INH - Month 4',
                'FP LTBI 6m INH - Month 5',
                #'FP LTBI 6m INH - Month 6',
                'FP LTBI RIF - Month 1',
                'FP LTBI RIF - Month 2',
                'FP LTBI RIF - Month 3',
                #'FP LTBI RIF - Month 4',
                'FP LTBI RTP - Month 1',
                'FP LTBI RTP - Month 2']
                #'FP LTBI RTP - Month 3']

for state in all_treatment_states:
    desc = "Monthly dropout from " + state
    make_tp(tb_chain, state, 'Uninfected TB', False, 0.1, desc)

'''



'''


# Active treatment recruitment
desc="Monthly recruitment of untreated active cases"
make_tp(tb_chain, 'Active - untreated', 'Active Treated Month 1', False, 0.1, desc)
'''

Progression

'''

from_state_names = ['Active Treated Month 1',
'Active Treated Month 2',
'Active Treated Month 3',
'Active Treated Month 4',
'Active Treated Month 5',
'Active Treated Month 6']

to_state_names = ['Active Treated Month 2',
'Active Treated Month 3',
'Active Treated Month 4',
'Active Treated Month 5',
'Active Treated Month 6',
'Former active TB']

i=0
for from_state_name in from_state_names: 
    from_state = State.query.filter_by(name=from_state_names[i]).first()
    to_state = State.query.filter_by(name=to_state_names[i]).first()
    from_state.is_tunnel = True
    from_state.tunnel_target_id = to_state.id
    db.session.add(from_state)
    db.session.commit()
    make_tp(tb_chain, from_state_names[i], to_state_names[i], False, 1)
    i = i+1

# Default
make_tp(tb_chain, 'Active Treated Month 1', 'Default', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 2', 'Default', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 3', 'Default', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 4', 'Default', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 6', 'Default', False, 0.1)

# Mortality
make_tp(tb_chain, 'Active - untreated', 'Death', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 1', 'Death', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 2', 'Death', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 3', 'Death', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 4', 'Death', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 5', 'Death', False, 0.1)
make_tp(tb_chain, 'Active Treated Month 6', 'Death', False, 0.1)

# Defaulters move to active diease
make_tp(tb_chain, 'Default', 'Active - untreated', False, 1)



'''
    
Make the testing states into tunnel states (otherwise turning on and off treatment creates sum TP > 1)

'''

infected_testing_states = ['Infected Testing TST',
'Infected Testing QFT',
'Infected Testing TSPOT',
'Infected Testing TST+QFT',
'Infected Testing TST+TSPOT']

infected_id = State.query.filter_by(name="Slow latent").first().id

uninfected_testing_states = [ 'Uninfected Testing TST',
'Uninfected Testing QFT',
'Uninfected Testing TSPOT',
'Uninfected Testing TST+QFT',
'Uninfected Testing TST+TSPOT' ]

uninfected_id = State.query.filter_by(name="Uninfected TB").first().id

for infected_testing_state in infected_testing_states:
    state = State.query.filter_by(name=infected_testing_state).first()
    state.is_tunnel = True
    state.tunnel_target_id = infected_id
    save(state)


for uninfected_testing_state in uninfected_testing_states:
    state = State.query.filter_by(name=uninfected_testing_state).first()
    state.is_tunnel = True
    state.tunnel_target_id = uninfected_id
    save(state)


'''






And we can create those transitions within the TB model.

'''

create_initialization_tps(tb_chain)

'''

#### Visualize

We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="tb_chain.png"
visualize_chain(filename, tb_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="tb_chain_noinit.png"
visualize_chain(filename,tb_chain, include_initialization=False)
Image(filename)

'''


# Other TB chains


Now let's build out the smaller chains we will be using:

* Past treated / not past treated (will interact with drug-resistance model)
* TNF-alpha inhibitor patients
* Homeless
* Alcholol abusers
* Close contacts
* Tourists (from US and to US)
* Smoking
* ESRD
* Immigration
    * Immigration status
    * Immigration > or < 5 years
    * Nation of origin
    * Status-adjusters
    
## Smoking

'''

# get TB resistance chain
smoking_chain = Chain.query.filter_by(name="Smoking").first()

# create the chains we need
state_names = ["Uninitialized", "Smoker", 
                "Non-smoker", "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=smoking_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=smoking_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(smoking_chain)

'''

And the relevant TPs:

'''

# Smoking uptake 
make_tp(smoking_chain, "Non-smoker", "Smoker", False, 0.1)
# Quit rate
make_tp(smoking_chain, "Smoker","Non-smoker", False, 0.1)

'''

We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="smoking.png"
visualize_chain(filename,smoking_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="smoking-noinit.png"
visualize_chain(filename,smoking_chain, include_initialization=False)
Image(filename)

'''

### Interactions

Smoking increases risk of progression to active disease:

'''

make_intr("Smoker", "Slow latent", "Active - untreated", 1.1)
make_intr("Smoker", "Fast latent", "Active - untreated", 1.1)

'''

    
## Homelessness

'''

# get TB resistance chain
homeless_chain = Chain.query.filter_by(name="Homeless").first()

# create the chains we need
state_names = ["Uninitialized", "Homeless","Not homeless",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=homeless_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=homeless_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(homeless_chain)

'''

And the relevant TPs:

'''

# Become homeless rate
make_tp(homeless_chain, "Not homeless","Homeless", False, 0.1)
# Recovery from homelessness rate 
make_tp(homeless_chain, "Homeless", "Not homeless", False, 0.1)

'''




### Interactions

TODO: Homeless more likely to become infected with TB

#### Homeless more likely to drop out of treatment - exlucded for now - set to 1


'''

all_tb_treatment_states = ['LBTI 9m INH - Month 1',
                        'LBTI 9m INH - Month 2',
                        'LBTI 9m INH - Month 3',
                        'LBTI 9m INH - Month 4',
                        'LBTI 9m INH - Month 5',
                        'LBTI 9m INH - Month 6',
                        'LBTI 9m INH - Month 7',
                        'LBTI 9m INH - Month 8',
                        'LBTI 9m INH - Month 9',
                        'LTBI 6m INH - Month 1',
                        'LTBI 6m INH - Month 2',
                        'LTBI 6m INH - Month 3',
                        'LTBI 6m INH - Month 4',
                        'LTBI 6m INH - Month 5',
                        'LTBI 6m INH - Month 6',
                        'LTBI RIF - Month 1',
                        'LTBI RIF - Month 2',
                        'LTBI RIF - Month 3',
                        'LTBI RIF - Month 4',
                        'LTBI RTP - Month 1',
                        'LTBI RTP - Month 2',
                        'LTBI RTP - Month 3']

for tb_treatment_state in all_tb_treatment_states:
    make_intr("Homeless", tb_treatment_state, "LTBI Dropped out", 1)



'''

#### Homeless less likely to access TB testing and care

Homelessness decreases access to treatment (currently just making an interaction from treatment enrollment). TODO: interactions with variables?

'''

treatment_option_states = ['LBTI 9m INH - Month 1', 'LTBI 6m INH - Month 1', 'LTBI RIF - Month 1', 'LTBI RTP - Month 1']


for treatment_state in treatment_option_states:
        make_intr("Homeless", "Slow latent", treatement_state, 1)
        make_intr("Homeless", "Fast latent", treatement_state, 1)


'''


We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="homeless.png"
visualize_chain(filename,homeless_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="homeless-noinit.png"
visualize_chain(filename,homeless_chain, include_initialization=False)
Image(filename)

'''

## ESRD

'''

# get ESRD chain
esrd_chain = Chain.query.filter_by(name="ESRD").first()

# create the chains we need
state_names = ["Uninitialized", "No ESRD","ESRD",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=esrd_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=esrd_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(esrd_chain)

'''

And the relevant TPs:

'''

# Become ESRD rate
make_tp(esrd_chain, "No ESRD","ESRD", False, 0.1)


'''

### Interactions

ESRD more likely to progress to active TB

'''

make_intr("ESRD", "Slow latent", "Active - untreated", 1.1)
make_intr("ESRD", "Fast latent", "Active - untreated", 1.1)



'''


We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="esrd.jpg"
visualize_chain(filename,esrd_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="esrd-noinit.jpg"
visualize_chain(filename,esrd_chain, include_initialization=False)
Image(filename)

'''

## TNF-alpha patients

'''

# get ESRD chain
tnf_alpha_chain = Chain.query.filter_by(name="TNF-alpha").first()

# create the chains we need
state_names = ["Uninitialized", "No TNF-alpha","TNF-alpha",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=tnf_alpha_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=tnf_alpha_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(tnf_alpha_chain)

'''

And the relevant TPs:

'''

# Become ESRD rate
make_tp(tnf_alpha_chain, "No TNF-alpha","TNF-alpha", False, 0.1)


'''

##### TNF Interactions

TNF-alpha inhibitor patients more likely to progress to active TB

'''

make_intr("TNF-alpha", "Slow latent", "Active - untreated", 1.1)
make_intr("TNF-alpha", "Fast latent", "Active - untreated", 1.1)


'''


We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="tnf-alpha.jpg"
visualize_chain(filename,tnf_alpha_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="tnf-alpha-noinit.jpg"
visualize_chain(filename,tnf_alpha_chain, include_initialization=False)
Image(filename)

'''


## Alcohol abuse

'''

# get ESRD chain
alcohol_chain = Chain.query.filter_by(name="Alcohol").first()

# create the chains we need
state_names = ["Uninitialized", "No Alcohol","Alcohol",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=alcohol_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=alcohol_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(alcohol_chain)

'''

And the relevant TPs:

'''

# Become alcohol abuser rate
make_tp(alcohol_chain, "No Alcohol","Alcohol", False, 0.1)
# Recovery rate
make_tp(alcohol_chain, "Alcohol","No Alcohol", False, 0.1)

'''

### Interaction

#### alcohol Abusers more likely to drop out of treatment

'''


all_tb_treatment_states = ['LBTI 9m INH - Month 1',
                        'LBTI 9m INH - Month 2',
                        'LBTI 9m INH - Month 3',
                        'LBTI 9m INH - Month 4',
                        'LBTI 9m INH - Month 5',
                        'LBTI 9m INH - Month 6',
                        'LBTI 9m INH - Month 7',
                        'LBTI 9m INH - Month 8',
                        'LBTI 9m INH - Month 9',
                        'LTBI 6m INH - Month 1',
                        'LTBI 6m INH - Month 2',
                        'LTBI 6m INH - Month 3',
                        'LTBI 6m INH - Month 4',
                        'LTBI 6m INH - Month 5',
                        'LTBI 6m INH - Month 6',
                        'LTBI RIF - Month 1',
                        'LTBI RIF - Month 2',
                        'LTBI RIF - Month 3',
                        'LTBI RIF - Month 4',
                        'LTBI RTP - Month 1',
                        'LTBI RTP - Month 2',
                        'LTBI RTP - Month 3']

for tb_treatment_state in all_tb_treatment_states:
    make_intr("Alcohol", tb_treatment_state, "LTBI Dropped out", 1.1)


'''
    

#### Alcohol Abusers less likely to access care

TODO: interactions with variables?

'''

treatment_option_states = ['LBTI 9m INH - Month 1', 'LTBI 6m INH - Month 1', 'LTBI RIF - Month 1', 'LTBI RTP - Month 1']


for treatment_state in treatment_option_states:
        make_intr("Alcohol", "Slow latent", treatment_state, 0.8)
        make_intr("Alcohol", "Fast latent", treatment_state, 0.8)


'''


TODO: Abusers experience higher side-effects from INH

We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="alcohol.jpg"
visualize_chain(filename,alcohol_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="alcohol-noinit.jpg"
visualize_chain(filename,alcohol_chain, include_initialization=False)
Image(filename)

'''

## Close contacts

'''

# get ESRD chain
close_contacts_chain = Chain.query.filter_by(name="Close contacts").first()

# create the chains we need
state_names = ["Uninitialized", "No close contacts","Close contacts",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=close_contacts_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=close_contacts_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(close_contacts_chain)

'''

And the relevant TPs:

'''

# Become a close TB contact
make_tp(close_contacts_chain, "No close contacts","Close contacts", True, 0.1)

# Lose a close TB contact
make_tp(close_contacts_chain,"Close contacts", "No close contacts", True, 0.1)

'''

We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="close-contacts.jpg"
visualize_chain(filename,close_contacts_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="close-contacts-noinit.jpg"
visualize_chain(filename,close_contacts_chain, include_initialization=False)
Image(filename)

'''


## Foreign born - nation of origin 

'''


# get TB resistance chain
birthplace_chain = Chain.query.filter_by(name='Birthplace').first()

# create the chains we need
state_names = ["Uninitialized", "Afghanistan", "Bangladesh", "Brazil", "Cambodia", "China", "Democratic Republic of Congo", "Ethiopia", "India", "Indonesia", "Kenya", "Myanmar", "Nigeria", "Pakistan", "Philippines", "Russian Federation", "South Africa", "United Republic of Tanzania", "Thailand", "Uganda", "Viet Nam", "Zimbabwe", "Mexico", "Belize", "Guatemala", "El Salvador", "Honduras", "Nicaragua", "Costa Rica", "Panama", "Other African Region", "Other Region of the Americas", "Other South-East Asia Region", "Other European Region", "Other Eastern Mediterranean Region", "Other Western Pacific Region", "United States", "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=birthplace_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=birthplace_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(birthplace_chain)

'''

This is static chain, so there are no transition probabilites.

## Foreign born - how long in US?

'''


# get TB resistance chain
time_in_us_chain = Chain.query.filter_by(name='Length of time in US').first()

# create the chains we need
state_names = ["Uninitialized", "Not Foreign-born", "Less than one year",  "Between one and 5 years", "5 or more years", "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=time_in_us_chain)
    save(the_state)
    
# print chains from database
print State.query.filter_by(chain=time_in_us_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(time_in_us_chain)

'''

The TPs are different for this chain, since everyone will always advance. In order to make this run fast enough, I'm saving all the TPs at the end. 

'''

# tps_to_save = list()
# for index, state_name in enumerate(state_names):
#     if state_name != "Uninitialized" and state_name != "Death" and state_name # != "Not Foreign-born" and state_name != "More than 5 years":
#         if index < len(state_names)-1:
#             from_state = State.query.filter_by(name=state_name,chain=# time_in_us_chain).first()
#             to_state = State.query.filter_by(name=state_names[index+1],chain=# time_in_us_chain).first()
#             if from_state == None:
#                 print "Error - cannot find from state: " + from_name
#                 sys.exit(0)
#             if to_state == None:
#                 print "Error - cannot find to state: " + to_state
#                 sys.exit(0)
#             tp = Transition_probability(
#                 description="From " + from_state.name+ " to "+ to_state.name,
#                 from_state=from_state,
#                 to_state=to_state,
#                 from_state_name=from_state.name,
#                 to_state_name=to_state.name,
#                 tp_base=1,
#                 is_dynamic=False
#             )
#             tps_to_save.append(tp)
# 
#     db.session.add_all(tps_to_save)
#     db.session.commit()
# 
# #make final TP
# 
# make_tp(time_in_us_chain, 'In US for 5.0 years', "More than 5 years", False, 1)

'''

We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="time-in-us.jpg"
visualize_chain(filename,time_in_us_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''
filename="time-in-us-noinit.jpg"
visualize_chain(filename,time_in_us_chain, include_initialization=False)
Image(filename)

'''

## Foreign born - visa

'''


# get TB resistance chain
citizen_chain = Chain.query.filter_by(name='Citizen').first()

# create the chains we need
state_names = ["Uninitialized", 'Born in US', 'Naturalized citizen', 'Not a citizen', 'Born abroad of American parents', 'Death']

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=citizen_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=citizen_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(citizen_chain)

'''

This is static chain, so there are no transition probabilites. We can visualize this chain, including the Uninitialized transitions. 

'''

link_tps_to_chains()
filename="visa.jpg"
visualize_chain(filename,citizen_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="visa-noninit.jpg"
visualize_chain(filename,citizen_chain, include_initialization=False)
Image(filename)

'''
    
# Race

'''

# get TB resistance chain
race_chain = Chain.query.filter_by(name="Race").first()

# create the chains we need
state_names = ["Uninitialized", "Asian", "Hispanic", "Black", "White", "Other",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=race_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=race_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(race_chain)

'''


We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="race.jpg"
visualize_chain(filename,race_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''
filename="race-noinit.jpg"
visualize_chain(filename,race_chain, include_initialization=False)
Image(filename)

'''

# Sex

'''

# get TB resistance chain
sex_chain = Chain.query.filter_by(name="Sex").first()

# create the chains we need
state_names = ["Uninitialized", "Male", "Female",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=sex_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=sex_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(sex_chain)

'''


We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="sex.jpg"
visualize_chain(filename,sex_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''
filename="sex-noinit.jpg"
visualize_chain(filename,sex_chain, include_initialization=False)
Image(filename)

'''


# Age groupings

To facilitate a not-crazy age system, I'd like to use larger groupings for age.

'''

# get TB resistance chain
age_grouping_chain = Chain.query.filter_by(name="Age grouping").first()

# create the states we need
state_names = ['Uninitialized', "Age 15-19","Age 20-24","Age 25-29","Age 30-34","Age 35-39","Age 40-44","Age 45-49","Age 50-54","Age 55-59","Age 60-64","Age 65-69","Age 70-74","Age 75-79","Age 80+", 'Death']

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=age_grouping_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=age_grouping_chain).all()
'''

Initialization

'''

create_initialization_tps(age_grouping_chain)



''' 
Interation with TNF-alpha

'''


make_intr("Age 35-39", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 40-44", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 45-49", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 50-54", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 55-59", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 60-64", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 65-69", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 70-74", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 75-79", "No TNF-alpha", "TNF-alpha", 1.1)
make_intr("Age 80+", "No TNF-alpha", "TNF-alpha", 1.1)


'''

Transitions will be handled through a synronization system.

# Natural death

We will also need a chain for natural death. 

## Natural death states

Let's get the chain for death, and add these states to the chain.

'''
# get TB resistance chain
natural_death_chain = Chain.query.filter_by(name="Natural death").first()

# create the chains we need
state_names = ["Uninitialized", "Life", "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=natural_death_chain)
    save(the_state)
    
# print chains from database
print State.query.filter_by(chain=natural_death_chain).all()
'''

## Natural death transition probabilites

Now let's add in the transition probabilites that we're interested in.

First, let's add the initializations TPs.

'''

create_initialization_tps(natural_death_chain)

'''

Now, let's add the other transitions we're interested in 

'''

# Risk of dying of non-DM, non-TB, non-HIV causes
make_tp(natural_death_chain, "Life", "Death", False, 0.1)


'''

We can visualize this chain, including the Uninitialized transitions. 

'''

filename="death.jpg"
link_tps_to_chains()
visualize_chain(filename,natural_death_chain, include_initialization=True)
Image(filename)

'''



# Diabetes

Now we can move on to building the diabetes related chains. Because we want treated diabetes to have a different interaction with TB than untreated diabetes, we need to have these as one chain. 

I've simplified the model into only haiving four disease states:

* No diabetes
* Pre-diabetes (no understood risk for TB, but good for sensitivity analysis)
* Diabetes untreated
* Diabetes treated

## DM states

Let's get the chain for resistance, and add these states to the chain.

'''
# get TB resistance chain
diabetes_chain = Chain.query.filter_by(name="Diabetes").first()

# create the chains we need
state_names = ["Uninitialized", "No diabetes", "Diabetes", "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=diabetes_chain)
    save(the_state)
    
# print chains from database
print State.query.filter_by(chain=diabetes_chain).all()
'''

## DM transition probabilites

Now let's add in the transition probabilites that we're interested in.

First, let's add the initializations TPs.

'''

create_initialization_tps(diabetes_chain)

'''

Now, let's add the other transitions we're interested in 

'''

make_tp(diabetes_chain, 'No diabetes', "Diabetes", False, 0.1)
# Risk of becoming pre-diabetic
# make_tp(diabetes_chain, 'No diabetes', "Pre-diabetes", False, 0.1)


# Risk of becoming diabetic once pre-diabetic
# make_tp(diabetes_chain, "Pre-diabetes", "Diabetes untreated", False, 0.1)

# Treatment recruitment rate
# make_tp(diabetes_chain, "Diabetes untreated", "Diabetes treated", False, 0.1)

# Mortality from diabetes
# make_tp(diabetes_chain, "Diabetes untreated", "Death", False, 0.1)
# make_tp(diabetes_chain, "Diabetes treated", "Death", False, 0.1)






'''

We can visualize this chain, including the Uninitialized transitions. 

'''

link_tps_to_chains()
filename="dm.jpg"
visualize_chain(filename,diabetes_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="dm-noninit.jpg"
visualize_chain(filename,diabetes_chain, include_initialization=False)
Image(filename)

'''


## DM Interaction

Diabetics (treated and untreated) more likely to progress to active TB

'''

make_intr("Diabetes", "Slow latent", "Active - untreated", 1.1)
make_intr("Diabetes", "Fast latent", "Active - untreated", 1.1)
# make_intr("Diabetes treated", "Slow latent", "Active - untreated", 1.1)
# make_intr("Diabetes treated", "Fast latent", "Active - untreated", 1.1)

'''


Diabeties incidence based on age

'''

'''

ESRD more likely to occur in diabetics

'''

make_intr("Diabetes", "No ESRD", "ESRD", 1.1)



# 20-24   0.000994
# 25-29   0.001693
# 30-34   0.002422
# 35-39   0.003611
# 40-44   0.006399
# 45-49   0.007944
# 50-54   0.011015
# 55-59   0.011268
# 60-64   0.010361
# 65-69   0.009888
# 70-74   0.008723
# 75-79   0.008019333
# 80+ 0.007200 


'''







# Cycles

We can make some cycles.

'''

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

save(Cycle(name="Initialization",year=2014))

for year in range(2015,2100):
    for month in months:
        name = month + " " + str(year)
        save(Cycle(name=name, year=year))


'''
    


# HIV disease

Now, lets turn our attention to the HIV model. Let's start by building the
disease model. Let's first build the states.

'''

# get TB resistance chain
hiv_chain = Chain.query.filter_by(name="HIV").first()

# create the chains we need
state_names = ["Uninitialized", "Uninfected HIV", "Infected HIV, no ART", "Infected HIV, ART", "Death" ]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=hiv_chain)
    save(the_state)
    
# print chains from database
'''


First, let's add the initializations TPs.

'''

create_initialization_tps(hiv_chain)

'''


## HIV Interactions

HIV increases risk of progression to active disease:

'''

all_hiv_pos_states = ["Infected HIV, no ART", "Infected HIV, ART",]

for hiv_pos_state in all_hiv_pos_states:
    make_intr(hiv_pos_state, "Slow latent", "Active - untreated", 1.1)
    make_intr(hiv_pos_state, "Fast latent", "Active - untreated", 1.1)

'''

HIV increases risk of TB mortality - excluded for now

'''

'''
all_hiv_pos_states = ["Acute, no ART",
"Early, no ART",
"Late, no ART",
"Advanced/AIDS, no ART",
"Acute, with ART",
"Early, with ART",
"Late, with ART",
"Advanced/AIDS, with ART"]

all_active_tb_states = ['Active - untreated','Active Treated Month 1','Active Treated Month 2','Active Treated Month 3','Active Treated Month 4','Active Treated Month 5','Active Treated Month 6']

# cant use make_intr bc "death" is ambigous, make states named death
for hiv_pos_state in all_hiv_pos_states:
    for active_tb_state in all_active_tb_states:
        in_state=State.query.filter_by(name=hiv_pos_state,chain=hiv_chain).first()
        from_state=State.query.filter_by(name=active_tb_state,chain=tb_chain).first()
        to_state=State.query.filter_by(name="Death",chain=tb_chain).first()
        adjustment=1.1
        affected_chain=tb_chain
        description = "RR/OR of transfering from " + from_state.name + " to " + to_state.name + " if in: " + in_state.name
        save(Interaction(
            from_state_name=from_state.name,
            to_state_name=to_state.name,
            in_state_name=in_state.name,
            in_state=in_state,
            from_state=from_state,
            to_state=to_state,
            description=description,
            adjustment=adjustment,
            affected_chain=affected_chain))
'''

'''

HIV treatment increases access to treatment (currently just making an interaction from treatment enrollment). TODO: interactions with variables?

'''

'''
all_hiv_treatement_states = ["Infected HIV, ART"]

treatment_option_states = ['LBTI 9m INH - Month 1', 'LTBI 6m INH - Month 1', 'LTBI RIF - Month 1', 'LTBI RTP - Month 1']

for hiv_treatement_state in all_hiv_treatement_states:
    for treatement_state in treatment_option_states:
        make_intr(hiv_treatement_state, "Slow latent", treatement_state, 1.1)
        make_intr(hiv_treatement_state, "Fast latent", treatement_state, 1.1)
'''
'''


### Infection

'''

make_tp(hiv_chain, "Uninfected HIV", "Infected HIV, no ART", True, 0.1)


'''

### Progression - exlcuded for now

'''

'''
# No ART

make_tp(hiv_chain, "Acute, no ART", "Early, no ART", False, 0.1)
make_tp(hiv_chain, "Early, no ART", "Late, no ART", False, 0.1)
make_tp(hiv_chain, "Late, no ART", "Advanced/AIDS, no ART", False, 0.1)

# With ART

make_tp(hiv_chain, "Acute, with ART", "Early, with ART", False, 0.1)
make_tp(hiv_chain, "Early, with ART", "Late, with ART", False, 0.1)
make_tp(hiv_chain, "Late, with ART" , "Advanced/AIDS, with ART", False, 0.1)
'''


'''

### Treatment dropout

'''


make_tp(hiv_chain, "Infected HIV, ART", "Infected HIV, no ART", False, 0.1)


'''

### Treatment uptake

'''

make_tp(hiv_chain, "Infected HIV, no ART", "Infected HIV, ART", False, 0.1)


'''

### Mortality

'''

all_hiv_pos_states = ["Infected HIV, no ART", "Infected HIV, ART"]

for hiv_pos_state in all_hiv_pos_states:
    make_tp(hiv_chain, hiv_pos_state, "Death", False, 0.1)

'''



### Visualize

We can visualize this chain, including the Uninitialized transitions:

'''

link_tps_to_chains()
filename="hiv_chain.png"
visualize_chain(filename, hiv_chain, include_initialization=True)
Image(filename)

'''

Or, a cleaner approach, just showing the transitions within intitialized states:

'''

filename="hiv_chain_noinit.png"
visualize_chain(filename,hiv_chain, include_initialization=False)
Image(filename)

'''





# HIV Risk Groups TODO

'''

hiv_risk_groups = Chain.query.filter_by(name="HIV risk groups").first()

# create the chains we need
state_names = ["Uninitialized", "General population men", "General population women", "IDU", "MSM", "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=hiv_risk_groups)
    save(the_state)
    
# print chains from database
print State.query.filter_by(chain=hiv_risk_groups).all()

'''



First, let's add the initializations TPs.

'''

create_initialization_tps(hiv_risk_groups)

'''


# Transplants

'''

# get TB resistance chain
transplant_chain = Chain.query.filter_by(name="Transplants").first()

# create the chains we need
state_names = ["Uninitialized", "Not transplant patient","Transplant patient",  "Death"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=transplant_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=transplant_chain).all()
'''

Add the initialization states.

'''

create_initialization_tps(transplant_chain)

'''

And the relevant TPs:

'''

# Become homeless rate
make_tp(transplant_chain, "Not transplant patient","Transplant patient", False, 0.1)


'''

Transplant patients more likely to progress to active TB

'''

make_intr("Transplant patient", "Slow latent", "Active - untreated", 1.1)
make_intr("Transplant patient", "Fast latent", "Active - untreated", 1.1)


'''


# Medical risk factor

'''

med_risk_chain = Chain.query.filter_by(name="Medical risk factor").first()

state_names = [ 'Uninitialized', 'No medical risk factor', 'Medical risk factor', 'Death']

for state_name in state_names:
    the_state = State(name=state_name,chain=med_risk_chain)
    save(the_state)


states_with_medical_risk_factor = [  "Smoker", "ESRD", "TNF-alpha", "Diabetes", "Infected HIV, no ART", "Infected HIV, ART", "Transplant patient" ]

print "states with medical risk factors"
for state_name in states_with_medical_risk_factor:
    print state_name
    state = State.query.filter_by(name=state_name).first()
    state.is_medical_risk_factor = True
    save(state)

create_initialization_tps(med_risk_chain)



'''
    
# SMRs

'''

states_that_have_smrs = ["Infected HIV, no ART","Infected HIV, ART","Diabetes","Homeless","ESRD","TNF-alpha","Smoker","Transplant patient","IDU","Alcohol"]


for state_name in states_that_have_smrs:
    in_state=State.query.filter_by(name=state_name).first()
    from_state=State.query.filter_by(name="Life",chain=natural_death_chain).first()
    to_state=State.query.filter_by(name="Death",chain=natural_death_chain).first()
    adjustment=1.1
    affected_chain=natural_death_chain
    print "SMR " + state_name
    description = "RR/OR of transfering from " + from_state.name + " to " + to_state.name + " if in: " + in_state.name
    save(Interaction(
        from_state_name=from_state.name,
        to_state_name=to_state.name,
        in_state_name=in_state.name,
        in_state=in_state,
        from_state=from_state,
        to_state=to_state,
        description=description,
        adjustment=adjustment,
        affected_chain=affected_chain))

'''

# Linking deaths to is_death_state 

'''

all_states = State.query.all()
for state in all_states:
    if state.name == "Death":
        print state
        state.is_death_state = True
        save(state)
    if state.name == "Uninitialized":
        print state
        state.is_uninitialized_state = True
        save(state)

'''


# Interventions

'''

save(Intervention(name="Control"))
save(Intervention(name="Test FB 10%"))





'''


# Synchronization 
# Test a synronization

'''

#sync = Synchronization(
#    trigger_state=State.query.filter_by(name="Default").first(),
#    to_state=State.query.filter_by(name="Default").first()
#)
#
#db.session.add(sync)
#db.session.commit()

'''

# Costs

And some costs.

'''

for state in State.query.all():
    save(Cost(state=state, state_name=state.name, costs=0))

'''
    
# Disability Weights

And some DWs.

'''

for state in State.query.all():
    save(Disability_weight(state=state, state_name=state.name, disability_weight=0))


'''

# Events

'''

events = ["TST test", "QFT test", "TSPOT", "TST+QFT", "TST+QFT"]
#TODO fill in


'''




# Stratify initialization

'''

from stratify import *

'''
    




# Fixing the zero index issue

Since SQL and SQLAlchemy are 1-index and the go model is 0-indexed. Need to adjust the primary keys and all foreign keys.

TODO: Check if already zero-indexed from past run


<!--

models_to_update = [ Chain, Cost, Cycle, Disability_weight, 
Interaction,  State, Transition_probability, Intervention, Stratum_type, Stratum, Stratum_type_content, Stratum_content, Transition_probability_by_stratum, Variable_by_stratum]
for model in models_to_update:
    table_name = model.__tablename__
    print "Updating table: " + table_name
    db.engine.execute("UPDATE '" + table_name +"' SET id = id - 1")
    cols = model.__table__.columns.keys()
    for col in cols:
        does_it = re.compile('.*_id')
        if (does_it.match(col)):
            print col
            db.engine.execute("UPDATE '" + table_name +"' SET " + col + " = " + col + " - 1")

-->

# Import from Google Drive

'''

from import_from_csv import *


'''

# Import from tb sheet

'''

from latent_tb import *


'''

   
    
# Add people from IPUMS

'''

from ipums import *


'''

# Add tracking to TPs

'''


# Active infection from slow latent
tp = Transition_probability.query.filter_by(from_state_name="Slow latent", to_state_name="Active - untreated").first()
tp.is_tracked = True
db.session.add(tp)
db.session.commit()


# Active infection from fast latent
tp = Transition_probability.query.filter_by(from_state_name="Fast latent", to_state_name="Active - untreated").first()
tp.is_tracked = True
db.session.add(tp)
db.session.commit()

# Active infection from unitialized
tp = Transition_probability.query.filter_by(from_state_name="Uninitialized", to_state_name="Active - untreated").first()
tp.is_tracked = True
db.session.add(tp)
db.session.commit()

'''


# Check that all chains have uninit and deaths
# Add recursive tps

'''

#TODO: Turn on recursive

states = State.query.all()

for state in states:
    if state.is_uninitialized_state:
        print "Skipping unit state - no need for recursive tp"
    else:
        sum = 0.0
        print "Adding recursive TP for ",
        print state
        all_tps = Transition_probability.query.filter_by(from_state=state).all()
        if all_tps == None: 
            print state,
            print " has no TPs"
        else:
            for tp in all_tps:
                sum = sum + tp.tp_base
            if sum > 1:
                print "TPs sum to more than one"
                print sum
                print all_tps
                # sys.exit(1)
            recursive_tp_base = 1 - sum
            recursive_tp = Transition_probability(
                description="Recursive TP",
                from_state=state,
                to_state=state,
                tp_base=recursive_tp_base
                )
            save(recursive_tp)




'''

Remove recursive Tps for tunnel states

'''

tunnel_state_ids = [i.id for i in State.query.filter_by(is_tunnel=True).all()]
for tunnel_state_id in tunnel_state_ids:
    db.session.delete(Transition_probability.query.filter_by(to_state_id=tunnel_state_id,from_state_id=tunnel_state_id).first())
db.session.commit()



'''

# Get variabes

'''

from set_variables import *


from get_variables import *





'''
    



TODO: Initializing the model will be a challenge, becasue there is interaction between the chains for initiail placement (ie, more HIV+ people will have TB than HIV-). In order to do this, I propose using a large table to capture all the probabilites of initiailizing in different states, stratified by other states people are in, using a tagging system I'm thinking that a structure like this would be best:

* initialization_probabilities table, with these columns
    - ID
    - State_id (that person will end up in ie, TB+)
    - Tags (ie, HIV+)
    - Probability of initiailizing to this states
* tags table
    - id
    - tag name
* states table
* states-tags association table (ie, join table)

This will allow a person to initalize a model by looking at that model (ie, TB disease), seeing whether tags are required. If they are, the person finds their tags (ie, HIV-, man, urban) and finds the matching initialization probabilities. 





# Run simulation

'''

#is_simulation_done = Variable(name="Is simulation done", value=0.0)
#save(is_simulation_done)

#os.system("cd go && go run limcat.go > log.txt")


'''

Wait for simulation to complete.

'''

#print "Waiting for simulation to complete..."
#while True:
#    is_simulation_done = Variable.query.filter_by(name="Is simulation done").first()
#    if is_simulation_done > 0:
#        print "Done!"
#        break
#    else:
#        print "."

'''
    

Now we can visualize outputs

Remember, need "%matplotlib inline" for notebook

Please see outputs notebook.

'''


#cxn = db.engine.connect()
#engine = db.engine
#df = pd.read_sql_query("SELECT * FROM outputs_by_cycle_state",engine)
#plt.plot(df[df.state_id == 4].population)
#plt.show()




print("Done with limcat.py !")



    


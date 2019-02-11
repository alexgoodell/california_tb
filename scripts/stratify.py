from IPython.display import Image
# For later visualizaton scripts
import pygraphviz as pgv
import time
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import networkx as nx

#connect to application
from app import * 

# clear tables 
db.session.query(Transition_probability_by_stratum).delete()
db.session.query(Variable_by_stratum).delete()
db.session.query(Stratum_content).delete()
db.session.query(Stratum_type_content).delete()
db.session.query(Stratum).delete()
db.session.query(Stratum_type).delete()

db.session.commit()


def stratify_initialization(chain_name, chain_names_to_strat_by):

	chain = Chain.query.filter_by(name=chain_name).first()

	from_state = State.query.filter_by(name="Uninitialized", chain=chain).first()

	#make chain list
	chain_list = list()
	for chain_name_to_strat_by in chain_names_to_strat_by:
		chain_list.append(Chain.query.filter_by(name=chain_name_to_strat_by).first())

	#get tps
	tps = Transition_probability.query.filter_by(from_state=from_state).all()
	for tp in tps:
		stratify_tp_by(tp, chain_list)





# Natural death by age and sex

death_chain = Chain.query.filter_by(name="Natural death").first()
from_state = State.query.filter_by(name="Life", chain=death_chain).first()

chain_names_to_strat_by = [ "Sex", "Age grouping" ]

chain_list = list()
for chain_name_to_strat_by in chain_names_to_strat_by:
	chain_list.append(Chain.query.filter_by(name=chain_name_to_strat_by).first())

to_state = State.query.filter_by(chain=death_chain,name="Death").first()
tp = Transition_probability.query.filter_by(from_state=from_state, to_state=to_state).first()
stratify_tp_by(tp, chain_list) 


## TB

tb_chain = Chain.query.filter_by(name="TB disease and treatment").first()
from_state = State.query.filter_by(name="Uninitialized", chain=tb_chain).first()
to_state_names = ["Slow latent", "Fast latent", "LTBI treated with INH 6m", "Uninfected TB" ]
chain_names_to_strat_by = [ "Length of time in US", "Birthplace", "Sex", "Race", "Age grouping" ]

chain_list = list()
for chain_name_to_strat_by in chain_names_to_strat_by:
	chain_list.append(Chain.query.filter_by(name=chain_name_to_strat_by).first())

for to_state_name in to_state_names:
	to_state = State.query.filter_by(chain=tb_chain,name=to_state_name).first()
	tp = Transition_probability.query.filter_by(from_state=from_state, to_state=to_state).first()
	stratify_tp_by(tp, chain_list)


# Test performance varies based on nativity, ESRD and HIV status
# using "Length of time in US" as proxy for nativity - excluded for now

# chain_names_to_strat_by = [ "Length of time in US", "ESRD", "HIV" ]
# chain_list = list()
# for chain_name_to_strat_by in chain_names_to_strat_by:
# 	chain_list.append(Chain.query.filter_by(name=chain_name_to_strat_by).first())

# tb_chain = Chain.query.filter_by(name="TB disease and treatment").first()

# # ADD IS STRAT


# tps = [
# 	{'from': 'Uninfected Testing TST', 'to': 'FP LBTI 9m INH - Month 1'},
# 	{'from': 'Uninfected Testing TST', 'to': 'FP LTBI 6m INH - Month 1'},
# 	{'from': 'Uninfected Testing TST', 'to': 'FP LTBI RIF - Month 1'},
# 	{'from': 'Uninfected Testing TST', 'to': 'FP LTBI RTP - Month 1'},
# 	{'from': 'Uninfected Testing QFT', 'to': 'FP LBTI 9m INH - Month 1'},
# 	{'from': 'Uninfected Testing QFT', 'to': 'FP LTBI 6m INH - Month 1'},
# 	{'from': 'Uninfected Testing QFT', 'to': 'FP LTBI RIF - Month 1'},
# 	{'from': 'Uninfected Testing QFT', 'to': 'FP LTBI RTP - Month 1'},
# 	{'from': 'Uninfected Testing TSPOT', 'to': 'FP LBTI 9m INH - Month 1'},
# 	{'from': 'Uninfected Testing TSPOT', 'to': 'FP LTBI 6m INH - Month 1'},
# 	{'from': 'Uninfected Testing TSPOT', 'to': 'FP LTBI RIF - Month 1'},
# 	{'from': 'Uninfected Testing TSPOT', 'to': 'FP LTBI RTP - Month 1'},
# 	{'from': 'Uninfected Testing TST+QFT', 'to': 'FP LBTI 9m INH - Month 1'},
# 	{'from': 'Uninfected Testing TST+QFT', 'to': 'FP LTBI 6m INH - Month 1'},
# 	{'from': 'Uninfected Testing TST+QFT', 'to': 'FP LTBI RIF - Month 1'},
# 	{'from': 'Uninfected Testing TST+QFT', 'to': 'FP LTBI RTP - Month 1'},
# 	{'from': 'Uninfected Testing TST+TSPOT', 'to': 'FP LBTI 9m INH - Month 1'},
# 	{'from': 'Uninfected Testing TST+TSPOT', 'to': 'FP LTBI 6m INH - Month 1'},
# 	{'from': 'Uninfected Testing TST+TSPOT', 'to': 'FP LTBI RIF - Month 1'},
# 	{'from': 'Uninfected Testing TST+TSPOT', 'to': 'FP LTBI RTP - Month 1'},

# 	{'from': 'Infected Testing TST', 'to': 'LBTI 9m INH - Month 1'},
# 	{'from': 'Infected Testing TST', 'to': 'LTBI 6m INH - Month 1'},
# 	{'from': 'Infected Testing TST', 'to': 'LTBI RIF - Month 1'},
# 	{'from': 'Infected Testing TST', 'to': 'LTBI RTP - Month 1'},
# 	{'from': 'Infected Testing QFT', 'to': 'LBTI 9m INH - Month 1'},
# 	{'from': 'Infected Testing QFT', 'to': 'LTBI 6m INH - Month 1'},
# 	{'from': 'Infected Testing QFT', 'to': 'LTBI RIF - Month 1'},
# 	{'from': 'Infected Testing QFT', 'to': 'LTBI RTP - Month 1'},
# 	{'from': 'Infected Testing TSPOT', 'to': 'LBTI 9m INH - Month 1'},
# 	{'from': 'Infected Testing TSPOT', 'to': 'LTBI 6m INH - Month 1'},
# 	{'from': 'Infected Testing TSPOT', 'to': 'LTBI RIF - Month 1'},
# 	{'from': 'Infected Testing TSPOT', 'to': 'LTBI RTP - Month 1'},
# 	{'from': 'Infected Testing TST+QFT', 'to': 'LBTI 9m INH - Month 1'},
# 	{'from': 'Infected Testing TST+QFT', 'to': 'LTBI 6m INH - Month 1'},
# 	{'from': 'Infected Testing TST+QFT', 'to': 'LTBI RIF - Month 1'},
# 	{'from': 'Infected Testing TST+QFT', 'to': 'LTBI RTP - Month 1'},
# 	{'from': 'Infected Testing TST+TSPOT', 'to': 'LBTI 9m INH - Month 1'},
# 	{'from': 'Infected Testing TST+TSPOT', 'to': 'LTBI 6m INH - Month 1'},
# 	{'from': 'Infected Testing TST+TSPOT', 'to': 'LTBI RIF - Month 1'},
# 	{'from': 'Infected Testing TST+TSPOT', 'to': 'LTBI RTP - Month 1'}

# ]

# for tp in tps:
# 	to_state = State.query.filter_by(chain=tb_chain,name=tp['to']).first()
# 	from_state = State.query.filter_by(chain=tb_chain,name=tp['from']).first()
# 	db_tp = Transition_probability.query.filter_by(from_state=from_state, to_state=to_state).first()
# 	db_tp.is_stratified = True
# 	db.session.add(db_tp)
# 	db.session.commit()
# 	stratify_tp_by(db_tp, chain_list) 



## TNF-alhpa by age group, sex

stratify_initialization(chain_name="TNF-alpha", 
						chain_names_to_strat_by= [ "Sex", "Age grouping" ])



## Smoking by sex, race, age group

stratify_initialization(chain_name="Smoking", 
						chain_names_to_strat_by= ["Sex", "Race", "Age grouping", "Length of time in US"])


## Homelessness by sex, race, age group

stratify_initialization(chain_name="Homeless", 
						chain_names_to_strat_by= [ "Sex", "Race", "Age grouping" ])



## Alcohol abuse by homelessness, sex, race, age group

stratify_initialization(chain_name="Alcohol", 
						chain_names_to_strat_by= [ "Homeless" , "Sex", "Race", "Age grouping" ])


## Diabetes by sex, race, age group

stratify_initialization(chain_name="Diabetes", 
						chain_names_to_strat_by= [ "Sex", "Race", "Age grouping", "Length of time in US" ])



## ESRD abuse by Diabetes, sex, race, age group

stratify_initialization(chain_name="ESRD", 
						chain_names_to_strat_by= [ "Diabetes" , "Sex", "Race", "Age grouping" ])



## Transplants by sex, race, age group

stratify_initialization(chain_name="Transplants", 
						chain_names_to_strat_by= [ "Sex", "Race", "Age grouping" ])



## HIV initialization by sex, race, age group

stratify_initialization(chain_name="HIV", 
						chain_names_to_strat_by= [ "Sex", "HIV risk groups", "Race", "Age grouping" ])




## HIV risk group by sex

stratify_initialization(chain_name="HIV risk groups", 
						chain_names_to_strat_by= [ "Sex" ])







# if running this outside of limcat.md, need to run this script as well

# models_to_update = [ Stratum_type, Stratum, Stratum_type_content, Stratum_content, Transition_probability_by_stratum, Variable_by_stratum]

# for model in models_to_update:
#     table_name = model.__tablename__
#     print "Updating table: " + table_name
#     db.engine.execute("UPDATE '" + table_name +"' SET id = id - 1")
#     cols = model.__table__.columns.keys()
#     for col in cols:
#         does_it = re.compile('.*_id')
#         if (does_it.match(col)):
#             print col
#             db.engine.execute("UPDATE '" + table_name +"' SET " + col + " = " + col + " - 1")












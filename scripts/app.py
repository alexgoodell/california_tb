# ---------------- Import packages ----------------

from IPython.display import Image
import pygraphviz as pgv
import time
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import itertools
import os

# ---------------- Flask-specific details ----------------
# flask is a python package for making web pages
# we use this little currently, but is helpful

from flask import Flask, render_template, session, redirect, url_for, flash
app = Flask(__name__)

app.config['SECRET_KEY'] = 'x3432d3232432lkjew3242'
# allows for debuging mode in runserver
app.config['DEBUG'] = True 

from flask.ext.script import Manager, Shell
manager = Manager(app)


# ---------------- Connect to SQLite -------------------------

from flask.ext.sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database/limcat-zero-index.sqlite')
    # 'sqlite:///' + os.path.join(basedir, 'database/limcat.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

# ---------------- Models -------------------------
# This defines the data structure that goes into the SQLite database


class Chain(db.Model):
	__tablename__ = 'chains'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	states = db.relationship('State', backref='Chain')

	def __repr__(self):
		return self.name

class Intervention(db.Model):
	__tablename__ = 'interventions'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	def __repr__(self):
		return self.name

# Not in use - can delete
class Transition_probability_by_intervention(db.Model):
	__tablename__ = 'transition_probabilities_by_intervention'

	id = db.Column(db.Integer, primary_key=True)
	intervention_id = db.Column(db.Integer,db.ForeignKey('interventions.id'))
	transition_probility_id = db.Column(db.Integer,db.ForeignKey('transition_probabilities.id'))
	replacement_tp  = db.Column(db.Float)

	def __repr__(self):
		return self.id

# Not in use - can delete
class Event(db.Model):
	__tablename__ = 'events'

	id = db.Column(db.Integer, primary_key=True)
 	state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	state_name = db.Column(db.String(2000))
	name = db.Column(db.String(2000))
	costs = db.Column(db.Float)
	ylls = db.Column(db.Float)
	probability = db.Column(db.Float)
	state = db.relationship("State", foreign_keys=[state_id])


	def __repr__(self):
		return self.state.name


class Cost(db.Model):
	__tablename__ = 'costs'
	
	id = db.Column(db.Integer, primary_key=True)
 	state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	state_name = db.Column(db.String(2000))
	costs = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)
	state = db.relationship("State", foreign_keys=[state_id])

	def __repr__(self):
		return self.state.name + " costs"

class Disability_weight(db.Model):
	__tablename__ = 'disability_weights'
	
	id = db.Column(db.Integer, primary_key=True)
 	state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	disability_weight = db.Column(db.Float)
	state = db.relationship("State", foreign_keys=[state_id])
	state_name = db.Column(db.String(2000))
	low = db.Column(db.Float)
	high = db.Column(db.Float)
	
	def __repr__(self):
		return self.state.name + " disability weight"


class Cycle(db.Model):
	__tablename__ = 'cycles'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	year = db.Column(db.Integer)

	def __repr__(self):
		return self.name


class State(db.Model):
	__tablename__ = 'states'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	is_uninitialized_state = db.Column(db.Boolean)
	is_death_state = db.Column(db.Boolean)

	chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))
	chain = db.relationship("Chain", foreign_keys=[chain_id])

	is_medical_risk_factor = db.Column(db.Boolean)

	is_tunnel = db.Column(db.Boolean)
	tunnel_target_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	#tunnel_target = db.relationship("State", foreign_keys=[tunnel_target_id])

	# TODO: Add chain name to representation
	def __repr__(self):
		return self.name

class Transition_probability(db.Model):
	__tablename__ = 'transition_probabilities'
	
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(2000))
	
	from_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	to_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	from_state = db.relationship("State", foreign_keys=[from_state_id])
	to_state = db.relationship("State", foreign_keys=[to_state_id])

	from_state_name = db.Column(db.String(2000))
	to_state_name = db.Column(db.String(2000))

	tp_base = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)

	is_dynamic = db.Column(db.Boolean)
	is_tracked = db.Column(db.Boolean)

	dynamic_function_name = db.Column(db.String(64))
	is_stratified = db.Column(db.Boolean)

	stratum_type_id = db.Column(db.Integer,db.ForeignKey('stratum_types.id'))
	stratum_type = db.relationship("Stratum_type", foreign_keys=[stratum_type_id])

	chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))
	chain = db.relationship("Chain", foreign_keys=[chain_id])

	def __repr__(self):
		return self.from_state.name + " => " + self.to_state.name

class Interaction(db.Model):
	__tablename__ = 'interactions'
	
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(2000))
	
	in_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	from_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	to_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	in_state = db.relationship("State", foreign_keys=[in_state_id])
	from_state = db.relationship("State", foreign_keys=[from_state_id])
	to_state = db.relationship("State", foreign_keys=[to_state_id])

	from_state_name = db.Column(db.String(2000))
	to_state_name = db.Column(db.String(2000))
	in_state_name = db.Column(db.String(2000))

	adjustment = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)


	affected_chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))
	affected_chain = db.relationship("Chain", foreign_keys=[affected_chain_id])

	def __repr__(self):
		return self.in_state.name + " affects " + self.from_state.name + " => " + self.to_state.name


class Variable(db.Model):
	__tablename__ = 'variables'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	value = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)

	def __repr__(self):
		return self.name


# no forgien keys for now
class OutputByCycleState(db.Model):
	__tablename__ = 'outputs_by_cycle_state'
	
	id = db.Column(db.Integer, primary_key=True)
	ylls = db.Column(db.Float)
	ylds = db.Column(db.Float)
	population = db.Column(db.Integer)
	costs = db.Column(db.Float)
	dalys = db.Column(db.Float)
	cycle_id = db.Column(db.Integer)
	state_id = db.Column(db.Integer)
	state_name = db.Column(db.String(64))
	intervention_id = db.Column(db.Integer)

	def __repr__(self):
		return "Cycle: " + str(self.cycle_id) + " State: " + state_name

class OutputByCycle(db.Model):
	id  = db.Column(db.Integer, primary_key=True)
	cycle_id = db.Column(db.Integer)
	event_description = db.Column(db.String(64))
	event_count = db.Column(db.Integer)

	def __repr__(self):
		return "Cycle: " + self.cycle_id


class Raw_input(db.Model):
	__tablename__ = 'raw_inputs'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	slug = db.Column(db.String(64), unique=True)
	value = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)
	reference_id = db.Column(db.Integer,db.ForeignKey('references.id'))

	def __repr__(self):
		return self.name

class Reference(db.Model):
	__tablename__ = 'references'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(4000))
	bibtex = db.Column(db.String(2000))
	raw_data = db.relationship('Raw_input', backref='reference')

	def __repr__(self):
		return self.name


# ----- Stratification system -----

# This describes a type of cross-section of the population, such as "gender - ethnicity - age"
class Stratum_type(db.Model):
	__tablename__ = 'stratum_types'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(4000))

	stratum_type_contents = db.relationship('Stratum_type_content', backref='Stratum_type')

	def __repr__(self):
		return self.name	
	
# This describes a specific grouping of people, for example "men - African American - 25 years old"
class Stratum(db.Model):
	__tablename__ = 'strata'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(4000))

	stratum_hash = db.Column(db.String(200))

	stratum_type_id = db.Column(db.Integer,db.ForeignKey('stratum_types.id'))
	stratum_type =  db.relationship("Stratum_type", foreign_keys=[stratum_type_id])

	stratum_contents = db.relationship('Stratum_content', backref='Stratum')
	
	def __repr__(self):
		return self.name	

# This specifies which chains (aka models) are a part of a stratum type, for
# example, for the statum type "gender - ethnicity - age", there would be 
#  three rows in stratum_type_content: gender, ethnicity, and age.
class Stratum_type_content(db.Model):
	__tablename__ = 'stratum_type_contents'
	id = db.Column(db.Integer, primary_key=True)
	stratum_type_id = db.Column(db.Integer,db.ForeignKey('stratum_types.id'))
	chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))

	stratum_type = db.relationship("Stratum_type", foreign_keys=[stratum_type_id])
	chain = db.relationship("Chain", foreign_keys=[chain_id])	


	def __repr__(self):
		return self.stratum_type.name + ": " + self.chain.name	

# This specifies which *states* are associated with a stratum. For example, 
# the stratum "men - African American - 25 years old" would have three rows:
# men state, African american state, and 25 years old state
class Stratum_content(db.Model):
	__tablename__ = 'stratum_contents'
	id = db.Column(db.Integer, primary_key=True)
	stratum_id = db.Column(db.Integer,db.ForeignKey('strata.id'))
	chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))
	state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	stratum = db.relationship("Stratum", foreign_keys=[stratum_id])
	chain = db.relationship("Chain", foreign_keys=[chain_id])	
	state = db.relationship("State", foreign_keys=[state_id])	

	def __repr__(self):
		return self.stratum.name + ": " + self.state.name	

# This specifes a specific TP for a specifc statrum of individuals. For example,
# it might look something like this:
#
#   | from_state | to_state | stratum                    | base | low  | high |
#   +------------+----------+----------------------------+------+------+------+
#   | no diabtes | diabetes | white-male-25yo            | 0.1  | 0.05 | 0.2  |
#   | no diabtes | diabetes | african-american-male-25yo | 0.2  | 0.1  | 0.3  |
#

class Transition_probability_by_stratum(db.Model):
	
	__tablename__ = 'transition_probabilities_by_stratum'
	
	id = db.Column(db.Integer, primary_key=True)

	stratum_id = db.Column(db.Integer,db.ForeignKey('strata.id'))
	stratum = db.relationship("Stratum", foreign_keys=[stratum_id])

	from_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	to_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	from_state = db.relationship("State", foreign_keys=[from_state_id])
	to_state = db.relationship("State", foreign_keys=[to_state_id])

	transition_probability_id = db.Column(db.Integer,db.ForeignKey('transition_probabilities.id'))
	transition_probability = db.relationship("Transition_probability", foreign_keys=[transition_probability_id])

	stratum_name = db.Column(db.String(4000))
	from_state_name = db.Column(db.String(4000))
	to_state_name = db.Column(db.String(4000))

	chain_name = db.Column(db.String(4000))


	base = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)

	def __repr__(self):
		return self.from_state.name + " => " + self.to_state.name + " in " + self.stratum.name


# below is currently not in use

# This specifes a specific variable for a specifc statrum of individuals. For example,
# it might look something like this:
#
#   | variableId | stratum                    | base | low  | high |
#   +------------+----------------------------+------+------+------+
#   | risk of X  | white-male-25yo            | 0.1  | 0.05 | 0.2  |
#   | risk of X  | african-american-male-25yo | 0.2  | 0.1  | 0.3  |

class Variable_by_stratum(db.Model):
	
	__tablename__ = 'variables_by_stratum'
	
	id = db.Column(db.Integer, primary_key=True)

	stratum_id = db.Column(db.Integer,db.ForeignKey('strata.id'))
	stratum = db.relationship("Stratum", foreign_keys=[stratum_id])

	variable_id = db.Column(db.Integer,db.ForeignKey('variables.id'))
	variable = db.relationship("Variable", foreign_keys=[variable_id])

	base = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)

	def __repr__(self):
		return self.variable.name + " by " + self.stratum.name


# syncronization

class Synchronization(db.Model):
	
	__tablename__ = 'synchronizations'
	
	id = db.Column(db.Integer, primary_key=True)

	trigger_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	to_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	trigger_state = db.relationship("State", foreign_keys=[trigger_state_id])
	to_state = db.relationship("State", foreign_keys=[to_state_id])

	def __repr__(self):
		return "Entering state " + self.trigger_state.name + " forces transition to " + self.to_state.name


class BaseInitLine(db.Model):
	
	__tablename__ = 'base_init_lines'
	
	id = db.Column(db.Integer, primary_key=True)
	sex = db.Column(db.String(200))
	race = db.Column(db.String(200))
	age_group = db.Column(db.String(200))
	years_in_us = db.Column(db.String(200))
	citizen = db.Column(db.String(200))
	birthplace = db.Column(db.String(200))
	weight2001 = db.Column(db.Integer)
	weight2014 = db.Column(db.Integer)

	weight_new_people2001  = db.Column(db.Integer)
	weight_new_people2002  = db.Column(db.Integer)
	weight_new_people2003  = db.Column(db.Integer)
	weight_new_people2004  = db.Column(db.Integer)
	weight_new_people2005  = db.Column(db.Integer)
	weight_new_people2006  = db.Column(db.Integer)
	weight_new_people2007  = db.Column(db.Integer)
	weight_new_people2008  = db.Column(db.Integer)
	weight_new_people2009  = db.Column(db.Integer)
	weight_new_people2010  = db.Column(db.Integer)
	weight_new_people2011  = db.Column(db.Integer)
	weight_new_people2012  = db.Column(db.Integer)
	weight_new_people2013  = db.Column(db.Integer)
	weight_new_people2014  = db.Column(db.Integer)





	def __repr__(self):
		return "todo"


class IpumsCurrentPerson(db.Model):
	
	__tablename__ = 'ipums_current_people'
	
	id = db.Column(db.Integer, primary_key=True)
	sex = db.Column(db.String(200))
	race = db.Column(db.String(200))
	age_group = db.Column(db.String(200))
	years_in_us = db.Column(db.String(200))
	citizen = db.Column(db.String(200))
	birthplace = db.Column(db.String(200))

	def __repr__(self):
		return "todo"

class IpumsNewPerson(db.Model):
	
	__tablename__ = 'ipums_new_people'
	
	id = db.Column(db.Integer, primary_key=True)
	sex = db.Column(db.String(200))
	race = db.Column(db.String(200))
	age_group = db.Column(db.String(200))
	years_in_us = db.Column(db.String(200))
	citizen = db.Column(db.String(200))
	birthplace = db.Column(db.String(200))

	def __repr__(self):
		return "todo"


# ---------------- Functions -------------------------   

# TODO: missing high, low
def stratify_tp_by(transition_probability, chains):
	transition_probability.is_stratified = True
	if get_stratum_id(chains) == False:
		create_strata_by(chains)
	stratum_type = get_stratum_id(chains)
	print stratum_type
	strata = Stratum.query.filter_by(stratum_type=stratum_type).all()

	transition_probability.stratum_type_id = stratum_type.id

	print strata
	for stratum in strata:
		from_state = transition_probability.from_state
		to_state = transition_probability.to_state
		tp_base = transition_probability.tp_base
		new_tp_bs = Transition_probability_by_stratum(
			transition_probability=transition_probability,
			stratum = stratum,
			from_state = from_state,
			to_state = to_state,
			base = 99, # this is to make sure it fails if this value is not replace
			stratum_name = stratum.name,
			from_state_name = from_state.name,
			to_state_name = to_state.name,
			chain_name = to_state.chain.name
		)
		db.session.add(new_tp_bs)
	db.session.add(transition_probability)
	db.session.commit()

# TODO: missing high, low
def stratify_var_by(variable, chains):
	if get_stratum_id(chains) == False:
		create_strata_by(chains)
	stratum_type = get_stratum_id(chains)
	print stratum_type
	strata = Stratum.query.filter_by(stratum_type=stratum_type).all()
	print strata
	for stratum in strata:
		new_var_bs = Variable_by_stratum(
			stratum = stratum,
			variable = variable,
			base = variable.value
		)
		db.session.add(new_var_bs)
	db.session.commit()



def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]


def get_stratum_id(chains):
 	# Create stratum type
	stratum_type = Stratum_type()
	stratum_type.name = ""
	for chain in chains:
		stratum_type.name = stratum_type.name + " " + chain.name

	# Check to see if this stratafication has already been made,
	# if so, return the id of that strata type
	results = Stratum_type.query.filter_by(name=stratum_type.name).all()
	if len(results) > 1:
		# there should be at most one
		print "error with strata"
		sys.exit(0)
	elif len(results) > 0:
		return results[0]
	else:
		return False



def create_strata_by(chains):
	state_list_list = list()
	for chain in chains:
		state_list = State.query.filter(
			State.chain == chain, 
			State.name != "Death",
			State.name != "Uninitialized",
		).all()
		# print state_list[0].id
		state_list_list.append(state_list)
	all_strata = list(itertools.product(*state_list_list))

	# Create stratum type
	stratum_type = Stratum_type()
	stratum_type.name = ""
	for chain in chains:
		stratum_type.name = stratum_type.name + " " + chain.name
	
	# Create stratum type contents
	for chain in chains:
		stratum_type_content = Stratum_type_content()
		stratum_type_content.stratum_type = stratum_type
		# print stratum_type
		stratum_type_content.chain = chain
		# print chain
		db.session.add(stratum_type_content)
		db.session.commit()

	# Create strata and stata contents
	for stratum_states in all_strata:
		stratum = Stratum()
		stratum.stratum_type = stratum_type
		stratum.name = ""
		stratum.stratum_hash = ""
		for state in stratum_states:
			stratum.name = stratum.name + " " + state.name
			stratum.stratum_hash = stratum.stratum_hash + "." + state.name
			stratum_content = Stratum_content()
			stratum_content.state = state
			stratum_content.chain = state.chain
			stratum_content.stratum = stratum
			db.session.add(stratum_content)
		print "hash:" + stratum.stratum_hash
		# trim first character (space) from name
		stratum.name = stratum.name[1:]
		db.session.add(stratum)
		db.session.commit()


def save(thing):
    if thing == None:
        raise ValueError('Nothing to save')
    else:
        db.session.add(thing)
        db.session.commit()

def make_tp(chain, from_name, to_name, is_dynamic, tp_base, description="Default"):
    from_state=State.query.filter_by(name=from_name,chain=chain).first()
    if from_state == None:
        print "Error - cannot find from state: " + from_name
        sys.exit(0)
    to_state=State.query.filter_by(name=to_name,chain=chain).first()
    if to_state == None:
        print "Error - cannot find to state: " + to_name
        sys.exit(0)
    if description == "Default":
        description = "Monthly transition probability from " + from_name + " to " + to_name
    save(Transition_probability(
        from_state_name=from_state.name,
        to_state_name=to_state.name,
        from_state=from_state,
        to_state=to_state,
        tp_base=tp_base,
        is_dynamic=is_dynamic,
        description=description
    ))

def make_var(name, value, low, high):
    save(Variable(
        name=name,
        value=value,
        low=low,
        high=high
    ))

# Note you cannot make interactions to the death state with this function, because "death" is ambigous, there are many states with this name
def make_intr(in_name, from_name, to_name, adjustment=1.1, description="Default"):

    from_state=State.query.filter_by(name=from_name).all()
    to_state=State.query.filter_by(name=to_name).all()
    in_state=State.query.filter_by(name=in_name).all()
    if len(from_state) > 1 or len(to_state) > 1 or len(in_state) > 1 :
        print "Ambiguity in interaction"
        sys.Exit(0)
    from_state=State.query.filter_by(name=from_name).first()
    if from_state == None:
        print "Error - cannot find from state: " + from_name
        sys.exit(0)
    to_state=State.query.filter_by(name=to_name).first()
    if to_state == None:
        print "Error - cannot find to state: " + to_name
        sys.exit(0)
    in_state=State.query.filter_by(name=in_name).first()
    if in_state == None:
        print "Error - cannot find to state: " + in_name
        sys.exit(0)
    if description == "Default":
        description = "RR/OR of transfering from " + from_name + " to " + to_name + " if in: " + in_name
    affected_chain = from_state.chain
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

def link_tps_to_chains():
    tps = Transition_probability.query.all()
    for tp in tps:
        from_state = tp.from_state
        chain = from_state.chain
        tp.chain = chain
        save(tp)

def visualize_chain(filename, chain, include_initialization):
    # return
    filename = "initialization_diagrams/" + filename
    tps = Transition_probability.query.filter_by(chain=chain).all()
    states = State.query.filter_by(chain=chain).all()
    G=pgv.AGraph(directed=True,  ratio="compress", size="30,40")
    for state in states:
        G.add_node(state.name, shape="box", fontname="ArialMT", fontsize="40",  width="5", height="2")
    for tp in tps:
        if tp.is_dynamic:
            G.add_edge(tp.from_state.name, tp.to_state.name, fontname="ArialMT", fontsize="40", arrowsize="3") # adds edge 'b'-'c' (and also nodes 'b', 'c')
            #label="Dynamic"
        else:
            if tp.from_state.name == "Uninitialized" and include_initialization:
                G.add_edge(tp.from_state.name, tp.to_state.name, fontname="ArialMT", fontsize="40", color="grey", arrowsize="3") # adds edge 'b'-'c' (and also nodes 'b', 'c')
            elif tp.from_state.name != "Uninitialized":
                G.add_edge(tp.from_state.name, tp.to_state.name, fontname="ArialMT", fontsize="40", arrowsize="3") # adds edge 'b'-'c' (and also nodes 'b', 'c')

                #label=tp.tp_base
    G.layout(prog='dot')
    G.draw(filename)



def visualize_chain2(filename, chain, include_initialization):
    # return
    filename = "initialization_diagrams/" + filename
    tps = Transition_probability.query.filter_by(chain=chain).all()
    states = State.query.filter_by(chain=chain).all()
    G=pgv.AGraph(directed=True, splines="ortho", overlap="false", ratio="compress", size="30,40") #,  #overlap="false",  sep="4", splines="true", size="40,40"
    for state in states:
        G.add_node(state.name, shape="box", fontname="ArialMT")
    for tp in tps:
        if tp.is_dynamic:
            G.add_edge(tp.from_state.name, tp.to_state.name, fontname="ArialMT", len="4") # adds edge 'b'-'c' (and also nodes 'b', 'c')
            #label="Dynamic"
        else:
            if tp.from_state.name == "Uninitialized" and include_initialization:
                G.add_edge(tp.from_state.name, tp.to_state.name, fontname="ArialMT", color="grey", len="4") # adds edge 'b'-'c' (and also nodes 'b', 'c')
            elif tp.from_state.name != "Uninitialized":
                G.add_edge(tp.from_state.name, tp.to_state.name, fontname="ArialMT", len="4") # adds edge 'b'-'c' (and also nodes 'b', 'c')

                #label=tp.tp_base
    G.layout(prog='neato')
    G.draw(filename)



def visualize_all_interactions(): 
    return
    G=pgv.AGraph(directed=True, rankdir="LR", overlap="scale")
    interactions = Interaction.query.all()
    for interaction in interactions:
        tp_name = interaction.from_state.name + " => " + interaction.to_state.name
        G.add_edge(interaction.in_state.name, tp_name, label=interaction.adjustment, fontname="ArialMT", fontsize="10")
    G.layout(prog='neato')
    G.draw("interactions.png")

def visualize_all_interactions_x(): 
    return
    G=nx.Graph()
    G.add_edge('a','b',weight=0.6)
    G.add_edge('b','c',weight=0.6)
    #interactions = Interaction.query.all()
    #for interaction in interactions:
        #tp_name = interaction.from_state.name + " => " + interaction.to_state.name
        #G.add_edge(interaction.in_state.name, tp_name, label=interaction.adjustment, fontname="ArialMT", fontsize="10")
    G.layout(prog='dot')
    G.draw("interactions.png")

def create_initialization_tps(chain):
    tps_to_save = list()
    states = State.query.filter_by(chain=chain).all()
    from_state=State.query.filter_by(name="Uninitialized",chain=chain).first()
    if from_state == None:
        print "Error - cannot find from state: " + from_name
        sys.exit(0)
    for state in states:
        if state.name != "Uninitialized" and state.name != "Death":  
            to_state=State.query.filter_by(name=state.name,chain=chain).first()
            if to_state == None:
                print "Error - cannot find to state: " + to_state
                sys.exit(0)
            tp = Transition_probability(
                description="Initialization to " + to_state.name,
                from_state=from_state,
                to_state=to_state,
                from_state_name=from_state.name,
                to_state_name=to_state.name,
                tp_base=0.1,
                is_dynamic=False
            )
            tps_to_save.append(tp)
    db.session.add_all(tps_to_save)
    db.session.commit()

    
# ---------------- Admin -------------------------
# This section adds models to the admin panel, which
# allows use to view them using the superadmin package

from flask.ext.superadmin import Admin, model

# Create admin
admin = Admin(app, 'Simple Models')

# Add views
admin.register(Chain, session=db.session)
admin.register(State, session=db.session)
admin.register(Raw_input, session=db.session)
admin.register(Reference, session=db.session)
admin.register(Transition_probability, session=db.session)
admin.register(Interaction, session=db.session)
admin.register(Cycle, session=db.session)
admin.register(Disability_weight, session=db.session)
admin.register(Cost, session=db.session)
admin.register(Intervention, session=db.session)
admin.register(Stratum, session=db.session)
admin.register(Stratum_content, session=db.session)
admin.register(Stratum_type, session=db.session)
admin.register(Stratum_type_content, session=db.session)
admin.register(Transition_probability_by_stratum, session=db.session)
admin.register(Variable_by_stratum, session=db.session)
admin.register(Variable, session=db.session)
admin.register(Synchronization, session=db.session)
admin.register(BaseInitLine, session=db.session)


# ---------------- Manager -------------------------
# This allows for access into a flask-specific shell
# It is not used much

from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


def make_shell_context():
	return dict(app=app, db=db, Interaction=Interaction, State=State, Chain=Chain, DisabilityWeight=Disability_weight, Cost=Cost)


manager.add_command("shell", Shell(make_context=make_shell_context))



if __name__ == '__main__': 
	manager.run()

# if __name__ == '__main__':
# 	app.run(host='0.0.0.0')



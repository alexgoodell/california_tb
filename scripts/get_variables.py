
# LIMCAT Outputs

from IPython.display import Image
# For later visualizaton scripts
import pygraphviz as pgv
import time
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython import embed
import math

#connect to application
from app import * 




f = open('go/variables_template.txt','r')
gocode_template = f.read()
f.close() # you can omit in most cases as the destructor will call it

gocode1 = ""
gocode2 = ""

var_df = pd.read_excel("raw-data-files/main_inputs.xlsx", sheetname="Variables")

for i, row in var_df.iterrows():

	c_value = row['Value']

	if c_value == None:
		print "Empty line"
	elif c_value == "Calculated":
		print "Dynamic transition - calculated - skipping"	
	elif math.isnan(float(c_value)):
		print "Not a number"
	else:

		name = row['Name']
		# capitalize 
		c_var = row['Name'].title()
		# remove spaces
		c_var = re.sub('[^A-Za-z0-9]+', '', c_var)
		

		variable = Variable.query.filter_by(name=name).first()
		if variable == None:
			print "Cannot find " + name + " !!!!!!!!!! "
		else:
			variable.value = c_value
			variable.low = row["Low"]
			variable.high = row["High"]
			save(variable)

			print c_var, c_value
			gocode1 += 'var {0}  Variable\n'.format(
				c_var
			) 

			gocode2 += '\tdb.Where("name = ?", "{0}").First(&{1})\n'.format(
				name,
				c_var
			)             

gocode_into_file = re.sub(r'\s{{gocode1}}\s', gocode1, gocode_template)
gocode_into_file = re.sub(r'\s{{gocode2}}\s', gocode2, gocode_into_file)




f = open("go/variables.go", 'w+')
f.write(gocode_into_file)
f.close()


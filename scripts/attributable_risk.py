import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt, mpld3
import matplotlib.patches as mpatches
import seaborn as sns
from IPython import embed

plt.clf()
plt.figure(figsize=(7, 5))

piv = pd.read_csv("piv.csv")
piv = piv.rename(columns={'Remaining': 'No identifiable risk factor'})

piv = piv.T

piv.columns = piv.iloc[0]
piv = piv.drop('Year', 0)
piv = piv.drop('Total', 0)
piv = piv.sort(2001)

cols =['Transplant',
 'TNF-alpha',
 'ESRD',
 'HIV',
 'Diabetes',
 'Imported',
 'Recent transmission',
 'Smokers',
 'No identifiable risk factor']


cols.reverse()

x = range(2001,2015)
y = piv.loc[cols].values.tolist()

colors = ["#9a4b51",
"#76b447",
"#8a48c6",
"#827b3d",
"#c85196",
"#55a694",
"#d46a3b",
"#7071ac"]




plt.stackplot(x, y, label=piv.index, colors=colors)

plt.xlim(2001,2014)
plt.ylim(0,3500)

plt.ylabel("Annual active cases")
plt.xlabel("Year")

# creating the legend manually
plt.legend([mpatches.Patch(color=colors[0]),  
            mpatches.Patch(color=colors[1]),  
            mpatches.Patch(color=colors[2]),  
            mpatches.Patch(color=colors[3]),  
            mpatches.Patch(color=colors[4]),  
            mpatches.Patch(color=colors[5]),  
            mpatches.Patch(color=colors[6]),  
            mpatches.Patch(color=colors[7])], 
           cols,ncol=2)

plt.savefig("tmp.png", bbox_inches='tight', dpi=300)



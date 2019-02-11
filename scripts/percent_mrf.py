import pandas as pd

rvct_df = pd.read_excel("raw-data-files/rvct_calib_data.xlsx", sheetname="Final")
rvct_df = rvct_df[rvct_df.Year == 2014]
total = rvct_df[rvct_df.Group == "Total"].CasesAverage.sum()

# Diabetes
# Smoking
# HIV
# TNF-alpha
# Solid-organ transplants
# ESRD


groups = [ "Diabetes" , "Smokers", 'HIV', 'TNF-alpha', 'Transplant', 'ESRD']

for group in groups:
	cases_percent = rvct_df[rvct_df.Group == group].CasesAverage.sum() / total * 100.0
	cases_percent = "{}".format(float('%.2g' % cases_percent))
	print group + "	" + cases_percent

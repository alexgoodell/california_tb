
years = range(2001,2200)
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

i = 1

print '''- Cycle 0: 
  id: 0
  name: Initialization
  year: 2000'''

for year in years:
	for month in months:
		text = '''- Cycle {0}: 
  id: {0}
  name: {1} {2}
  year: {2}'''
		text = text.format(i, month, year)
		print text
		i = i + 1



# limcat

Limcat is a project using Locally-interacting Markov models for TB control in California.

This project was originally started as a model for South Africa. That repo can be found here: https://github.com/alexgoodell/limsa

There are a few core components:

* A data model is defined by SQLAlchemy in the Flask app ```app.py```
* Data is stored in an SQLite database found in the ```database``` directory.
* Data preparation and analysis is written as python file in ```limcat.py```. ────  _This will serve as the primary document for the project__
* One of the core principles of this project is that of reproducibility. No changes to the database should be made directly. Instead, this data should be stored by modifying ```limcat.md```. ```limcat.md``` destroys the database as its first command and rebuilds it from ground up.
* The model itself is run in Go
* There are many required packages for python and Go. Please see the dockerfile for the specific requirements.

Here are all the files and their purposes (as of Dec 29 2015).

```
├── Makefile  ────  Make is a program that simplifies a few processes
├── README.md ────  You are here
├── app.py ────  This has all of the database definitions
├── database ────  This folder holds the database file(s)
│   └── limcat-zero-index.sqlite ────  This is the core database file. It is zero-indexed
├── docker
│   └── Dockerfile ────  This is a dockerfile. Create a VM that can run the program
├── get_variables.py ────  The moves variables from main_inputs.xls to database
├── go 
│   ├── cli.go ────  Sets up command-line interface
│   ├── getters-and-setters.go ────  These get and set
│   ├── globals.go ────  All global variables
│   ├── index.go ────  This has most of the functionality
│   ├── io.go ────  This is input and output
│   ├── scenarios ────  This folder holds different scenarios used to simulate
│   │   ├── basecase-config.yaml ────  This is an example of the basecase simulation
│   │   └── qft-fb-med-risk-config.yaml ────  This is an example of an intervention
│   ├── tmp ────  This folder holds all of the outputs
│   │   ├── cycle
│   │   ├── cycle_state ────  The primary CSV outputs live here
│   │   ├── events
│   │   ├── eventsPSA
│   │   ├── master
│   │   ├── model_calib_results.json
│   │   ├── other
│   │   └── otherPSA
│   ├── types.go ────  This defines the different object types
│   ├── variable_calculations.go 
│   ├── variables.go
│   └── variables_template.txt
├── import_from_csv.py ────  This transfers data from the XLSs to the database
├── ipums.py ────  This populates the database with demographic data
├── latent_tb.py ────  This populates part of the database with prevalence estimates for LTBI
├── limcat.py ────  This builds the database, calls on ipums, import, stratify, etc 
├── make_zero_index_db.py ────  This converts the 1-indexed database that limcat.py creates to zero-indexed, which is what go needs
├── output_html ────  This folder holds all of the HTML output
├── outputs2.py ────  This is the primary visualizaition script
├── outputs_ttt.py ────  This script runs the TTT analysis
├── raw-data-files ────  This folder holds all the raw data sources
│   ├── active_CDPH.csv
│   ├── active_tb_prevalence.csv
│   ├── calib_cycles.yaml
│   ├── cdph_data.csv
│   ├── chis_raw.csv
│   ├── initialization_data.xlsx
│   ├── latent_tb_raw.csv
│   ├── main_inputs.xlsx
│   ├── raw_all_years_ipums_small.tar.gz
│   ├── risk_of_death.csv
│   ├── rvct.yaml
│   ├── rvct_calib_data.csv
│   ├── tb.csv
│   └── ~$main_inputs.xlsx
├── set_variables.py ────  This just populates the database with variables
├── stratify.py ────  This builds the stratification system where needed
├── tmp ────  Temp folder
└── ttt-results ────  This holds the ttt results
```
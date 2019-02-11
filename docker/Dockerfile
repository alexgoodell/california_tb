##############################################################################################
##############################################################################################
##############################################################################################
######################################   LIMCAT Dockerfile  ##################################
##############################################################################################
##############################################################################################
#          
#
#        
#      How do you use this Dockerfile?
#      
#      1. Make sure you have correctly installed docker and can access the "docker" command. 
#         If not, please follow the instructions: https://www.docker.com/
#      
#      2. Place this file in a folder. Name it "Dockerfile", no extension. Capital D.
#      
#      3. Create another folder within the same folder called "outputs". The command should
#         be "mkdir outputs"
#      
#      4. Build this dockerfile into an image. This should take ~1h to complete. Run the 
#         command "docker build -t limcat_base ."  Make sure the period is in there, and 
#         you are in the same folder as this dockerfile.
#      
#      5. That will build the image. You should see a line for limcat_base if you type
#         "docker images"
#      
#      6. Next, you need to start a virtual machine (called a "container" in docker 
#         language). This is done by running 
#         "docker run -it -v ${PWD}/outputs:/home/limcat/output_html limcat_base" 
#         This command creates a new virtual machine and links the
#         "/home/limcat/output_html" directory to the "outputs" directory you just 
#         created.
#      
#      7. You should notice that your command prompt has changed. This means you 
#         are in the virtual machine. You can now access the model.
#
#      8. Next, go to the limcat directory: "cd /home/limcat"
#
#      9. Then, run the go model with the following command:
#      go run go/*.go --run_type single --size s --cycles 12 --name basecase --runs 1
#      
#      10. Then, create a folder:
#      mkdir /home/limcat/output_html/output_figures
#
#	   11. Then run the output script:
#      python outputs2.py --images y --name basecase --size s --comment "basecase2 single run"
#
#      11. Your results should be in the "output" folder you created!
#      
#      




# Start with basic ubuntu image
FROM ubuntu:14.04

MAINTAINER Alex Goodell <alexgoodell@gmail.com>

# Install basics
RUN apt-get -y update
RUN apt-get install -y git make wget curl bison vim

# Graphviz dependencies
RUN apt-get -y install graphviz libgraphviz-dev

# Install python dependencies
RUN apt-get -y install build-essential checkinstall
RUN apt-get -y install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

# sci py dependencies
RUN apt-get -y install libblas-dev liblapack-dev libatlas-base-dev gfortran

# Download python source
RUN mkdir ~/Downloads/
RUN cd ~/Downloads/ && wget http://python.org/ftp/python/2.7.10/Python-2.7.10.tgz

# Extract and install python
RUN cd ~/Downloads/ && tar -xvf Python-2.7.10.tgz
RUN cd ~/Downloads/Python-2.7.10 && ./configure
RUN cd ~/Downloads/Python-2.7.10 && make
RUN cd ~/Downloads/Python-2.7.10 && make install

# Get pip (python package manager)
RUN cd ~/Downloads && wget https://bootstrap.pypa.io/get-pip.py
RUN cd ~/Downloads && python get-pip.py
RUN pip install --upgrade pip

# Install dependencies (these can be run all at once but was easier to break them up)
RUN pip install alembic==0.8.4
RUN pip install decorator==4.0.6
RUN pip install Flask==0.10.1
RUN pip install Flask-Migrate==1.4.0
RUN pip install Flask-Script==2.0.5
RUN pip install Flask-SQLAlchemy==2.0
RUN pip install Flask-SuperAdmin==1.7.1
RUN pip install Flask-WTF==0.12
RUN pip install funcsigs==0.4
RUN pip install ipython==4.0.0
RUN pip install ipython-genutils==0.1.0
RUN pip install itsdangerous==0.24
RUN pip install Jinja2==2.8
RUN pip install Mako==1.0.3
RUN pip install MarkupSafe==0.23
RUN pip install matplotlib==1.4.3
RUN pip install mock==1.3.0
RUN pip install mpld3==0.2
RUN pip install nose==1.3.7
RUN pip install numpy==1.10.2
RUN pip install pandas==0.16.2
RUN pip install path.py==8.1.2
RUN pip install pbr==1.8.1
RUN pip install pexpect==4.0.1
RUN pip install pickleshare==0.5
RUN pip install ptyprocess==0.5
RUN pip install pygraphviz==1.2
RUN pip install pyparsing==2.0.6
RUN pip install python-dateutil==2.4.2
RUN pip install python-editor==0.5
RUN pip install pytz==2015.7
RUN pip install PyYAML==3.11
RUN pip install scikits.bootstrap==0.3.2
RUN pip install scipy==0.16.1
RUN pip install seaborn==0.6.0
RUN pip install simplegeneric==0.8.1
RUN pip install six==1.10.0
RUN pip install SQLAlchemy==1.0.11
RUN pip install tabulate==0.7.5
RUN pip install traitlets==4.0.0
RUN pip install Werkzeug==0.11.3
RUN pip install WTForms==2.1
RUN pip install xlrd==0.9.4

# Install limcat source code from GitHub
# There are two ways to do this: pull the current repo (which might have errors)
# Or the specific commit (dfd9...) from when I tested this (Dec 29)

# RUN cd /home && git clone --depth  1  https://github.com/alexgoodell/limcat.git
RUN cd /home && git clone https://github.com/alexgoodell/limcat.git
RUN cd /home/limcat && git reset --hard 6b6ee126a3f657f8fd1d27e09f970a5ce29e85a3

# Decompress the input data from IPUMS (uncompressed it is ~400 mb)
RUN cd /home/limcat && tar -xvzf raw-data-files/raw_all_years_ipums_small.tar.gz -C raw-data-files/

# Build database
RUN cd /home/limcat && python limcat.py
RUN cd /home/limcat && python make_zero_index_db.py

# Install Go (1.4.2 needed)
RUN curl -O https://storage.googleapis.com/golang/go1.6.2.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.6.2.linux-amd64.tar.gz
ENV PATH $PATH:/usr/local/go/bin

# Set path for go dependencies
RUN mkdir /home/go
ENV GOPATH /home/go

# Get Go dependencies
RUN sudo go get "github.com/cheggaaa/pb"
RUN sudo go get "github.com/codegangsta/cli"
RUN sudo go get "github.com/fatih/structs"
RUN sudo go get "github.com/jinzhu/gorm"
RUN sudo go get "github.com/mattn/go-sqlite3"
RUN sudo go get "gopkg.in/yaml.v2"
RUN sudo go get "github.com/agoussia/godes"

# Set environment variable
ENV LIMCATENV laptop

# Create file structure for Go's outputs
RUN mkdir /home/limcat/go/tmp
RUN mkdir /home/limcat/go/tmp/cycle_state
RUN mkdir /home/limcat/go/tmp/cycle


VOLUME mkdir /home/limcat/output_html
RUN mkdir /home/limcat/output_html/output_figures



# # Run the model for a small population for 12 cycles
# RUN cd /home/limcat && go run go/*.go --run_type single --size s --cycles 12 --name basecase --runs 1

# # Format outputs - The final file should be found in "output_html"
# RUN cd /home/limcat && python outputs2.py --images y --name basecase --size s --comment "basecase2 single run"

# VOLUME /outputs

# RUN 

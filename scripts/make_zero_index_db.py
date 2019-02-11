
from app import *

import os

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database/limcat-zero-index.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


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
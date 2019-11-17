"""
This program takes the data frames of each table and enters them into the SQL database.

"""
import pandas as pd
from sqlalchemy import create_engine
import app_extract_18 as extract
import os
import numpy as np

directory = 'applications/eapp_2018/'

### convert all applications to data frames
file_list = os.listdir(directory)

db_tbls = extract.create_dataframe(directory, file_list[:5])

### convert the hour working per week to integer and strip non-numbers
### can't figure out how to do this within a function or loop

# columns to convert
convert_cols = [db_tbls[0]['fullTime_job'], db_tbls[1][2]['hours_week'], db_tbls[1][3]['hours_week']]

## first column

# if length is greater than 4 extract first two digits, otherwise extract first digit
db_tbls[1][2]['hours_week'] = np.where(db_tbls[1][2]['hours_week'].str.len() > 4, 
                                       db_tbls[1][2]['hours_week'].str[:2],
                                       db_tbls[1][2]['hours_week'].str[0])
        
# convert 'no answer provided' which is 'no' after the previous conversion, to nan
db_tbls[1][2]['hours_week'] = np.where(db_tbls[1][2]['hours_week'] == 'no', np.nan, db_tbls[1][2]['hours_week'])
    
# convert np array to pd series
db_tbls[1][2]['hours_week'] = pd.Series(db_tbls[1][2]['hours_week'])
    
# only keep numbers; fill NA with 0; convert to integer
db_tbls[1][2]['hours_week'] = db_tbls[1][2]['hours_week'] \
        .str.extract('([0-9]+)') \
        .fillna(0) \
        .astype(int)
        
## second column

# if length is greater than 4 extract first two digits, otherwise extract first digit
db_tbls[0]['fullTime_job'] = np.where(db_tbls[0]['fullTime_job'].str.len() > 4, 
                                      db_tbls[0]['fullTime_job'].str[:2],
                                      db_tbls[0]['fullTime_job'].str[0])
        
# convert 'no answer provided' which is 'no' after the previous conversion, to nan
db_tbls[0]['fullTime_job'] = np.where(db_tbls[0]['fullTime_job'] == 'no', np.nan, db_tbls[0]['fullTime_job'])
    
# convert np array to pd series
db_tbls[0]['fullTime_job'] = pd.Series(db_tbls[0]['fullTime_job'])
    
# only keep numbers; fill NA with 0; convert to integer
db_tbls[0]['fullTime_job'] = db_tbls[0]['fullTime_job'] \
        .str.extract('([0-9]+)') \
        .fillna(0) \
        .astype(int)
        
## third column
        
# if length is greater than 4 extract first two digits, otherwise extract first digit
db_tbls[1][3]['hours_week'] = np.where(db_tbls[1][3]['hours_week'].str.len() > 4, 
                                       db_tbls[1][3]['hours_week'].str[:2],
                                       db_tbls[1][3]['hours_week'].str[0])
        
# convert 'no answer provided' which is 'no' after the previous conversion, to nan
db_tbls[1][3]['hours_week'] = np.where(db_tbls[1][3]['hours_week'] == 'no', np.nan, db_tbls[1][3]['hours_week'])
    
# convert np array to pd series
db_tbls[1][3]['hours_week'] = pd.Series(db_tbls[1][3]['hours_week'])
    
# only keep numbers; fill NA with 0; convert to integer
db_tbls[1][3]['hours_week'] = db_tbls[1][3]['hours_week'] \
        .str.extract('([0-9]+)') \
        .fillna(0) \
        .astype(int)

### create tables to insert into database

demographic_vars = ['LSAC', 'birthDate', 'birthPlace', 'race', 'latino', 'gender', 'military',
                    'fullTime_job', 'citizenship', 'countryCitizen']
demographic_a = db_tbls[0].loc[:, demographic_vars]

app_status_a = db_tbls[0].loc[:, ['LSAC', 'date', 'applyingAs', 'decisionCycle']]

parent_vars = ['LSAC', 'parent1_Occupation', 'parent1_Education', 'parent2_Occupation', 'parent2_Education']
parents_a = db_tbls[0].loc[:, parent_vars]

# create list of tables
to_db = [demographic_a, app_status_a, parents_a,
         db_tbls[2], # character and fitness
         db_tbls[1][0], # lsat
         db_tbls[1][1], # education
         db_tbls[1][2], # employment
         db_tbls[1][3] # extracurricular
         ]

files = db_tbls[3]

del db_tbls

# create list of table names
tbl_names = ['demographic_a', 'app_status_a', 'parents_a', 'char_fit_a', 
             'lsat_a', 'education_a', 'employment_a', 'extracurricular_a']

# connect to database
engine = create_engine('sqlite:///student_db.db')

# iterate through tables, inserting into database
for tbl, tbl_name in zip(to_db, tbl_names):
    print(tbl_name)
    tbl.to_sql(tbl_name, con=engine, chunksize = 10, if_exists='append', index = False)
"""
This program takes the data frames of each table and enters them into the SQL database.

"""
import pandas as pd
from sqlalchemy import create_engine
import app_extract_18 as extract
import os, shutil
import sys
import numpy as np
import zipfile
import re

def main():
        
        year = re.findall(r'\d{4}', sys.argv[1])
        year = int(year[0])
        output_type = sys.argv[2]
        zip_file = sys.argv[3]

        pdf_dir = 'pdf'

        # unzip the zip file of individual PDF files and place in folder
        unzip_files(pdf_dir, zip_file)

        # convert all applications to data frames
        file_list = os.listdir(pdf_dir)

        db_tbls = extract.create_dataframe(pdf_dir + '/', file_list[:3], year)

        # clean up hours work week columns
        db_tbls = convert_cols(db_tbls)

        # create tables to place in dataframe
        to_db = create_db_tables(db_tbls)

        del db_tbls

        # output to either csv files or sqlite database
        output_csv_sql(to_db, output_type)

        # delete the unzipped pdf applications
        shutil.rmtree(pdf_dir)

# output to csv file or sqlite database
def output_csv_sql(to_db, output_type):

        # create list of table names
        tbl_names = ['demographic_a', 'app_status_a', 'parents_a', 'char_fit_a', 
                'lsat_a', 'education_a', 'employment_a', 'extracurricular_a']

        # connect to database
        engine = create_engine('sqlite:///student_db.db')

        # iterate through tables, inserting into database or exporting csv files
        if output_type == '--csv':
                # make new directory to store csv files
                os.mkdir('eapp')
                # iterate through each table, writing out file
                for tbl, tbl_name in zip(to_db, tbl_names):
                      tbl.to_csv('eapp/' + tbl_name + 'csv', index = False)  
                        
        elif output_type == '--sql': 
                # connect to database
                engine = create_engine('sqlite:///student_db.db')

                for tbl, tbl_name in zip(to_db, tbl_names):
                        # write out each table to database     
                        tbl.to_sql(tbl_name, con=engine, chunksize = 1000, if_exists='append', index = False)

    
def unzip_files(pdf_dir, zip_file):

        os.mkdir(pdf_dir)

        with zipfile.ZipFile(zip_file,"r") as zip_ref:
                zip_ref.extractall(pdf_dir)

### convert the hour working per week to integer and strip non-numbers
### can't figure out how to do this within a function or loop
def convert_cols(db_tbls):
        # columns to convert
        #convert_cols = [db_tbls[0]['fullTime_job'], db_tbls[1][2]['hours_week'], db_tbls[1][3]['hours_week']]

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

        return db_tbls

### create tables to insert into database
def create_db_tables(db_tbls):

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
        
        return to_db

if __name__ == '__main__':
   main()
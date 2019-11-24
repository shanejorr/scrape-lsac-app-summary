"""
This program takes the Eapp file as input, calls app_to_dict_18 to convert the file
to a dictionary, then converts the dictionary to a dataframe

"""

import re
import pandas as pd
import numpy as np
import textExtract as extract


def hours_worked(dataframe_column):
    '''
    many hours worked variables either contain a repeat of the number or 'no answer provided'
    create function that convert 'no answer' to null and extracts first two digits
    convert to float
    
    Remove excess repeat of numbers
    '''
    # if length is greater than 4 extract first two digits, otherwise extract first digit
    dataframe_column = np.where(dataframe_column.str.len() > 4, 
                                                dataframe_column.str[:2],
                                                dataframe_column.str[0])
        
    # convert 'no answer provided' which is 'no' after the previous conversion, to nan
    dataframe_column = np.where(dataframe_column == 'no', np.nan, dataframe_column)
    
    # convert np array to pd series
    dataframe_column = pd.Series(dataframe_column)
    
    # only keep numbers; fill NA with 0; convert to integer
    dataframe_column = dataframe_column \
        .str.extract('([0-9]+)') \
        .fillna(0) \
        .astype(int)

    return dataframe_column

def app_to_dict_18(filename, year):
    
    """
    This function extracts information from the long-form application information 
    for the entering class of 2018.
    
    Date created: August 3, 2018
    """
    
    #extract application summary
    summary = extract.deleteDuplicateLines(filename)
    
    # save output of summary to text file for printing
    #with open("eapp_output_nopage.txt", "w") as text_file:
    #    print(f"{summary}", file=text_file)
    
    #remove page number text

    summary = re.sub(r'\nPage [0-9]+\n.*\nL[0-9]+\nElon.*\nFall.*\n', '\n', summary)
    summary = re.sub(r'\nPage [0-9]+\n', '\n', summary)
    
    #create blank dictionary to store application items
    summaryValues = {}
    summaryValues['fullName'] = re.search(r"Applicant Name: (\w+, \w+)", summary).group(1)
    summaryValues['LSAC'] = re.search(r"LSAC Account Number: ([A-Z0-9]+)", summary).group(1)
    
    # remove header information that is on all pages
    # must remove after extracting name and lsat, because these might be removed
    header = re.compile(r"\nElon University School of Law\n"
                        "Fall " + str(year) + " - Application\n"
                        ".*?\n"
                        "L.*?\n")
    summary = re.sub(header, '\n', summary)
    
    school_header = re.compile(r"\nElon University School of Law\n"
                               "Fall " + str(year) + " - Application\n")
    summary = re.sub(school_header, '\n', summary)
    
    summaryValues['date'] = re.search(r"Transmission Date and Time: (\d+/\d+/\d+)", summary).group(1)
    summaryValues['applyingAs'] = re.search(r"1. I am applying for admission as a:\n(.*?)\n", summary).group(1)
    summaryValues['decisionCycle'] = re.search(r"\n(.*)\n3. Biographical\n", summary).group(1)
    summaryValues['birthDate'] = re.search(r"Date of birth\n(.*)\n", summary).group(1)
    summaryValues['birthPlace'] = re.search(r"Place of birth: City/State/Country\n(.*)\n", summary).group(1)
    summaryValues['gender'] = re.search(r"Gender\n(.*)\n", summary).group(1)
    summaryValues['citizenship'] = re.search(r"\nCitizenship\n(.*)\n", summary).group(1)
    summaryValues['countryCitizen'] = re.search(r"Country of citizenship\n(.*)\n", summary).group(1)
    summaryValues['latino'] = re.search(r"\nAre you Hispanic\/Latino\?\n(.*)\n", summary).group(1)
    #only returns first race value
    summaryValues['race'] = re.search(r"\nWhat is your race\?.*\n(.*?)[,\n]", summary).group(1)
    summaryValues['legacy'] = re.search("\n2. If you have any close relatives.*\n(.*)\n", summary).group(1)
    
    #use one RE to pull both parent's occupation and income
    parentOccupation = re.findall(r"\nOccupation\n(.*)\n", summary)
    parentEducation = re.findall(r"\nHighest Education Level\n(.*)\n", summary)
    parent = ["parent1_", "parent2_"]
    for occ, ed, par in zip(parentOccupation, parentEducation, parent):
        summaryValues[par+"Occupation"] = occ
        summaryValues[par+"Education"] = ed
    
    ##don't know how many lsat scores there are, so must create flexibility in RE
        
    # initialize list that will store a different dictionary for eacy lsat
    lsat_list = []
    
    #extract all text (dates and scores of all LSATs) under LSAT question
    lsatRE = re.compile(r"take the LSAT\n(.*?)\nTOEFL\n", re.DOTALL)
    wholeLsat = re.search(lsatRE, summary).group(1)
    
    #extract LSAT scores and dates, multiple come in single list
    lsat_scores = re.findall("\n(\d\d\d)\d\d+", wholeLsat)
    lsat_dates = re.findall("(\d\d/\d\d\d\d)\n", wholeLsat)
    
    # convert scores and dates into dictionary, and add to list of dictionaries of lsat scores]
    for score, date in zip(lsat_scores, lsat_dates):
        lsat_dict = {}
        lsat_dict['lsat_score'] = score
        lsat_dict['lsat_date'] = date
        lsat_list.append(lsat_dict)
    
    # add list of lsat scores to main dictionary
    summaryValues['lsat'] = lsat_list
        
    # education: multiple entries
    #regular expression to extract all education
    educationRE = re.compile(r"\n(.*?)\n" #school name
                             "Education type\n(.*?)\n"
                             "Location\n(.*?)\n"
                             "Attendance Dates\n(.*?)\n"
                             "Degree and Degree Date\n(.*?)\n"
                             "Major\n(.*?)\n"
                             "Other Major\n(.*?\n)"
                             "GPA\n(.*?)\n")
    #create keys for putting education items in dictionary
    edKeys = ['school', 'educationType', 'location', 'dates', 'degree', 'major', 'otherMajor', 'GPA']
    # extract education
    summaryValues['education'] = extract.extract_multi(summary, educationRE, edKeys)
    
    # we will only keep the variable of whether person was in military
    # years prior to 2018 have other variables, but 2018 only has this variable
    # so, for consistency we will only keep this variable
    summaryValues['military'] = re.search(r"1. Have you.*fulltime, active military duty.\n(.*)\n", summary).group(1)

    # employment: multiple entries
    #regular expression to extract all employment
    employmentRE = re.compile(r"\n(.*?)\n" #employer name
                             "Employment type\n(.*?)\n"
                             "Location\n(.*?)\n"
                             "Employment Dates\n(.*?)\n"
                             "Position\n(.*?)\n"
                             "Hours per week\n(.*?)\n"
                             "Reason for leaving\n.*?\n" # don't record this field
                             "This employment was during the academic year\n(.*?\n)")
    
    #create keys for putting employment items in dictionary
    empKeys = ['name', 'employmentType', 'location', 'dates', 'position', 'hours_week', 'during_school']
    # extract employment
    summaryValues['employment'] = extract.extract_multi(summary, employmentRE, empKeys)
    
    # full-time job experience
    full_time_job = re.compile(r"2. Full-time job experience\n"
                             "Total number of months\n"
                             "(.*?)\n")
    try:
        # enter full time hours if applicable
        summaryValues['fullTime_job'] = re.search(full_time_job, summary).group(1)
    except:
        # if not applicable, enter 0
        summaryValues['fullTime_job'] = 0
    
    #extracurricular: multiple entries
    #regular expression to extract all extracurricular
    extraRE = re.compile(r"\nName/Organization\n(.*?)\n"
                             "Position Held\n(.*?)\n"
                             "Dates\n(.*?)\n"
                             "Description\n(.*?)\n"
                             "Hours/Week\n(.*?)\n")
    #create keys for putting extracurricular items in dictionary
    extraKeys = ['name', 'position', 'dates', 'description', 'hours_week']
    # extract extracurricular
    summaryValues['extracurricular'] = extract.extract_multi(summary, extraRE, extraKeys)
    
    # character and fitness
    # create own dictionary for character and fitness, and add dictionary to main
    # a seperate dictionary is used because this information may not be needed and
    # will be its own table in database
    
    # create one RE to extract all character and fitness answers
    char_fit_re = re.compile(r"\n(.*?)\n"
                              "2. Are there any academic[\s\S]*\n(.*?)\n"
                              "3. Have you ever been reprimanded[\s\S]*\n(.*?)\n"
                              "4. Have you ever been suspended[\s\S]*\n(.*?)\n"
                              "5. Have you ever received a citation[\s\S]*\n(.*?)\n"
                              "6. Have you ever been convicted[\s\S]*\n(.*?)\n"
                              "7. Are there any criminal charges pending[\s\S]*\n(.*?)\n"
                              "8. Have you ever been requested[\s\S]*\n(.*?)\n"
                              "9. Have you ever been disciplined[\s\S]*\n(.*?)\n"
                              "10. Have you ever been dismissed[\s\S]*\n(.*?)\n"
                              "11. Has a judgment been entered[\s\S]*\n(.*?)\n"
                              "14. Early Decision Agreement")
    
    # dictionary key names for character and fitness entries
    char_fit_names = ['academic_probation', 'academic_infractions', 'academic_discipline',
                      'academic_suspension', 'criminal_charge', 'criminal_conviction',
                      'criminal_pending', 'criminal_appearance', 'employee_discipline', 
                      'employee_dismissal', 'civil_judgement']
    
    # initialize dictionary
    char_fit = {}
    
    # add values to dictionary
    for i, key_name in zip(range(1,len(char_fit_names)+1), char_fit_names):
        char_fit[key_name] = re.search(char_fit_re, summary).group(i)
        
    #add character and fitness dictionary to main dictionary
    summaryValues['char_fit'] = char_fit
    
    return summaryValues


def create_dataframe(directory, file_list, year):
    
    '''
    This function converts the dictionary of application information that was
    produced by app_to_dict_18 and converts it to data frames
    '''
       
    # initialize dataframe that will act as tables
    large_df = pd.DataFrame()
    char_fit_large = pd.DataFrame()
    # initialize list that will contain data frames for tables that might have more than
    # one entry per student
    multi_tables = [pd.DataFrame(),
                    pd.DataFrame(),
                    pd.DataFrame(),
                    pd.DataFrame()]    
    
    # create sets of key names of keys that contain multiple entries per student
    multi_entries = {"char_fit", "education", "employment", "extracurricular", "lsat"}
    multi_no_cf = {"education", "employment", "extracurricular", "lsat"}
    
    # iterate through each file, extract application information and store in list
    # where ech element of the list is a single dictionary for a student
    for file in file_list:

        try:
            app_dict = app_to_dict_18(directory + file, year)
            lsac_num = app_dict['LSAC']
        except:
            with open("error_log.txt", "a+") as text_file:
                print(f"{file}; Year = {year}", file=text_file)      
        # convert dictionaries of individual students to tables for the database
        # don't clean data (such as names) yet, wait until entire data frame is constructed
        # so cleaning can be vectorized
        # all table names end in 'e' so they are distinguished from 'cas'
        
        # return single dataframe with all values except those where there are multiple
        # listings per student
        def without_keys(d, keys):
             return {x: d[x] for x in d if x not in keys}
         
        # convert single entry dictionary items to data frame
        student_df = pd.DataFrame.from_dict(without_keys(app_dict, multi_entries), orient='index').T
        # add single entry items to dataframe holding single entry items
        large_df = large_df.append(student_df)
        
        # create table for character and fitness
        char_fit_single = pd.DataFrame.from_dict(app_dict['char_fit'], orient='index').T
        # add lsac number to character and fitness table
        char_fit_single['lsac_num'] = lsac_num
        # combine with large character and fitness table
        char_fit_large = char_fit_large.append(char_fit_single)
        
        # pull out dictionary keys where there may be multiple values per student
        def with_keys(d, keys):
             return {x: d[x] for x in d if x in keys}
         
        dict_multiple = with_keys(app_dict, multi_no_cf)
        
        table_i = 0
        
        # iterate through dictionary items that represent multiple entries per student
        for key, value in dict_multiple.items():
            # Initialize data frame to store all results for a student on a given item
            large_multi = pd.DataFrame()
            # iterate through individual entries for a given item (lsat score)
            for student in value:
                i = 0
                # create data frame for single entry
                student_multi = pd.DataFrame.from_dict(student, orient='index').T
                student_multi['lsac_num'] = lsac_num
                # append row to table with all entries for student
                large_multi = large_multi.append(student_multi)
                i += 1
            # add data frame of all rows for student to the data frame of that item for all students.
            multi_tables[table_i] = multi_tables[table_i].append(large_multi)
            table_i += 1
    
    # clean data frames by removing repeat words
    
    # character and fitness Yes and no columns repeat the words multiple times; only keep first letter
    char_fit_large.loc[:, char_fit_large.columns != 'lsac_num'] = char_fit_large.loc[:, char_fit_large.columns != 'lsac_num'] \
        .apply(lambda x: x.str[0])
    
    multi_tables[2]['during_school'] = multi_tables[2]['during_school'].str[0]
    
    # College GPA either repeats numbers or has 'no answer provided'
    # extract first sequence of numbers and convert 'no answer ...' to NaN
    multi_tables[1]['GPA'] = multi_tables[1]['GPA'] \
        .str.extract('(^[0-9][.][0-9][0-9])') \
        .astype(float)
    
    # the following three variables repeat words; extract first letter
    large_df[['gender', 'latino', 'military']] = large_df[['gender', 'latino', 'military']] \
        .apply(lambda x: x.str[0])
        
    # the following variables for hours worked have repeating numbers; delete repeats
    #try:
    #    large_df['fullTime_job'] = hours_worked(large_df['fullTime_job'])
    #except:
    #    large_df['fullTime_job'] = 0
    #multi_tables[2]['hours_week'] = hours_worked(multi_tables[2]['hours_week'])
    #multi_tables[3]['hours_week'] = hours_worked(multi_tables[3]['hours_week'])
    
    # convert dates to consistent format
    large_df['date'] = pd.to_datetime(large_df['date'], infer_datetime_format=True).dt.date
    large_df['birthDate'] = pd.to_datetime(large_df['birthDate'], infer_datetime_format=True).dt.date
    multi_tables[0]['lsat_date'] = pd.to_datetime(multi_tables[0]['lsat_date'], infer_datetime_format=True).dt.date
    multi_tables[1][['start_date', 'end_date']] = multi_tables[1]['dates'].str.split(' to ', expand=True)
    multi_tables[1] = multi_tables[1].drop('dates', axis=1)
    multi_tables[2][['start_date', 'end_date']] = multi_tables[2]['dates'].str.split(' to ', expand=True)
    multi_tables[2] = multi_tables[2].drop('dates', axis=1)
    
    # convert full name to first and last
    large_df[['first_name', 'last_name']] = large_df['fullName'].str.split(', ', expand=True)
    large_df = large_df.drop('fullName', axis=1)
    
    # remove 'L' from lsac_num and convert to integer
    large_df['LSAC'] = large_df['LSAC'].str[1:].astype(int)
    char_fit_large['lsac_num'] = char_fit_large['lsac_num'].str[1:].astype(int)
    multi_tables[0]['lsac_num'] = multi_tables[0]['lsac_num'].str[1:].astype(int)
    multi_tables[1]['lsac_num'] = multi_tables[1]['lsac_num'].str[1:].astype(int)
    multi_tables[2]['lsac_num'] = multi_tables[2]['lsac_num'].str[1:].astype(int)
    multi_tables[3]['lsac_num'] = multi_tables[3]['lsac_num'].str[1:].astype(int)

    # return a list of the tables that are needed
    return [large_df, multi_tables, char_fit_large]

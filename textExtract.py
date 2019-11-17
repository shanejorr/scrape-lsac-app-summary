"""
Created on Tue Mar  6 13:35:53 2018

The functions in this file extract text from non-bookmark PDF files.

@author: shane
"""

##################################

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
import re

def extractText(file_name):
    """
    extract text in file
    """
    connection = open(file_name, 'rb')
    parser = PDFParser(connection)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.char_margin = 1.0
    laparams.word_margin = 1.0
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    extracted_text = ''

    for page in doc.get_pages():
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                extracted_text += lt_obj.get_text()
    return extracted_text

###########################################

def deleteDuplicateLines(file_name):
    """
    extract text and seperate lines into a list; and deleted duplicate lines
    to be used primarily with application summary
    """
    #extract text between two bookmarks
    text = extractText(file_name)
    #convert PDF text to list where each line is one entry in list
    listLines = list(iter(text.splitlines()))
    #iterate through each line, delete duplicates, and save originals in a list       
    nonDups = []
    #delete duplicate lines and place lines in list
    for i, line in enumerate(listLines):
        if line == listLines[i-1]:
            continue
        else:
            nonDups.append(line)
    #convert list to string
    nonDups = '\n'.join(nonDups)
    return nonDups

###########################################

def extract_multi(txt, reg_ex, key_list):
    """
    extract values from categories without a set number of entries,
    such as employment, education, and extracurricular activities
    
    Input: 
    text to be searched
    regular expression (from re.compile) for extracting one entry
    list of key values to assign to each entry in dictionary (ex: employer_name, position)
    
    Output: a list of dictionaries where each dictionary in the list is one
    entry of the category (ex: one job)
    """
    #extract all entries in the category matching the re
    category = re.findall(reg_ex, txt)
    # initialize list that will store a different dictionary of of each entry
    catList = []
    # add values to dictionary
    # iterate through each activity, creating a seperate dictionary for each
    for entry in category:
        catResults = {}
        # add keys to values in list
        for keys, values in zip(key_list, entry):
            catResults[keys] = values
        # append dictionary of extracurricular results from one activity onto list
        catList.append(catResults)

    return catList
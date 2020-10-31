# Scrape LSAC Application Summary PDF Files

PDF scrapper of LSAC application summary files. The program can be run from the command line. It has three parameters:

1. Year of the applications (integer)
2. Type of output. Can be either `--csv` for a series of csv files or `--sql` for a SQLite database.
3. Path to file that contains LSAC summary reports for the year.

Example: `python output_eapp.py --2013 --csv 'applications/eapp_2013.zip'`

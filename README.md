# Scrape LSAT Application Summary PDF Files

PDF scrapper of LSAC application summary.

The only file that needs to be ran is `output_eapp.py`.  Users will need to change the path to the application PDF files with the `directory` object on line 11.  After chaning the directory and running the file, application information will be placed into a SQLite database called `student_db.db` in the root directory.

done: 2018, 2017, 2016, 2015, 2014, 2013

To run program: `python output_eapp.py --2013 --csv 'applications/eapp_2013.zip'`

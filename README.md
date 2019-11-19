# Scrape LSAT Application Summary PDF Files

PDF scrapper of LSAC application summary.

The only file that needs to be ran is `output_eapp.py`.  Users will need to change the path to the application PDF files with the `directory` object on line 11.  After chaning the directory and running the file, application informatin will be placed into a SQLite database called `student_db.db` in the root directory.

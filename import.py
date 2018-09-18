import csv

"""In this file, you will find a function that imports all data from a .csv-file to the PostgreSQL
database that is linked to application.py. It is not part of the webapp contained in application.py,
and must be run from the CLI with 'python3 import'."""

# TODO TODO TODO TODO TODO TODO

db.execute("CREATE TABLE books (
    isbn INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
)")

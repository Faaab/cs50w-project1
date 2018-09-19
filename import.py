import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

"""In 'main', you will find a function that imports all data from a .csv-file to the PostgreSQL
database that is linked to with the environment variable "DATABASE_URL".
It is specifically made to import relevant data for the 'books' app (CS50W Project 1),
and must be run from the CLI with 'python3 import'."""

# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

# TODO TODO TODO TODO TODO TODO
# db.execute("CREATE TABLE books (
#     isbn INTEGER PRIMARY KEY,
#     title VARCHAR NOT NULL,
#     author VARCHAR NOT NULL,
#     year INTEGER NOT NULL
# )")

def main():
    with open('books.csv', 'r') as books_csv:
        csv_reader = csv.reader(books_csv)

        for isbn, title, author, year in csv_reader:
            print(f"Added row to table: isbn = {isbn}, title = {title}, author = {author}, year = {year}. JK.")

if __name__ == "__main__":
    main()

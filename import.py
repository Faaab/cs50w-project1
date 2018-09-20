import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

"""In 'main', you will find a function that imports all data from a .csv-file to the PostgreSQL
database that is linked to with the environment variable "DATABASE_URL".
It is specifically made to import relevant data for the 'books' app (CS50W Project 1),
and must be run from the CLI with 'python3 import'."""

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # Create table to import data into
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")

    with open('books.csv', 'r') as books_csv:
        csv_reader = csv.reader(books_csv)

        # Skip first row in csv, since this holds names of columns, not actual data
        next(csv_reader)

        # Print to terminal, just for testing
        for isbn, title, author, year in csv_reader:
            # Insert data in every line into TABLE books
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {'isbn': isbn, 'title': title, 'author': author, 'year': year})
        db.commit()


if __name__ == "__main__":
    main()

import os
import sys

from helpers import hash_password, check_password, login_required

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests
import urllib.parse

app = Flask(__name__)

# key for querying Goodreads API
developer_key = 'eBVKMxIKL8SGityQc5TOg'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure app's secret key for cookie signing
app.secret_key = os.urandom(24)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    # POST-request to this route means the user tries to log in
    if request.method == "POST":

        # Check if all required fields were filled in
        if not request.form.get("username"):
            return render_template("sorry.html", error="Username field not filled in")

        if not request.form.get("password"):
            return render_template("sorry.html", error="Must fill in password")

        # Get data from form
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for user
        userrow = db.execute("SELECT passwordhash FROM users WHERE username = :username",
            {"username": username}).fetchone()

        # If we get no data back here, the user is not in our database=
        if not userrow:
            return render_template("sorry.html", error="We could not find that username. Have you signed up yet?")

        # Get passwordhash from userrow
        for row in userrow:
            userhash = row

        # We found the user. Continue to check if filled-in password was correct
        if not check_password(userhash, password):
            return render_template("sorry.html", error="Password incorrect.")

        # If we get here, we found the user and the password is correct. Continue to log in.
        else:
            session["user"] = username
            return redirect("/loginhome")

    # Branch for GET-request to index page; prompt for login
    else:
        if session.get("user") is None:
            return render_template("welcome.html")

        else:
            return redirect("/loginhome")


#If we get here via GET -> show form. If we get here via POST -> register user.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Let users register"""

    if request.method == "POST":

        #Check if all fields were filled in
        if not request.form.get("username"):
            return render_template("sorry.html", error="Username field not filled in")

        elif not request.form.get("password"):
            return render_template("sorry.html", error="Password field not filled in")

        elif not request.form.get("passwordConfirm"):
            return render_template("sorry.html", error="Password confirmation field not filled in")

        #Get all fields from the form
        username = request.form.get("username")
        password = request.form.get("password")
        passwordConfirm = request.form.get("passwordConfirm")

        ## DEBUG:
        print(username, file=sys.stderr)
        print(password, file=sys.stderr)
        print(passwordConfirm, file=sys.stderr)

        #Check form for correctness
        if not password == passwordConfirm:
            return render_template("sorry.html", error="Passwords did not match")

        # Check whether we have an entry with that username
        userrow = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        if not userrow:
            # If we do not have an entry with that username, store the username and hashed password in the database
            hashedPassword = hash_password(password)
            db.execute("INSERT INTO users (username, passwordhash) VALUES (:username, :hashedPassword)",
                {"username": username, "hashedPassword": hashedPassword})
            db.commit()
            return render_template("registercomplete.html")

        # If a row with that username was found, apologize to user
        else:
            return render_template("sorry.html", error="That username is taken.")

    # GET-method for register: present register form
    else:
        return render_template("register.html")

@app.route("/search", methods=["POST"])
def search():
    #get search query from request
    q = request.form.get("search")
    q = "%" + q + "%"
    print(q)

    # Search database for any entry containing this set of characters
    # NB: Search is case-sensitive now, although this was not my intent. Not yet sure how to fix it.
    result = db.execute("SELECT isbn, title, author, year, id FROM books WHERE isbn LIKE :q OR title LIKE :q OR author LIKE :q OR year LIKE :q",
                {"q": q})

    # The data will be given to the template in a list, where each row is represented by another list
    result_list = []

    # In this loop, result and the rows therein are converted to lists; result_list containing row_lists
    for row in result:
        row_list = []
        for i in range(5):
            row_list.append(row[i])

        result_list.append(row_list)

    # NB: with each SELECT query, a connection to the database remains open, even with the below
    # (connections are closed after several minutes)
    result.close()

    # Give result_list to the Jinja template, which will create a list of search results
    return render_template("search.html", result_list=result_list)

@app.route("/book/<id>", methods=["GET", "POST"])
def book(id):
    """The GET-method for this page will take the id of a book, search for that id in our database and return a page with
    info on the book. Part of that info is an average score on Goodreads. This data is retrieved
    using a query to the Goodreads API. Once implemented, this page will also display a form to
    leave a review, and display all existing reviews for the book.
    The POST-method for this route will submit the user's review, and redirect the user to this same
    route via GET."""

    # TODO
    if request.method == "POST":
        #Submitting user review goes here
        return "TODO"

    # Branch for
    else:
        # Get data about book from database
        result = db.execute("SELECT isbn, title, author, year FROM books WHERE id = :id",
        {"id": id})

        # Store isbn, title, author, year (in that order) in book_data
        for row in result:
            book_data = dict(row)

        # add book id to book_data
        book_data['id'] = id

        # Build a URL to query Goodreads API (book.review_counts function), using ISBN and the globally
        # defined developer key as parameters
        base_url = "https://www.goodreads.com/book/review_counts.json?"
        query_parameters = {"isbns": book_data['isbn'], "key": developer_key}
        full_url = base_url + urllib.parse.urlencode(query_parameters)

        # Make HTTP request to the URL built above
        json_data = requests.get(full_url).json()

        # Get data we need (average_rating) from the JSON response
        average_rating = json_data['books'][0]['average_rating']
        number_ratings = json_data['books'][0]['work_ratings_count']
        if not average_rating:
            average_rating = "Not found"
        if not number_ratings:
            number_ratings = "Not found"
        book_data['average_rating'] = average_rating
        book_data['number_ratings'] = number_ratings

        return render_template("book.html", book_data=book_data)

@app.route("/loginhome")
@login_required
def loginhome():
    """This is the first page you get to after logging in."""
    return render_template("loginhome.html")

@app.route("/logout")
@login_required
def logout():
    """Removes the user from the session, logging them out"""
    session.pop("user", None)
    return render_template("goodbye.html")

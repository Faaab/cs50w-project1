import os
import sys

from helpers import hash_password, check_password

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
            userhash = row['passwordhash']

        # DEBUG:
        print("DEBUGGING INFO (userhash):", file=sys.stderr)
        print(userhash, file=sys.stderr)





        # We found the user. Continue to check if filled-in password was correct
        if not check_password(userhash, password):
            return render_template("sorry.html", error="Password incorrect.")

        # If we get here, we found the user and the password is correct. Continue to log in.
        else:
            session["user"] = username

        return session["user"]

    # Branch for GET-request to index page; prompt for login
    else:
        return render_template("welcome.html")

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




        # TODO TODO TODO TODO CHECK WHETHER THAT USERNAME ALREADY EXISTS




        #Store the username and hashed password in the database
        hashedPassword = hash_password(password)
        db.execute("INSERT INTO users (username, passwordhash) VALUES (:username, :hashedPassword)",
            {"username": username, "hashedPassword": hashedPassword})
        db.commit()

        return render_template("registercomplete.html")

    else:
        return render_template("register.html")

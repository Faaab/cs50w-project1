import os
import sys

import helpers

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("welcome.html")

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

        #Store the username and hashed password in the database


        return render_template("registercomplete.html")

    else:
        return render_template("register.html")

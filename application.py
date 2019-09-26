import os

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
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("Username")
    password = request.form.get("Password")
    if db.execute("SELECT name FROM users where name=:name",{"name": name}).rowcount > 0:
        return render_template("error.html", message="Username already exists")
    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name,"password": password})
    db.commit()
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        name = request.form.get("Username")
        password = request.form.get("Password")
        if db.execute("SELECT name,password FROM users WHERE name=:name and password=:password",{"name": name,"password": password}).rowcount == 1:
            return render_template("home.html")
        else:
            return render_template("error.html", message="Invalid Username or Password")

@app.route("/search", methods=["POST"])
def search():
    search_text = request.form.get("search_text")
    res = db.execute("SELECT title FROM books WHERE title=:title",{"title": search_text}).fetchall()
    if res is not None:
        return render_template("results.html", titles = res)
    else:
        res = db.execute("SELECT title FROM books WHERE isbn=:isbn",{"isbn": search_text}).fetchall()
        if res is not None:
            return render_template("results.html", titles = res)
        else:
            res = db.execute("SELECT title from books WHERE author=:author",{"author": search_text}) .fetchall()
            if res is not None:
                return render_template("results.html", titles = res)
            else:
                return render_template("error.html", message = "No match found")

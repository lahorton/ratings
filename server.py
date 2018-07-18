"""Movie Ratings."""
from flask import (Flask, render_template, redirect, request,
                   flash, session)

from model import User, Rating, Movie, connect_to_db, db
from jinja2 import StrictUndefined

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/logout')
def logout():
    """Clears user_id from session"""

    del session['user_id']
    flash("Logged out.")
    return redirect("/login")


@app.route('/users')
def user_list():
    """show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/user-info')
def user_info_page():
    """connect user to desired user info page"""
 
    user_id = request.args.get("user_id")
    user = User.query.filter(User.user_id == user_id).one()
    user_ratings = Rating.query.filter(Rating.user_id == user_id).all()
    movie_title, movie_rating = SELECT Movie.title, Rating.score FROM Movie JOIN Rating ON (Movie.movie_id = Rating.movie_id) WHERE (Rating.user_id = user_id)

    # for user in users:
    #     user_age = user.age
    #     user_zipcode = user.zipcode



    # user_movie_ratings =


@app.route('/login')
def user_login():
    """Gets email and password from user"""

    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_user():
    """Log in existing users"""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()

    if user:
        session["user_id"] = user.user_id
        flash("Welcome back. You're logged in.")
        return redirect("/")
    else:
        flash("This email address is not recognized, please log in or register.")
        return redirect("/login")


@app.route('/register')
def show_registration_form():
    """Shows new user registration form"""

    return render_template("register.html")


@app.route('/register', methods=["POST"])
def add_user():
    """Adds new user information to database"""

    age = request.form.get("age")
    zipcode = request.form.get("zipcode")
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()

    if user:
        flash("That email is already registered.  Please log in.")
        return redirect("/login")

    new_user = User(email=email, password=password, age=age, zipcode=zipcode)

    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter(User.email == email).first()
    session["user_id"] = user.user_id
    flash("Logged in.")
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

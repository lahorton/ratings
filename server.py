"""Movie Ratings."""
from flask import (Flask, render_template, redirect, request,
                   flash, session)

from datetime import datetime

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

@app.route('/movies')
def movie_list():
    """show list of movies linked to info"""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_id_page(movie_id):
    """provides movie information"""

    movie = Movie.query.get(movie_id)
    released_at = movie.released_at.strftime('%d-%b-%Y')
    user_id = session["user_id"]
    score = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first()

    return render_template("movie_info.html",
                           movie=movie,
                           user_id=user_id,
                           released_at=released_at,
                           score=score)


@app.route('/movies/<int:movie_id>', methods=["POST"])
def update_movie_score(movie_id):
    """updates user movie score"""

    new_score = int(request.form.get("movie_score"))
    user_id = session["user_id"]

    rating = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first()

    if rating:
        rating.score = new_score
        db.session.add(rating)
        # rating.score = new_score
        # db.session.append(rating.score)
        flash("Your score has been updated.")

    else:
        rating = Rating(user_id=user_id, movie_id=movie_id, score=new_score)
        db.session.add(rating)
        flash("Your score has been added.")

    db.session.commit()
    return redirect(f'/movies/{movie_id}')


@app.route('/users/<user_id>')
def user_info_page(user_id):
    """connect user to desired user info page"""

    user = User.query.get(user_id)

    return render_template("user_info.html", user=user)


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
        return redirect(f"/users/{user.user_id}")
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

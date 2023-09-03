import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, ExternalFactorsForm, RatingForm
from models import db, connect_db, find_past_date, User, Rating, Summary, ExternalFactor
from decorators import check_user
from datetime import datetime

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///optimal'))

app.app_context().push()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

app.debug = True
connect_db(app)

#db.drop_all()
db.create_all()
##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY]) 
        #why does the curr user need to be in the Flask global?
    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        g.user = None


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.
    If there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                survey_reminder_time=form.survey_reminder_time.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        return redirect("/factor_intro")

    else:
        return render_template('users/signup.html', form=form)
    
@app.route("/about")
def about_page():
    return render_template("about.html")

@check_user
@app.route("/users/<int:user_id>")
def user_page(user_id):
    return render_template("/users/detail.html")

@check_user
@app.route('/factor_intro')
def factor_intro():
    return render_template("users/factor-info.html")

@check_user
@app.route('/external_factors', methods=["GET", "POST"])
def factors_form():
    """Handle display of/submitting of external factors form"""

    form = ExternalFactorsForm()

    if form.validate_on_submit():
        factors = ExternalFactor(
            ef1_name = form.ef1.data,
            ef2_name = form.ef2.data,
            ef3_name = form.ef3.data,
            ef4_name = form.ef4.data,
            ef5_name = form.ef5.data,
            user_id = g.user.id
        )
        db.session.add(factors)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("users/factors.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    if CURR_USER_KEY in session:
        do_logout()
        flash("Successfully logged out.", "success")
    else:
        flash("Error: No user currently logged in.", "danger")

    return redirect("/")

@app.route('/')
def homepage():
    """Show homepage:
    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    if not g.user:
        return render_template("home-anon.html")
    else:
        print(g.user.last_completed_survey.date())
        print(datetime.today().date())
        if g.user.last_completed_survey.date() == datetime.today().date():
            survey_done = True
        else:
            survey_done = False
        return render_template("home.html", survey_done=survey_done)

@check_user
@app.route('/take_survey', methods=["GET", "POST"])
def take_survey():
    "Displays or submits daily survey taken by user."

    form = RatingForm()

    if form.validate_on_submit():
        if form.took_all_meds.data == "Yes":
            took = True
        else:
            took = False
        if form.ef_effect.data == "Positively":
            effect = -1
        else:
            effect = 1
        rating = Rating(mood = int(form.mood.data),
                        took_all_meds = took,
                        ef_rating = (int(form.ef_rating.data) * effect),
                        med_rating = int(form.med_rating.data),
                        notes= form.notes.data,
                        user_id= g.user.id)
        db.session.add(rating)
        g.user.last_completed_survey = datetime.today().date()
        g.user.surveys_completed += 1
        db.session.add(g.user)
        db.session.commit()
        flash("Survey submitted! Good Job!", "success")
        return redirect("/")
    else:
        return render_template("survey.html", form=form)

def create_summaries():
    """Create weekly summaries for every user in the DB"""
    target_date = find_past_date(7)
    users = User.query.all()
    summary_list = []
    for user in users:
        ratings = Rating.query.filter(Rating.timestamp.date() > target_date,
                                      user_id=user.id).all()
        print("Rating: " + ratings)
        if ratings:
            numb_ratings = len(ratings)
            took_all_meds_sum = 0
            for rating in ratings:
                mood_rating_sum += rating.mood
                med_rating_sum += rating.med_rating
                ef_rating_sum += rating.ef_rating

                if rating.took_all_meds:
                    took_all_meds_sum += 1

            avg_mood = mood_rating_sum / numb_ratings
            avg_med_rating = med_rating_sum / numb_ratings
            avg_ef_rating = ef_rating_sum / numb_ratings

            summary = Summary(duration=7,
                            start_date=target_date,
                            end_date=datetime.today().date(),
                            surveys_completed=numb_ratings,
                            average_mood=avg_mood,
                            num_of_days_meds_taken=took_all_meds_sum,
                            average_ef=avg_ef_rating,
                            average_med=avg_med_rating,
                            user_id=user.id
                            )
            summary_list.append(summary)
            med_effectiveness_score = avg_mood + avg_ef_rating
    
    db.session.add_all(summary_list)
    db.session.commit()


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

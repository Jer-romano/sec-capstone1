import os, time, atexit
#from schedule import every, repeat, run_pending
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from apscheduler.schedulers.background import BackgroundScheduler

# Still need to
# Test summary function
# Flash message to user when a new summary is available 
# Maybe a 'medicines' page where a info about medications can be listed

from forms import UserAddForm, LoginForm, ExternalFactorsForm, RatingForm, MedicationsForm
from models import db, connect_db, find_past_date, User, Rating, Summary, ExternalFactor, Medication
from decorators import check_user
from helpers import send_reminder, get_quote

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///optimal'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
# TODO
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret") #Change this!!!
app.app_context().push()
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
            flash("Username or Email already in use", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        return redirect("/factor_intro")

    else:
        return render_template('users/signup.html', form=form)
    
@app.route("/about")
def about_page():
    """Displays a simple page explaining the purpose of the website."""
    return render_template("about.html")

@check_user
@app.route("/users/<int:user_id>")
def user_page(user_id):
    """Displays page of user details"""
    return render_template("/users/detail.html")

@check_user
@app.route('/factor_intro')
def factor_intro():
    """A simple blurb explaining what 'external factors' are. Part of signup flow"""
    return render_template("users/factor-info.html")

########################################################################
# Form routes

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
        return redirect("/medications")
    else:
        return render_template("users/factors_form.html", form=form)

@check_user
@app.route('/medications', methods=["GET", "POST"])
def medications_form():
    """Handle display of/submitting of medications form"""

    form = MedicationsForm()

    if form.validate_on_submit():
        med = Medication(
            med_name = form.med_name.data,
            med_dosage = form.med_dosage.data,
            user_id = g.user.id
        )
        db.session.add(med)
        db.session.commit()
        flash("User successfully created. Welcome!", "success")
        return redirect("/")
    else:
        return render_template("users/med_form.html", form=form)

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
###########################################################################
# Homepage route

@app.route('/')
def homepage():
    """Show homepage:
    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    if not g.user:
        # Return the homepage for non-logged-in users
        return render_template("home-anon.html")
    else: #User is logged in
        if 'quote' in session: #Has the QOTD been loaded?
            quote = session['quote']
        else:
            quote = get_quote()

        if g.user.last_completed_survey == datetime.today().date():
            session['survey_done'] = True
        else:
            session['survey_done'] = False
        return render_template("home.html", quote=quote)

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
        session['survey_done'] = True
        return redirect("/")
    else:
        return render_template("survey.html", form=form)


def create_summaries():
    """Create weekly summaries for every user in the DB
        This is scheduled to happen every Sunday at 8PM.
    """
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
                            user_id=user.id,
                            med_effectiveness_score = avg_mood + avg_ef_rating
                            )
            summary_list.append(summary)
    
    db.session.add_all(summary_list)
    db.session.commit()

@check_user
@app.route("/show_summaries")
def show_summaries():
    """Display page of past summaries for the User."""
    summaries = Summary.query.filter_by(user_id=g.user.id).all()
    return render_template("/users/summaries.html", summaries=summaries)

@check_user
@app.route("/medications", methods=["GET", "POST"])
def show_medications():
    """Show user medications"""
    pass

def send_reminder_emails():
    """Writes and sends reminder email to users who haven't 
        yet completed their survey today
        Have to check that
         1) The current time is 'past' a user's survey reminder time.
         2) The user hasn't already been sent a reminder email today
         3) The user hasn't completed a survey today. 
        """ 
    with app.app_context():
        today = datetime.now()
        users_to_remind = User.query.filter(today.time() > User.survey_reminder_time,
                                            today.date() > User.last_reminder_email,
                                            today.date() != User.last_completed_survey).all()
        
        if users_to_remind:
            print("found user to remind")
            for user in users_to_remind:
                send_reminder(user)
                user.last_reminder_email = today.date()
                db.session.add(user)
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

#################
# Here we schedule the send_reminder_emails function to run every 2 minutes
# And schedule the create_summaries function to run every Sunday at 20:00
scheduler.add_job(send_reminder_emails, "interval", minutes=2)
scheduler.add_job(func=create_summaries, trigger='cron', day_of_week='sun', hour=20)
scheduler.start()

atexit.register(lambda: scheduler.shutdown()) #shutdown scheduler on app exit
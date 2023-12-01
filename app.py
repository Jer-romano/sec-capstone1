import os, time, atexit, pdb
#from schedule import every, repeat, run_pending
from datetime import datetime, date
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from apscheduler.schedulers.background import BackgroundScheduler

from forms import UserAddForm, EditUserForm, LoginForm, ExternalFactorsForm, RatingForm, MedicationsForm
from models import db, connect_db, find_past_date, User, Survey, Summary, E_Factor, User_Factor_Pair, Medication
from decorators import login_required
from helpers import send_reminder, get_quote, send_ping

CURR_USER_KEY = "curr_user"

scheduler = BackgroundScheduler()

app = Flask(__name__)

# Still need to...
# Flash message to user when a new summary is available 
# Maybe a 'medicines' page where a info about medications can be listed
#Because the medicine API returns so much info, is there any point in using it?

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///optimal'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.app_context().push()
toolbar = DebugToolbarExtension(app)

connect_db(app)
#Summary.__table__.drop(db.engine)
# Rating.__table__.drop(db.engine)
# User_Factor_Pair.__table__.drop(db.engine)
# Medication.__table__.drop(db.engine)
# User.__table__.drop(db.engine)

#db.drop_all()
db.create_all()

##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY]) 
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
            db.session.rollback()
            flash("Username or Email already in use", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        return redirect("/factor_intro")

    else:
        return render_template('users/signup.html', form=form)
    
#############################################################################
# Page Routes
@app.route("/about")
def about_page():
    """Displays a simple page explaining the purpose of the website."""
    return render_template("about.html")

@app.route("/users/<int:user_id>")
@login_required
def user_page(user_id):
    """Displays page of user details"""
    return render_template("/users/detail.html")

@app.route('/factor_intro')
@login_required
def factor_intro():
    """A simple blurb explaining what 'external factors' are. Part of signup flow"""
    return render_template("users/factor-info.html")

########################################################################
# Modify User Routes
@app.route("/users/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    """Displays Edit User Form, or handles its submission"""

    form = EditUserForm(obj=g.user)
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.email = form.email.data
            g.user.image_url = form.image_url.data
            g.user.survey_reminder_time = form.survey_reminder_time.data

            db.session.add(g.user)
            db.session.commit()
            return redirect(f"/users/{g.user.id}")
        else:
            flash("Password Incorrect.", "danger")
            return redirect("/")
    else:
        return render_template("/users/edit.html", user=g.user, form=form)

@app.route('/users/delete', methods=["GET", "DELETE"])
@login_required
def delete_user():
    """Delete user."""

    try:
        db.session.delete(g.user)
        do_logout()
        db.session.commit()
        flash("User account deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}")
    finally:
        db.session.close()

    return redirect("/")

########################################################################
# Form routes

@app.route('/external_factors', methods=["GET", "POST"])
@login_required
def factors_form():
    """Handle display of/submitting of external factors form"""

    form = ExternalFactorsForm()

    if form.validate_on_submit():
        #pdb.set_trace()
        ef1 = form.ef1.data
        ef2 = form.ef2.data
        ef3 = form.ef3.data
        ef4 = form.ef4.data
        ef5 = form.ef5.data
        
        existing_factors = []
        for factor_name in [ef1, ef2, ef3, ef4, ef5]:
            if factor_name: #Not all factors will be filled out, most likely
                existing_factor = E_Factor.query.filter_by(name=factor_name).one_or_none()
                if existing_factor:
                    print("This shouldn't print: " + existing_factor.name)
                    existing_factors.append(existing_factor)
                else:
                    #Factor doesn't exist yet in the db
                    new_factor = E_Factor(name=factor_name)
                    db.session.add(new_factor)
                    db.session.commit()
                    # now have to query the db to get the new factor's id
                    new_factor = E_Factor.query.filter_by(name=factor_name).first()
                    new_pair = User_Factor_Pair(user_id=g.user.id, factor_id=new_factor.id)
                    db.session.add(new_pair)
        
        db.session.commit()
        if existing_factors:
            for factor in existing_factors:
                new_pair = User_Factor_Pair(user_id=g.user.id, factor_id=factor.id)
                db.session.add(new_pair)

        db.session.commit()
        return redirect("/medications")
    else:
        return render_template("users/factors_form.html", form=form)

# @app.route('/external_factors', methods=["GET", "POST"])
# @login_required
# def factors_form():
#     """Handle display of/submitting of external factors form"""

#     form = ExternalFactorsForm()

#     if form.validate_on_submit():
#         ef1 = form.ef1.data
#         ef2 = form.ef2.data
#         ef3 = form.ef3.data
#         ef4 = form.ef4.data
#         ef5 = form.ef5.data

#         id_dict = {"Social Interactions": 1, "Level of Exercise": 2,
#                   "My Work Day": 3,        "My Day at School": 4,
#                    "Diet": 5,              "Level of Stress": 6,
#                   "Personal Health": 7, "My Productivity": 8,
#                   "Sleep Quality": 9}

#         for factor_name in [ef1, ef2, ef3, ef4, ef5]:
#             if factor_name != "None": #Not all factors will be filled out, most likely
#                 new_factor = User_Factor_Pair(user_id=g.user.id, factor_id=id_dict[factor_name])
#                 db.session.add(new_factor)
        
#         db.session.commit()
#         return redirect("/medications")
#     else:
#         return render_template("users/factors_form.html", form=form)


@app.route('/medications', methods=["GET", "POST"])
@login_required
def medications_form():
    """Handle display of/submitting of medications form"""

    form = MedicationsForm()

    if form.validate_on_submit():
        if (form.med1_name.data and form.med1_dosage.data):
            med1 = Medication(
                med_name = form.med1_name.data,
                med_dosage = form.med1_dosage.data,
                user_id = g.user.id
            )
            db.session.add(med1)
        if (form.med2_name.data and form.med2_dosage.data):
            med2 = Medication(
                med_name = form.med2_name.data,
                med_dosage = form.med2_dosage.data,
                user_id = g.user.id
            )
            db.session.add(med2)
        if (form.med3_name.data and form.med3_dosage.data):
            med3 = Medication(
                med_name = form.med3_name.data,
                med_dosage = form.med3_dosage.data,
                user_id = g.user.id
            )
            db.session.add(med3)
        
        db.session.commit()
        flash("User successfully created. Welcome!", "success")
        return redirect("/")
    else:
        return render_template("users/med_form.html", form=form)

@app.route('/take_survey', methods=["GET", "POST"])
@login_required
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
        survey = Survey(mood = int(form.mood.data),
                        took_all_meds = took,
                        ef_rating = (int(form.ef_rating.data) * effect),
                        med_rating = int(form.med_rating.data),
                        notes= form.notes.data,
                        user_id= g.user.id)
        db.session.add(survey)
        g.user.last_completed_survey = datetime.today().date()
        g.user.surveys_completed += 1
        db.session.add(g.user)
        db.session.commit()
        flash("Survey submitted! Good Job!", "success")
        session['survey_done'] = True
        return redirect("/")
    else:
        ext_factors = g.user.factors
        meds = g.user.meds
        return render_template("survey.html", form=form, factors=ext_factors, meds=meds)

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
    #print("Config: " + str(app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()))
    if not g.user:
        # Return the homepage for non-logged-in users
        return render_template("home-anon.html")
    else: #User is logged in
        if 'quote' in session: #Has the QOTD been loaded?
            quote = session['quote']
        else:
            quote = get_quote()
            session["quote"] = quote

        if g.user.last_completed_survey == datetime.today().date():
            session['survey_done'] = True
        else:
            session['survey_done'] = False
        return render_template("home.html", quote=quote)

@app.route("/show_summaries")
@login_required
def show_summaries():
    """Display page of past summaries for the User."""
    summaries = Summary.query.filter_by(user_id=g.user.id).all()
    return render_template("/users/summaries.html", summaries=summaries)

@app.route("/medications", methods=["GET", "POST"])
@login_required
def show_medications():
    """Show user medications
        side effects
        min and max dosage
        basic info
    """
    pass

######################################################################################
# Background Scheduled Functions

def send_reminder_emails():
    """Writes and sends reminder email to users who haven't 
        yet completed their survey today
        Have to check that
         1) The user hasn't completed a survey today.
         2) The user hasn't already been sent a reminder email today
         3) The current time is 'past' a user's survey reminder time.
        """ 
    with app.app_context():
        today = datetime.now()
        users_to_remind = User.query.filter(User.survey_reminder_time != None,
                                            today.time() > User.survey_reminder_time,
                                            today.date() > User.last_reminder_email,
                                            today.date() != User.last_completed_survey).all()
        
        if users_to_remind:
            print("found user to remind")
            for user in users_to_remind:
                send_reminder(user)
                user.last_reminder_email = today.date()
                db.session.add(user)
            db.session.commit()

def create_summaries():
    """Create weekly summaries for every user in the DB.
        This is scheduled to happen every Sunday at 8PM.
        The summary 'time range' is between 12:00AM on
        the previous Sunday to 11:59PM on Saturday.
    """
    with app.app_context():
        target_date = find_past_date(7)
        users = User.query.all()
        summary_list = []
        #print("Number of users: " + str(len(users)))
        for user in users:
            surveys = Survey.query.filter(Survey.date > target_date,
                                          Survey.date != date.today(),
                                        Survey.user_id == user.id).all()
           # print("Ratings: " + str(len(surveys)))
            if surveys:
                numb_ratings = len(surveys)
                
                mood_ratings = [survey.mood for survey in surveys]
                med_ratings = [survey.med_rating for survey in surveys]
                ef_ratings = [survey.ef_rating for survey in surveys]
                took_all_meds_flags = [survey.took_all_meds for survey in surveys]

                avg_mood = sum(mood_ratings) / numb_ratings
                avg_med_rating = sum(med_ratings) / numb_ratings
                avg_ef_rating = sum(ef_ratings) / numb_ratings
                took_all_meds_sum = sum(took_all_meds_flags)
                end_date = find_past_date(1) #The last day is one day before
                summary = Summary(duration=7,
                                start_date=target_date.strftime('%d %b %Y'),
                                end_date=end_date.strftime('%d %b %Y'),
                                surveys_completed=numb_ratings,
                                average_mood=avg_mood,
                                num_days_took_all_meds=took_all_meds_sum,
                                average_ef=avg_ef_rating,
                                average_med=avg_med_rating,
                                user_id=user.id,
                                med_effectiveness_score = avg_mood + avg_ef_rating
                                )
                summary_list.append(summary)
        
        db.session.add_all(summary_list)
        db.session.commit()
       #flash("A new Summary is available!", "success")


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
db.engine.dispose()

scheduler.add_job(send_reminder_emails, "interval", minutes=2)
scheduler.add_job(send_ping, "interval", minutes=12)
scheduler.add_job(func=create_summaries, trigger='cron', day_of_week='wed', hour=22, minute=5)
scheduler.start()


atexit.register(lambda: scheduler.shutdown()) #shutdown scheduler on app exit
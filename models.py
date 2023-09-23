"""SQLAlchemy models"""

from datetime import datetime, date, timedelta, time

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

bcrypt = Bcrypt()
db = SQLAlchemy()

starter_date = date.fromisoformat('2009-12-04')

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.String(40),
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.String(40),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/user_icon.jpeg",
    )

    survey_reminder_time = db.Column(
        db.Time,
        nullable=False,
        default=time(hour=20, minute=0, second=0)
    )

    last_completed_survey = db.Column( #The last time the user completed a survey
        db.Date,
        default=starter_date #pick a random date in the past as default
    )

    last_reminder_email = db.Column(
        db.Date,
        default=starter_date
    )

    member_since = db.Column(
        db.Date,
        nullable=False,
        default=date.today()
    )

    surveys_completed = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    factors = db.relationship(
        'E_Factor',
        secondary="users_factors"
       # primaryjoin= (User_Factor_Pair.user_id == id)
    )

    surveys = relationship("Survey", cascade="all, delete-orphan", back_populates="author")
    summaries = relationship("Summary", cascade="all, delete-orphan", back_populates="patient")
    meds = relationship("Medication", cascade="all, delete-orphan", back_populates="patient")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url, survey_reminder_time):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            survey_reminder_time=survey_reminder_time
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class E_Factor(db.Model):
    """A Table for the External Factors that a User reports as affecting their mood"""
    __tablename__ = 'factors'
   
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

class User_Factor_Pair(db.Model):
    """A Table for joining a user to a specific external factor they have reported."""
    __tablename__ = 'users_factors'
   
    factor_id = db.Column(
        db.Integer,
        db.ForeignKey('factors.id',),
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )


class Survey(db.Model):
    """A daily rating completed by the User."""

    __tablename__ = 'surveys'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    mood = db.Column(
        db.Integer,
        nullable=False
    )

    took_all_meds = db.Column(
        db.Boolean,
        nullable=False
    )

    ef_rating = db.Column(
        db.Integer
    )

    med_rating = db.Column(
        db.Integer
    )

    notes = db.Column(
        db.String(140),
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.now(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    author = relationship("User", back_populates="surveys")


class Summary(db.Model):
    """A Summary of how a user has felt over the past 'x' number of days
    (Usually 7, 30, or 90)
    """
    __tablename__ = "summaries"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    duration = db.Column(
                db.Integer,
                nullable=False
    )

    start_date = db.Column(
                db.String(50),
                nullable=False
    )

    end_date = db.Column(
                db.String(50),
                nullable=False
    )

    surveys_completed = db.Column(
                        db.Integer,
                        nullable=False
    )

    average_mood = db.Column(
                db.DECIMAL(precision=3, scale=2),
                nullable=False
    )

    num_days_took_all_meds = db.Column(
                db.Integer,
                nullable=False
    )

    average_ef = db.Column(
                db.DECIMAL(precision=3, scale=2)
    )

    average_med = db.Column(
                db.DECIMAL(precision=3, scale=2)
    )

    med_effectiveness_score = db.Column(
                db.DECIMAL(precision=4, scale=2)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    patient = relationship("User", back_populates="summaries")


class Medication(db.Model):
    """A model for storing the medications a user is taking."""

    __tablename__ = 'medications'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    med_name = db.Column(
        db.String(50),
        nullable=False
    )

    med_dosage = db.Column(
        db.Integer
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    patient = relationship("User", back_populates="meds")



def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

def find_past_date(num_days):

    return date.today() - timedelta(days=num_days)
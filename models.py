"""SQLAlchemy models"""

from datetime import datetime, date

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

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

    # first_name = db.Column(
    #     db.String(25),
    # )

    # last_name = db.Column(
    #     db.String(25),
    # )

    image_url = db.Column(
        db.Text,
        default="/static/images/user_icon.jpeg",
    )

    survey_reminder_time = db.Column(
        db.Time,
        nullable=False,
        default=datetime.now(),
    )

    last_completed_survey = db.Column( #The last time the user completed a survey
        db.DateTime,
        default=starter_date #pick a random date in the past as default
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

class ExternalFactor(db.Model):
    """A Table for the External Factors that a User reports as affecting their mood"""
    __tablename__ = 'factors'
   
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    ef1_name = db.Column(
        db.String(50)
    )

    ef2_name = db.Column(
        db.String(50)
    )

    ef3_name = db.Column(
        db.String(50)
    )

    ef4_name = db.Column(
        db.String(50)
    )

    ef5_name = db.Column(
        db.String(50)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')

class Rating(db.Model):
    """A daily rating completed by the User."""

    __tablename__ = 'ratings'

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

    # ef_effect = db.Column(
    #     db.Boolean,
    #     nullable=False
    # )

    ef_rating = db.Column(
        db.Integer
    )

    med_rating = db.Column(
        db.Integer
    )

    notes = db.Column(
        db.String(140),
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User', backref="ratings")


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
                db.Date,
                nullable=False
    )

    end_date = db.Column(
                db.Date,
                nullable=False
    )

    surveys_completed = db.Column(
                        db.Integer,
                        nullable=False
    )

    average_mood = db.Column(
                db.Float,
                nullable=False
    )

    num_of_days_meds_taken = db.Column(
                db.Integer,
                nullable=False
    )

    average_ef = db.Column(
                db.Float
    )

    average_med = db.Column(
                db.Float
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

def find_past_date(num_days):

    date = datetime.date.today() - datetime.timedelta(days=num_days)
    return date
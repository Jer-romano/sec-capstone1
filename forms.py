from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, TimeField, SelectField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo
from datetime import datetime


class RatingForm(FlaskForm):
    """Form for completing a daily rating"""
    scale = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    took_all_meds = SelectField("Did you take all your medications?", choices=['Yes', 'No'])
    mood = SelectField("How would you rate your mood today?", choices=scale)
    ef_effect = SelectField("Would you say that external factors positively or negatively affected your mood?",
                            choices=["Positively", "Negatively"])
    ef_rating = SelectField("To what extent do you feel external factors affected your mood today?", choices=scale)
    med_rating = SelectField("To what extent do you feel your medication affected your mood today?", choices=scale)
    notes = TextAreaField('Notes (Optional)')

#consider installing email validator
class UserAddForm(FlaskForm):
    """Form for adding users."""
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    username = StringField('Username', validators=[DataRequired(), Length(max=40)])
    email = StringField('E-mail', validators=[DataRequired(), Length(max=40), Email(message="Invalid email.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=30),
                            EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    image_url = StringField('(Optional) Profile Image URL')
    survey_reminder_time = TimeField("Survey Reminder Time",  default=datetime.now(),
     validators=[InputRequired()])

class ExternalFactorsForm(FlaskForm):
    """Form for recording external factors relevant to user"""

    ef1 = StringField("External Factor #1")
    ef2 = StringField("External Factor #2")
    ef3 = StringField("External Factor #3")
    ef4 = StringField("External Factor #4")
    ef5 = StringField("External Factor #5")


class MedicationForm(FlaskForm):
    """Form for recording a user's medications"""

    med1 = StringField("Medication Name")
    med1_dosage = IntegerField("Dosage (in mg)", validators=[InputRequired()])
    #How to make it so that a user can add more medications to the form if necessary?


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6, max=30), DataRequired()])
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, TimeField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo
from datetime import datetime

# regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

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
    username = StringField('Username', validators=[DataRequired(), Length(max=40)])
    email = StringField('E-mail', validators=[DataRequired(), Length(max=40),
                         Email(message="Invalid email.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=30),
                            EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    image_url = StringField('(Optional) Profile Image URL')
    #nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #num_of_meds = SelectField("How many medications are you currently taking?", choices=nums)
    survey_reminder_time = TimeField("Survey Reminder Time",  default=datetime.now(),
     validators=[InputRequired()])

class EditUserForm(FlaskForm):
    """Form for editing user info"""
    email = StringField('E-mail', validators=[DataRequired(), Length(max=40),
                         Email(message="Invalid email.")])
    image_url = StringField('(Optional) Profile Image URL')
    
    survey_reminder_time = TimeField("Survey Reminder Time", validators=[InputRequired()])
    password = PasswordField("Confirm Password", 
                            validators=[InputRequired(), Length(min=6, max=30)])


class ExternalFactorsForm(FlaskForm):
    """Form for recording external factors relevant to user"""

    ef1 = StringField("External Factor #1")
    ef2 = StringField("External Factor #2")
    ef3 = StringField("External Factor #3")
    ef4 = StringField("External Factor #4")
    ef5 = StringField("External Factor #5")

# class MedForm(FlaskForm):
#     """Form for recording a single medication"""
#     med_name = StringField("Brand Name of Medication", validators=[InputRequired()])
#     med_dosage = IntegerField("Dosage (in mg)", validators=[InputRequired()])

# class MedicationsForm(FlaskForm):
#     """Form for recording all of a user's medications"""
#     meds = FieldList(FormField(MedForm), min_entries=1, max_entries=5)

class MedicationsForm(FlaskForm):
    """Form for recording all of a user's medications"""
    med_name = StringField("Brand Name of Medication", validators=[InputRequired()])
    med_dosage = IntegerField("Dosage (in mg)", validators=[InputRequired()])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6, max=30), DataRequired()])
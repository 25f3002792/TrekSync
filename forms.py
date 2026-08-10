from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register as', choices=[('user', 'Trekker'), ('staff', 'Trek Staff')], validators=[DataRequired()])

class TrekForm(FlaskForm):
    name = StringField('Trek Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    difficulty = SelectField('Difficulty', choices=[('Easy', 'Easy'), ('Moderate', 'Moderate'), ('Hard', 'Hard')], validators=[DataRequired()])
    available_slots = IntegerField('Available Slots', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Open', 'Open'), ('Closed', 'Closed'), ('Completed', 'Completed')])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])

    def validate_start_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Start date cannot be in the past.')

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data <= self.start_date.data:
            raise ValidationError('End date must be after start date.')

class StaffUpdateForm(FlaskForm):
    available_slots = IntegerField('Available Slots', validators=[NumberRange(min=0)])
    status = SelectField('Trek Status', choices=[('Open', 'Open'), ('Closed', 'Closed'), ('Completed', 'Completed')])

class UserProfileForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Email()])
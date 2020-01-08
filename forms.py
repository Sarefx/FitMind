from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Regexp, ValidationError, Email, Length, EqualTo, NumberRange, InputRequired, Optional

from db import User

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, numbers, and underscores only,")),name_exists])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists])
    password = PasswordField('Password',validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2',message='Passwords must match')])
    password2 = PasswordField('Confirm Password',validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])

class MyStats(FlaskForm):
    weight = FloatField('Bodyweight',validators=[Optional()])
    height = FloatField('Height',validators=[Optional()])
    birth_date = DateField('birth_date',validators=[Optional()])
    gender = RadioField('gender', choices=[("n/a","N/A"),("male","Male"),("female","Female"),("other","Other")],
            validators=[Optional()])
    weight_measurement_preference = RadioField('weight_measurement_preference',choices=[("kg","Kilograms"),("lbs","Pounds")],
            validators=[Optional()])
    height_measurement_preference = RadioField('height_measurement_preference',choices=[("cm","Centimeters"),("in","Inches")],
            validators=[Optional()])

class AddLog(FlaskForm):
    date = DateField('date',validators=[DataRequired()])
    cal_plus = IntegerField('Calories consumed',validators=[InputRequired()])
    cal_minus = IntegerField('Calories burnt',validators=[InputRequired()])
    day_weight = FloatField('Bodyweight',validators=[InputRequired()])    

class GetParameters(FlaskForm):
    weight_days = IntegerField('weight_days',validators=[InputRequired(), 
        NumberRange(min=1, max=10, message="The number needs to be at least 1 and no more than 10")])
    calorie_days = IntegerField('calorie_days',validators=[InputRequired(), 
        NumberRange(min=1, max=20, message="The number needs to be at least 1 and no more than 20")])
    start_day = DateField('start_day',validators=[DataRequired()])
    week_goal = FloatField('week_goal',validators=[InputRequired(), 
        NumberRange(min=-1, max=2, message="The number needs to be between -2.0 and 2.0")])

class SetGoals(FlaskForm):
    calorie_minus_goal = IntegerField('Calorie minus',validators=[Optional()])
    calorie_plus_goal = IntegerField('Calorie plus',validators=[Optional()])
    calorie_balance = IntegerField('Calorie balance',validators=[Optional()])

class GenerateGoals(FlaskForm):
    bw_goal = FloatField('',validators=[Optional()])

class SetLastCountedDate(FlaskForm):
    last_counted_date = DateField('last_counted_date',validators=[Optional()])

class GenerateGoals2(FlaskForm):
    weight = FloatField('Bodyweight',validators=[DataRequired()])
    weight_measurement_preference = RadioField('weight_measurement_preference', choices=[("lbs","lbs"), ("kg","kg")],validators=[InputRequired()])
    height = FloatField('Height',validators=[DataRequired()])
    height_measurement_preference = RadioField('height_measurement_preference', choices=[("inches","inches"), ("cm","cm")],validators=[InputRequired()])
    age =  IntegerField('Age',validators=[DataRequired()])
    gender = RadioField('gender', choices=[("male","Male"), ("female","Female"), ("other","Other")],validators=[InputRequired()])
    bw_goal = FloatField('',validators=[DataRequired()])
    bw_goal_measurement_preference = RadioField('bw_goal_measurement_preference', choices=[("lbs","lbs"), ("kg","kg")],validators=[InputRequired()])

class ChangePasword(FlaskForm):
    old_password = PasswordField('Old Password',validators=[DataRequired()])
    password = PasswordField('New Password',validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2',message='Passwords must match')])
    password2 = PasswordField('Confirm Password',validators=[DataRequired()])
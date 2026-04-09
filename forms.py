from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=2, max=20), 
        Regexp('^[A-Za-z0-9_]+$', message="Username must contain only letters, numbers, or underscores")
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class MessageForm(FlaskForm):
    username = StringField('IDENTIFIER', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('DATA_STREAM', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Execute Transmission')

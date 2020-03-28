from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired,Required
from hospital_app.models import User,specialization
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from hospital_app import db
from wtforms.fields.html5 import TelField


class LoginForm(FlaskForm):
    username = StringField('Email or username',validators=[DataRequired()])
    password = PasswordField('Password' , validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Retype Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Send Confirmation Mail')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



def get_specialization_list():
    return db.session.query(specialization).all()


class RegistrationForm_Doctor(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    qualification = StringField('Qualification',validators=[DataRequired()])
    experience = StringField('Experience',validators=[DataRequired()])
    specialization = QuerySelectField('Specialization',validators=[Required()],query_factory=get_specialization_list)
    phonenumber = TelField("Phone Number",validators=[DataRequired()])
    submit = SubmitField('Submit')
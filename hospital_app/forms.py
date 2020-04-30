from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField,SelectField,DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired,Required
from hospital_app.models import User,specialization
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from hospital_app import db
from wtforms.fields.html5 import TelField
# from flask_wtf.file import FileField, FileRequired
# from werkzeug.utils import secure_filename


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


class specialization_form(FlaskForm):
    specialization_name = StringField('Specialization: ',validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_specialization_name(self, specialization_name):
        spec_name = specialization.query.filter_by(specialization = specialization_name.data).first()
        if spec_name is not None:
            raise ValidationError('Already added!!')

class search_user(FlaskForm):
    username = StringField('Username: ',validators=[DataRequired()])
    submit = SubmitField('Search')
    

def get_specialization_list():
    return db.session.query(specialization).all()


class RegistrationForm_Doctor(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    qualification = StringField('Qualification',validators=[DataRequired()])
    experience = StringField('Experience',validators=[DataRequired()])
    specialization = QuerySelectField('Specialization',validators=[Required()],query_factory=get_specialization_list)
    phonenumber = StringField("Phone Number",validators=[DataRequired()])
    submit = SubmitField('Submit')

class search_doctor_form(FlaskForm):
    specialization = QuerySelectField('Specialization',validators=[Required()],query_factory=get_specialization_list)
    submit = SubmitField('Search')

class update_user_form(FlaskForm):
     name = StringField('Name: ')
     age = IntegerField('Age: ')
     blood_group = StringField('Blood Group: ')
     contact_number = IntegerField('Contact Number: ')
     address = TextAreaField('Address: ')
     gender_user = StringField('Gender: ')
     submit = SubmitField('Update')

# class upload_document(FlaskForm):
#     treat_id = IntegerField('Treatment Id: ')
#     type_doc = SelectField('Type: ',choices=[('Prescription','Prescription'),('Invoice','Invoice'),('Report','Report')])
#     date = DateField('Date: ')
#     File = FileField('Upload file',validators=[FileRequired()])
#     submit = SubmitField('Upload')



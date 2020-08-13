from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField,SelectField, FloatField, RadioField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, InputRequired,Required, NumberRange
from hospital_app.models import User, specialization, temporary_users, temporary_role_users
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from hospital_app import db
from wtforms.fields.html5 import TelField,DateField
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Email or username',validators=[InputRequired()])
    password = PasswordField('Password' , validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class UserRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField(
        'Retype Password', validators=[InputRequired(), EqualTo('password')])
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
    specialization_name = StringField('Specialization: ',validators=[InputRequired()])
    submit = SubmitField('Add')

    def validate_specialization_name(self, specialization_name):
        spec_name = specialization.query.filter_by(specialization = specialization_name.data).first()
        if spec_name is not None:
            raise ValidationError('Already added!!')

class search_user(FlaskForm):
    username = StringField('Username: ',validators=[InputRequired()])
    submit = SubmitField('Search')
    

def get_specialization_list():
    return db.session.query(specialization).all()


class RegistrationForm_Doctor(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField(
        'Retype Password', validators=[InputRequired(), EqualTo('password')])
    name = StringField('Name',validators=[InputRequired()])
    qualification = StringField('Qualification',validators=[InputRequired()])
    experience = StringField('Experience',validators=[InputRequired()])
    specialization = QuerySelectField('Specialization',validators=[Required()],query_factory=get_specialization_list)
    phonenumber = StringField("Phone Number",validators=[InputRequired()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
 

class search_doctor_form(FlaskForm):
    specialization = QuerySelectField('Specialization',validators=[Required()],query_factory=get_specialization_list)
    submit = SubmitField('Search')

class update_user_form(FlaskForm):
     name = StringField('Full Name')
     age = IntegerField('Age in years')
     blood_group = SelectField('Blood Group ',choices = [('Unknown','Unknown'),('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')])
     contact_number = IntegerField('Contact Number')
     address = TextAreaField('Address')
     submit = SubmitField('Update')

class update_doctor_form(FlaskForm):
     name = StringField('Name: ')
     age = IntegerField('Age: ')
     blood_group = StringField('Blood Group: ')
     contact_number = IntegerField('Contact Number: ')
     address = TextAreaField('Address: ')
     gender_doctor = StringField('Gender: ')
     qualification = TextAreaField('Qualification: ')
     experience = StringField('Experience: ')
     specialization = TextAreaField('Specialization: ')
     consultant_fee = FloatField('Consultant_fee: ')
     visiting_hours = StringField('Visiting Hours: ')
     submit = SubmitField('Update')


# class upload_document(FlaskForm):
#     treat_id = IntegerField('Treatment Id: ')
#     type_doc = SelectField('Type: ',choices=[('Prescription','Prescription'),('Invoice','Invoice'),('Report','Report')])
#     date = DateField('Date: ')
#     File = FileField('Upload file',validators=[FileRequired()])
#     submit = SubmitField('Upload')

class disease_statistic_form(FlaskForm):
    disease_name = StringField("Disease Name: ")


class patient_registration_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    birthdate = DateField("Birthdate", validators=[InputRequired()])
    firstname = StringField('First name',validators=[InputRequired()])
    lastname = StringField('Last name ')
    age = IntegerField('Age in years',validators=[InputRequired(), NumberRange(1,150)])
    blood_group = SelectField('Blood Group ',choices = [('Unknown','Unknown'),('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')])
    contact_number = IntegerField('Contact Number ',validators=[InputRequired()])
    address = TextAreaField('Address ')
    gender = RadioField('Gender ',validators=[InputRequired()], choices = [('Male','Male'),('Female','Female'),('Transgender','Transgender')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        u = temporary_users.query.filter_by(username = username.data).first()
        if user is not None or u is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        u = temporary_users.query.filter_by(email = email.data).first()
        if user is not None or u is not None:
            raise ValidationError('Please use a different email address.')

class queue_form(FlaskForm):
    treat_id = IntegerField('Treatment ID',id = "treatId",validators=[InputRequired()])
    doctor_username = StringField('Doctor username',validators=[InputRequired()])

    def validate_doctor_username(self,doctor_username):
        user = User.query.filter_by(username = doctor_username.data, role = "doctor").first()
        if user is None:
            raise ValidationError('Invalid username')

class register_role_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    doctor_username = StringField('Doctor username',default = None)
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField(
        'Retype Password', validators=[InputRequired(), EqualTo('password')])
    email = StringField('Email', validators=[InputRequired(), Email()])
    birthdate = DateField("Birthdate", validators=[InputRequired()])
    role = SelectField('Select role',choices=[('reception','Receptionist'),('compounder','Compounder'),('assistant','Assistant'),('chief_doctor','Chief Medical Officer')])
    firstname = StringField('First name',validators=[InputRequired()])
    lastname = StringField('Last name ')
    age = IntegerField('Age in years',validators=[InputRequired(), NumberRange(1,150)])
    contact_number = IntegerField('Contact Number ',validators=[InputRequired()])
    address = TextAreaField('Address ')
    work_timings = StringField('Working days - working hours',validators=[InputRequired()])
    gender = SelectField('Gender ',validators=[InputRequired()], choices = [('Male','Male'),('Female','Female'),('Transgender','Transgender')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        u = temporary_users.query.filter_by(username = username.data).first()
        x = temporary_role_users.query.filter_by(username = username.data).first()
        if user is not None or u is not None or x is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        u = temporary_users.query.filter_by(email = email.data).first()
        x = temporary_role_users.query.filter_by(email = email.data).first()
        if user is not None or u is not None or x is not None:
            raise ValidationError('Please use a different email address.')

        
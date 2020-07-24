from hospital_app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from hospital_app import login
from flask_login import UserMixin
from time import time
import jwt
from hospital_app import app
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey, Date, Boolean, LargeBinary
from datetime import datetime
from sqlalchemy import Enum



@login.user_loader
def load_user(username):
    return User.query.filter_by(username = username).first()


# username cannot be updated, patient and doctor can be deleted
class User(UserMixin,db.Model):
    username = db.Column(db.String(64), index=True, unique=True, primary_key=True,nullable= False)
    email = db.Column(db.String(100), index=True, unique=True,nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20),nullable=False)
    patient = db.relationship("Patient" , backref='user',uselist=False, cascade = 'save-update,delete')
    doctor = db.relationship("Doctor" , backref='user',uselist=False, cascade = 'save-update,delete')
    def get_reset_password_token(self,expires_in = 900):
        return jwt.encode({'reset_password':self.username,'exp':time()+expires_in},app.config['SECRET_KEY'],algorithm = 'HS256').decode('utf-8')


    @staticmethod
    def verify_reset_password_token(token):
        try:
            username = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.filter_by(username = username).first()   

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)  
    
    def get_id(self):
        return str(self.username)


#only delete, insert is allowed 
class specialization(db.Model):
    specialization = db.Column(db.String(50),primary_key=True,nullable=False)

    def get_id(self):
        return str(self .specialization)

    def __repr__(self):
        return '{}'.format(self.specialization)

class Patient( db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64) , ForeignKey('user.username'),index = True,nullable=False)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(15))
    contact_number = db.Column(db.Unicode(20))
    address = db.Column(db.String(80))
    gender_user = db.Column(db.String(15))

class Doctor( db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64) , ForeignKey('user.username'),index = True,nullable = False)
    name = db.Column(db.String(50),nullable = False)
    gender_doctor = db.Column(db.String(15))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(15))
    contact_number = db.Column(db.String(15),nullable = False)
    address = db.Column(db.String(80)) 
    qualification = db.Column(db.String(100),nullable = False)  
    experience = db.Column(db.String(15),nullable = False)
    specialization = db.Column(db.String(20),nullable = False)
    consultant_fee = db.Column(db.Float)
    visiting_hours = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date_of_joining = db.Column(db.Date)

    def __repr__(self):
        return '{}'.format(self.name)

class deleted_patients(db.Model):
    username = db.Column(db.String(64),primary_key = True)
    email = db.Column(db.String(100),unique = True,nullable = False)
    name = db.Column(db.String(50),nullable = False)
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(15))
    contact_number = db.Column(db.Unicode(20))
    address = db.Column(db.String(80))
    gender_user = db.Column(db.String(15))
    deleted_on = db.Column(db.DateTime,default=datetime.utcnow)

class deleted_doctors(db.Model):
    username = db.Column(db.String(64),primary_key = True)
    email = db.Column(db.String(100),unique = True,nullable = False)
    name = db.Column(db.String(50),nullable = False)
    gender_doctor = db.Column(db.String(15))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(15))
    contact_number = db.Column(db.String(15),nullable = False)
    address = db.Column(db.String(80)) 
    qualification = db.Column(db.String(100),nullable = False)  
    experience = db.Column(db.String(15),nullable = False)
    specialization = db.Column(db.String(20),nullable = False)
    date_of_joining = db.Column(db.Date)
    deleted_on = db.Column(db.DateTime,default=datetime.utcnow)

class is_user_deleted(db.Model):
    username = db.Column(db.String(64),primary_key=True)
    is_deleted = db.Column(Boolean, unique=False, default=False)

class upload_medical_records(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    treat_id = db.Column(db.Integer,nullable=False)
    type_doc = db.Column(Enum('Invoice','Prescription','Report',name="type_enum", create_type=False),nullable = False)
    date = db.Column(db.Date,nullable = False)
    filename = db.Column(db.String(50),nullable = False)
    File = db.Column(db.LargeBinary,nullable = False)

class upload_report(db.Model):
    treat_id = db.Column(db.Integer,primary_key=True)
    pres_id = db.Column(db.Integer,primary_key=True)
    report_name = db.Column(db.String(50),primary_key= True)
    file_name = db.Column(db.String(50),nullable = False)
    report = db.Column(db.LargeBinary,nullable = False)

class temporary_users(db.Model):
    username = db.Column(db.String(64), index=True, unique=True, primary_key=True)
    email = db.Column(db.String(100), index=True, unique=True,nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20),nullable=False)

    def get_reset_password_token(self,expires_in = 900):
        return jwt.encode({'reset_password':self.username,'exp':time()+expires_in},app.config['SECRET_KEY'],algorithm = 'HS256').decode('utf-8')


    @staticmethod
    def verify_reset_password_token(token):
        try:
            username = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return temporary_users.query.filter_by(username = username).first()   

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
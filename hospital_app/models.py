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




class User(UserMixin,db.Model):
    username = db.Column(db.String(64), index=True, unique=True,primary_key=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))

    def get_reset_password_token(self,expires_in = 600):
        return jwt.encode({'reset_password':self.username,'exp':time()+expires_in},app.config['SECRET_KEY'],algorithm = 'HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            username = jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.filter_by(username=username).first()   



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)  
    
    def get_id(self):
        return str(self.username)



@login.user_loader
def load_user(username):
    return User.query.filter_by(username = username).first()

# class user(db.Model):
#      user_id = db.Column(db.String(30),primary_key=True)
#      name = db.Column(db.Unicode(50),nullable = False)
#      # phone_num = db.Column(db.Unicode(50), nullable = True)
#      # address = db.Column(db.Text(100))
#      # age = db.Column(db.Integer)
     
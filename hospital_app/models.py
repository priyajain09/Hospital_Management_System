from hospital_app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from hospital_app import login
from flask_login import UserMixin




class User(UserMixin,db.Model):
    username = db.Column(db.String(64), index=True, unique=True,primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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
     
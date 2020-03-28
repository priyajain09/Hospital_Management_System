from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from flask_mail import Mail



app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
login = LoginManager(app)
login.login_view='login'
db = SQLAlchemy(app)
mongo = PyMongo(app)
<<<<<<< Updated upstream
#user_collection = mongo.db.users               uncomment for testing connection hereonly
#user_collection.insert({'name':'Anthoy'})
=======
# user_collection = mongo.db.users
# user_collection.insert({'name':'Anthoy'})
>>>>>>> Stashed changes
migrate = Migrate(app, db)
mail = Mail(app)

from hospital_app import  models
from .views.login import login_bp
from .views.register import register_bp
<<<<<<< Updated upstream
from .views.admin import admin_bp
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(admin_bp)
=======
# from .views.doctor_routes import doctor_routes_bp
from .views.hello import hello
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(hello)
# app.register_blueprint(doctor_routes_bp)
>>>>>>> Stashed changes


    

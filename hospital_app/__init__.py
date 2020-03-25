from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager



app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
login = LoginManager(app)
login.login_view='login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from hospital_app import  models
from .views.login import login_bp
from .views.hello import hello
app.register_blueprint(login_bp)
app.register_blueprint(hello)



    

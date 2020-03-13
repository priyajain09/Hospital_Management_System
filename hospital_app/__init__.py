from flask import Flask
from flask_sqlalchemy import SQLAlchemy                 #SQL database

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

##SQL database
db = SQLAlchemy(app)

@app.route('/')
def hello():
    return "hello_world"

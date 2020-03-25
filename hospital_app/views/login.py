''''
handles login and logout
'''

from flask_login import current_user, login_user, logout_user
from hospital_app.models import User
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm
import re

login_bp = Blueprint('login', __name__)
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


@login_bp.route('/login', methods = ['Get','Post'])
def login():
    if current_user.is_authenticated:
        return current_user.username

    form = LoginForm()

    if form.validate_on_submit():

        # checks if user gave email or username as input
        if(re.search(regex,form.username.data)):
            user = User.query.filter_by(email = form.username.data).first()
        else:
            user = User.query.filter_by(username = form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password!")
            return redirect(url_for('login.login'))

        login_user(user,remember = form.remember_me.data)
        next_page = request.args.get('next')

        # when the Url is absolute it does not redirect to the url 
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('login.index')

        # chnage it later
        return redirect(url_for('login.index'))
    return render_template('Authentication/login.html', title = "Sign In", form = form)            


@login_bp.route('/index')
# @login_required
def index():
    return("Hello world!!")

@login_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login.index'))

''''
handles login and logout
'''
from flask_login import current_user, login_user, logout_user
from hospital_app.models import User
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app.email import send_password_reset_email
import re
from hospital_app import db
from werkzeug.urls import url_parse
from hospital_app import login

login_bp = Blueprint('login', __name__)
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


@login_bp.route('/', methods = ['Get','Post'])
def login():
    if current_user.is_authenticated:
        if current_user.role=="user":
            return redirect(url_for('user.home_page'))
        if current_user.role=="admin":
            return redirect(url_for('admin.home_page'))
        if current_user.role=="doctor":
            return redirect(url_for('doctor_routes.home_page'))   
        if current_user.role == "receptionist":
            return redirect(url_for('receptionist.home_page'))  
        if current_user.role == "chief_doctor":
            return redirect(url_for('cmo.home_page'))
        if current_user.role == "compounder":
            return redirect(url_for('comp.home'))            
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
        if current_user.role=="user" :
            return redirect(url_for('user.home_page'))
        if current_user.role=="admin":
            return redirect(url_for('admin.registration_request'))
        if current_user.role=="doctor":
            return redirect(url_for('doctor_routes.home_page'))      

        if current_user.role == "reception":
            return redirect(url_for('recep.home_page'))  

        if current_user.role == "compounder":
            return redirect(url_for('comp.home'))    
        if current_user.role == "assistant":
            return redirect(url_for("assistant.home_page")) 
        if current_user.role == "chief_doctor":
            return redirect(url_for("cmo.home_page"))    

    return render_template('Authentication/authentication/login.html', title = "Sign In", form = form)            


@login_bp.route('/index')
# @login_required
def index():
    return("Hello world!!")


@login_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login.login'))


@login_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login.login'))
    return render_template('Authentication/reset_password_request.html',
                           title='Reset Password', form=form)


@login_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login.login'))
    return render_template('Authentication/reset_password.html', form=form)


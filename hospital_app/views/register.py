from hospital_app import db
from hospital_app.forms import UserRegistrationForm, RegistrationForm_Doctor
from flask import Blueprint
from flask_login import current_user, login_user, logout_user
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.models import User, Doctor, is_user_deleted, Patient, temporary_users
from hospital_app.email import send_registration_request_email

register_bp = Blueprint('register', __name__)


@register_bp.route('/confirm_email_address/<token>')
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    user = temporary_users.verify_reset_password_token(token)
    if not user:
        flash("Invalid user!!")
        return redirect(url_for('login.index'))
    
    u = is_user_deleted(username = user.username)
    db.session.add(u)
    db.session.commit()

    if user.role == "user":
        us = User(username = user.username, email = user.email, role = "user", password_hash = user.password_hash)
        db.session.add(us)
        db.session.commit()
        x = Patient(username = user.username)
        db.session.add(x)
        db.session.commit()
    else:
        us = User(username = user.username, email = user.email, role = "doctor", password_hash = user.password_hash)
        db.session.add(us)
        db.session.commit()
        
    db.session.delete(user)
    db.session.commit()
    
    return redirect(url_for('login.login'))

@register_bp.route('/register/user',methods = ['GET','POST'])
def register_user_request():
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        user = temporary_users(username = form.username.data, email = form.email.data, role = "user")
        user.set_password(form.password.data)   
        db.session.add(user)
        db.session.commit()
        # flash('Congratulations, you are now a registered user!')
        flash("Check email for the further instructions")
        send_registration_request_email(user)
        return redirect(url_for('login.login'))
    return render_template('Authentication/register.html', title='Register', form=form)  

@register_bp.route('/register/doctor',methods=['GET', 'POST'])
def register_request():
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    form = RegistrationForm_Doctor()
    if form.validate_on_submit():
        spec = str(form.specialization.data)
        user = temporary_users(username = form.username.data, email = form.email.data, role = "doctor",name = form.name.data,qualification = form.qualification.data,
        experience = form.experience.data,specialization = spec,contact_number = form.phonenumber.data)
        user.set_password(form.password.data)  
        db.session.add(user)
        db.session.commit()
        flash("You will be notified through email if your request get approved/rejected.")
        return redirect(url_for('login.login'))
    return render_template('Authentication/register_doctor.html',title = "Register Doctor",form = form)    



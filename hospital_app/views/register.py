from hospital_app import db
from hospital_app.forms import RegistrationForm, RegistrationForm_Doctor
from flask import Blueprint
from flask_login import current_user, login_user, logout_user
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.models import User
from hospital_app.email import send_registration_request_email


register_bp = Blueprint('register', __name__)


@register_bp.route('/confirm_email_address/<token>')
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login.index'))
    if user.role =="user":
        user.confirmed = True
        # db.session.add(user)
        db.session.commit()
        return redirect(url_for('login.login'))
    return redirect(url_for('register.register_doctor',token=token))


@register_bp.route('/register/<string:role>',methods=['GET', 'POST'])
def register_request(role):
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        if role == "user":
            user.role = "user"
        else:
            user.role = "doctor"    
        db.session.add(user)
        db.session.commit()
        # flash('Congratulations, you are now a registered user!')
        flash("Confirm Email-Address")
        send_registration_request_email(user)
        return redirect(url_for('login.login'))
    return render_template('Authentication/register.html', title='Register', form=form)

@register_bp.route('/register/doctor/<token>',methods = ['GET','POST'])
def register_doctor(token):
    if current_user.is_authenticated:
        return redirect(url_for('login.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login.login'))
    form = RegistrationForm_Doctor()
    if form.validate_on_submit():
        return redirect(url_for('login.index'))
    return render_template('Authentication/register_doctor.html',title = "Register Doctor",form = form)    






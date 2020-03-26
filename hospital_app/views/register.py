from hospital_app import db
from hospital_app.forms import RegistrationForm
from flask import Blueprint
from flask_login import current_user, login_user, logout_user
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.models import User


register_bp = Blueprint('register', __name__)

@register_bp.route('/register/<string:role>',methods=['GET', 'POST'])
def register(role):
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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login.login'))
    return render_template('Authentication/register.html', title='Register', form=form)
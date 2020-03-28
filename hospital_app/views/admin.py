from flask_login import current_user, login_user, logout_user
from hospital_app.models import User,Doctor
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/registration_request')
def registration_request():
    q = db.session.query(User,Doctor).join(Doctor).filter(User.confirmed == False)
    return render_template('Admin/registration_request.html',q=q)


@admin_bp.route('/admin/registration_request/<username>')
def action_reg_request(username):
    q = Doctor.query.filter_by(username = username).first()
    return render_template('Admin/registration_request_action.html',q=q)

@admin_bp.route('/admin/<username>/<action>')
def action_taken_on_request(username,action):
    if action=="Reject":
        x = Doctor.query.filter_by(username=username).first() 
        db.session.delete(x) 
        db.session.commit()
        x = User.query.filter_by(username=username).first() 
        db.session.delete(x) 
        db.session.commit()
    else:
        x = User.query.filter_by(username=username).first() 
        x.confirmed = True
        db.session.commit()
        # x = Doctor.query.filter_by(username=username).first() 
        # add doj later
    return redirect(url_for('admin.registration_request'))

  

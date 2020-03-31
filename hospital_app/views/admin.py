from hospital_app.models import User,Doctor
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/home_page')
def home_page():
    return render_template('Admin/home_page.html')

@admin_bp.route('/admin/doctor_list')
def doctor_list():
    q = db.session.query(User,Doctor).join(Doctor).filter(User.confirmed == True)
    return render_template('Admin/admin_sites/list_of_doctors.html',q=q)

@admin_bp.route('/admin/user_list')
def user_list():
    q = User.query.filter_by(role='user').all()
    return render_template('Admin/admin_sites/list_of_users.html',q=q)


@admin_bp.route('/admin/registration_request')
def registration_request():
    q = db.session.query(User,Doctor).join(Doctor).filter(User.confirmed == False)
    return render_template('Admin/admin_sites/registration_request.html',q=q)


@admin_bp.route('/admin/registration_request/<username>')
def action_reg_request(username):
    q = Doctor.query.filter_by(username = username).first()
    return render_template('Admin/admin_sites/registration_request_action.html',q=q)

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
    return redirect(url_for('admin.home_page'))
        # x = Doctor.query.filter_by(username=username).first() 
        # add doj later
    return redirect(url_for('admin.registration_request'))

  

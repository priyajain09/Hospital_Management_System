from hospital_app.models import User,Doctor, Patient, is_user_deleted, patient_queue,compounder_queue,user_role
from flask import Blueprint, render_template, redirect,url_for, request, flash
from flask_login import current_user, login_required
from hospital_app import user_collection
from flask import request
from sqlalchemy import func
from hospital_app import db
from io import BytesIO
import base64
assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/assistant/patient_queue')
@login_required
def home_page():
    username = current_user.username
    x = user_role.query.filter_by(username = username, role = "assistant").first()
    u = patient_queue.query.filter_by(doctor_username = x.doctor_username).all()    
    return render_template('Assistant/patient_queue.html',list = u)


@assistant_bp.route('/assistant/doctor_queue/<treat_id>')
@login_required
def remove_doctor_queue(treat_id):
    try:
        u = patient_queue.query.get(treat_id)
        db.session.delete(u)
        db.session.commit()
        flash("Removed successfully!")
    except:
        db.session.rollback()
        flash("Try again!")
    return redirect(url_for('assistant.home_page'))


@assistant_bp.route('/assistant/doctor_queue/remove_all')
@login_required
def remove_all_doctor_queue():
    try:
        u = patient_queue.query.delete()
        db.session.commit()
        flash("Removed All")
    except:
        db.session.rollback()
        flash("Try again !")
    return redirect(url_for('assistant.home_page'))    

@assistant_bp.route('/assistant/user_details/<username>')
@login_required
def user_details(username):
    q = Patient.query.filter_by(username = username).first()
    image = base64.b64encode(q.File).decode('ascii')
    return render_template('Assistant/user_details.html',user=q,image = image)
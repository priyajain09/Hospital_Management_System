from hospital_app.models import User,Doctor, Patient, is_user_deleted, patient_queue,compounder_queue
from flask import Blueprint, render_template, redirect,url_for, request, flash
from flask_login import current_user, login_required
from hospital_app import user_collection
from flask import request
from sqlalchemy import func
from hospital_app import db

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/assistant/patient_queue')
def home_page():
    if request.method == "POST":
        search_text = request.form['search_text']
        if request.form['filter'] == "username":
            u = patient_queue.query.filter(func.lower(patient_queue.username).contains(search_text.lower(),autoescape = True))

        elif request.form['filter'] == "name":
            u = patient_queue.query.filter(func.lower(patient_queue.name).contains(search_text.lower(),autoescape = True))

        elif request.form['filter'] == "none":        
            u = patient_queue.query.all()

        elif request.form['filter'] == "doctor_name":        
            u = patient_queue.query.filter(func.lower(patient_queue.doctor).contains(search_text.lower(),autoescape = True))   
    else:
        u = patient_queue.query.all()    
    return render_template('Assistant/patient_queue.html',list = u)


@assistant_bp.route('/assistant/doctor_queue/<treat_id>')
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
def remove_all_doctor_queue():
    try:
        u = patient_queue.query.delete()
        db.session.commit()
        flash("Removed All")
    except:
        db.session.rollback()
        flash("Try again !")
    return redirect(url_for('assistant.home_page'))    
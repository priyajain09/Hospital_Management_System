from hospital_app.models import User,Doctor, Patient, is_user_deleted, patient_queue,compounder_queue
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import db
from hospital_app import mongo
import json
from flask_login import current_user, login_required
from hospital_app import user_collection
from flask import request
from hospital_app.forms import patient_registration_form,queue_form
import random, string
from sqlalchemy import func
from datetime import date, datetime, timedelta

recep_bp = Blueprint('recep', __name__)

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return  result_str

@recep_bp.route('/patient_registration', methods = ['GET','POST'])
def home_page():
    form = patient_registration_form()
    
    if form.validate_on_submit():
        try:
            u = is_user_deleted(username = form.username.data)
            db.session.add(u)
            user = User(username = form.username.data, email = form.email.data, role = "user")
            password = get_random_alphanumeric_string(8)
            user.set_password(password)   
            db.session.add(user)
            x = Patient(username = form.username.data, name = form.firstname.data+" "+form.lastname.data,
            age = form.age.data, blood_group = form.blood_group.data, contact_number= form.contact_number.data,
            address = form.address.data, gender_user = form.gender.data, birthdate = form.birthdate.data)
            db.session.add(x)
            db.session.commit()
            flash("Added successfully!!")
        except:
            db.session.rollback()
            flash("Try Again!")    
        return redirect(url_for('recep.home_page'))
    return render_template('Reception/patient_registration.html',form = form)

@recep_bp.route('/patient_enquiry', methods = ['GET','POST'])
def patient_enquiry():

    if request.method == "POST":
        search_text = request.form['search_text']
        if request.form['filter'] == "username":
            u = db.session.query(User, Patient).join(Patient).filter(User.username.contains(search_text))

        elif request.form['filter'] == "name":
            u = db.session.query(User, Patient).join(Patient).filter(Patient.name.contains(search_text))
        
        elif request.form['filter'] == "email":
            u = db.session.query(User, Patient).join(Patient).filter(User.email.contains(search_text))

        elif request.form['filter'] == "none":        
            u = db.session.query(User, Patient).join(Patient).all()
    else:
        u = db.session.query(User, Patient).join(Patient).all()        
    return render_template("Reception/patient_enquiry.html",list = u)

    

@recep_bp.route('/reception/add_to_queue/<name>/<username>',methods = ['GET','POST'])
def add_to_queue(name, username):
    form = queue_form()
    if form.validate_on_submit():
        try:
            treat_id = form.treat_id.data

            if (patient_queue.query.get(treat_id) is not None):
                flash("Already added!")
                return redirect(url_for('recep.patient_enquiry'))
            
            treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })    
            #existing treatment
            if treatment['total_prescriptions'] != 0:
                mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions': treatment['total_prescriptions'] + 1 }})
                mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : treatment['total_prescriptions'] + 1, 'timestamp' : datetime.now()} } })
            else:
                flash("No existing treatment with this treatment ID!")
                return redirect(url_for('recep.patient_enquiry'))
            doctor_username = form.doctor_username.data
            doctor = Doctor.query.filter_by(username = doctor_username).first()
            doctor_name = doctor.name
            patient = patient_queue(name = name, username = username, treat_id = treat_id, doctor = doctor_name,
            doctor_username = doctor_username)
            db.session.add(patient)
            db.session.commit()
            flash("Added successfully!")
            return redirect(url_for('recep.patient_enquiry'))
        except:
            db.session.rollback()
            flash("Try Again!") 

    else:
        treatments = mongo.db.Treatment.find({"patient_userid":username})
        return render_template('Reception/treatments.html',treatments = treatments,name = name, username = username,form = form)



@recep_bp.route('/<name>/<username>')
def add_to_compounder_queue(name,username):
    try:
        user = compounder_queue.query.get(username)
        if(user is not None):
            flash("Already added!")
            return redirect(url_for('recep.patient_enquiry'))
        u = compounder_queue(name = name, username = username)
        db.session.add(u)
        db.session.commit()
        flash("Added successfully!")
    except:
        db.session.rollback()
        flash("Try Again!")    
    return redirect(url_for('recep.patient_enquiry'))

@recep_bp.route('/compounder_queue',methods = ['GET','POST'])
def compounderQueue():
    if request.method == "POST":
        search_text = request.form['search_text']
        if request.form['filter'] == "username":
            u = compounder_queue.query.filter(func.lower(compounder_queue.username).contains(search_text.lower(),autoescape = True))

        elif request.form['filter'] == "name":
            u = compounder_queue.query.filter(func.lower(compounder_queue.name).contains(search_text.lower(),autoescape = True))

        elif request.form['filter'] == "none":        
            u = compounder_queue.query.all()
    else:
        u = compounder_queue.query.all()    
    return render_template('Reception/compounder_queue.html',list = u)

@recep_bp.route('/doctor_queue',methods = ['GET','POST'])
def doctorQueue():
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
    return render_template('Reception/patient_queue.html',list = u)

@recep_bp.route('/compounder_queue/<username>')
def remove_compounder_queue(username):
    try:
        u = compounder_queue.query.get(username)
        db.session.delete(u)
        db.session.commit()
        flash("Removed successfully!")
    except:
        db.session.rollback()
        flash("Try again!")
    return redirect(url_for('recep.compounderQueue'))


@recep_bp.route('/compounder_queue/remove_all')
def remove_all_compounder_queue():
    try:
        u = compounder_queue.query.delete()
        db.session.commit()
        flash("Removed All")
    except:
        db.session.rollback()
        flash("Try again !")
    return redirect(url_for('recep.compounderQueue'))
        
@recep_bp.route('/doctor_enquiry')
def doctor_enquiry():
    u = Doctor.query.all()
    return render_template('/Reception/doctor_enquiry.html',list = u)

@recep_bp.route('/doctor_queue/<treat_id>')
def remove_doctor_queue(treat_id):
    try:
        u = patient_queue.query.get(treat_id)
        db.session.delete(u)
        db.session.commit()
        flash("Removed successfully!")
    except:
        db.session.rollback()
        flash("Try again!")
    return redirect(url_for('recep.doctorQueue'))


@recep_bp.route('/doctor_queue/remove_all')
def remove_all_doctor_queue():
    try:
        u = patient_queue.query.delete()
        db.session.commit()
        flash("Removed All")
    except:
        db.session.rollback()
        flash("Try again !")
    return redirect(url_for('recep.doctorQueue'))
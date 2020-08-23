from hospital_app.models import User,Doctor, Patient, is_user_deleted, patient_queue,compounder_queue,user_role
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
import base64
from werkzeug.security import generate_password_hash, check_password_hash

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
            file = request.files[form.image.name]
            u = is_user_deleted(username = form.username.data)
            db.session.add(u)
            user = User(username = form.username.data, email = form.email.data, role = "user")
            # password = get_random_alphanumeric_string(8)
            password = "password"
            user.set_password(password)   
            db.session.add(user)
            x = Patient(username = form.username.data, name = form.firstname.data+" "+form.lastname.data,
            age = form.age.data, blood_group = form.blood_group.data, contact_number= form.contact_number.data,
            address = form.address.data, gender_user = form.gender.data, birthdate = form.birthdate.data,File = file.read())
            db.session.add(x)
            db.session.commit()
            flash("Added successfully!!") 
        except:
            db.session.rollback()
            flash("Try Again") 
        return redirect(url_for('recep.home_page'))   
    return render_template('Reception/patient_registration.html',form = form)

@recep_bp.route('/patient_enquiry', methods = ['GET','POST'])
def patient_enquiry():
    u = db.session.query(User, Patient).join(Patient).all()        
    return render_template("Reception/patient_enquiry.html",list = u)

@recep_bp.route('/reception/user_details/<username>',defaults={'email':None})
@recep_bp.route('/reception/user_details/<username>/<email>')
def user_details(username,email):
    if email is None:
        u = User.query.get(username)
        email = u.email
    q = Patient.query.filter_by(username = username).first()
    image = base64.b64encode(q.File).decode('ascii')
    return render_template('Reception/user_details.html',user=q,email = email,image = image)

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
            doctor_username = form.doctor_username.data
            doctor = Doctor.query.filter_by(username = doctor_username).first()
            if doctor is None:
                flash("Invalid doctor username! ")
                return redirect(url_for('admin.add_to_queue',name = name, username = username))
            #existing treatment
            if treatment['total_prescriptions'] != 0:
                mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions': treatment['total_prescriptions'] + 1 }})
                mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : treatment['total_prescriptions'] + 1, 'timestamp' : datetime.now()} } })
                mongo.db.Treatment.update(
                    { "treat_id": int(treat_id) },
                    { "$set": 
                        {
                            "pres_status" : "not filled"
                        }
                    }
                )    
            else:
                flash("No existing treatment with this treatment ID!")
                return redirect(url_for('admin.add_to_queue',name = name, username = username))
            
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
    images = []
    for i in u:
         images.append(base64.b64encode(i.File).decode('ascii'))
    return render_template('/Reception/doctor_enquiry.html',list = u,images = images)

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

@recep_bp.route('/receptionist/view_profile')
def view_profile():
    username = current_user.username
    u = user_role.query.filter_by(username = username,role="reception").first()
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('Reception/view_profile.html',user = u,image = image)    

@recep_bp.route('/receptionist/update_profile',methods = ['GET','POST'])
def update_profile():
    if request.method == "POST":
        file = request.files['profile_photo']

        u = user_role.query.filter_by(role="reception").first()

        if file and file.filename != "":
            u.File = file.read()

        
        u.name = request.form['name']
        u.age = request.form['age']
        u.address = request.form['address']
        u.contact_number = request.form['contact_number']
        u.work_timings = request.form['work_timings']
        
        try:
            db.session.commit()
            flash("Updated successfully!")
        except:
            db.session.rollback()
            flash("Try Again!")    
    u = user_role.query.filter_by(role="reception").first()
    image = base64.b64encode(u.File).decode('ascii')         
    return render_template('Reception/update_profile.html',user = u,image = image) 

@recep_bp.route('/receptionist/change_password',methods = ['GET','POST'])
def change_password():
    if request.method == "POST":
        old_password = request.form['old_pass']  
        if check_password_hash(current_user.password_hash, old_password) == False:
            message = "Wrong Password!"
            return render_template('Reception/change_password.html',message = message) 
        
        new_password = request.form['new_pass']
        current_user.set_password(new_password)
        try:
            db.session.commit()
            flash("Password changed!")
        except:
            db.session.rollback()
            flash("Try again!")    
    return render_template('Reception/change_password.html')     
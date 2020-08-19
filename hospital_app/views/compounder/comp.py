from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
from hospital_app.models import User,Doctor, Patient, patient_queue,compounder_queue , user_role
from hospital_app import db
import json
from flask_login import current_user
from hospital_app.forms import update_doctor_form,change_password_form
from hospital_app.models import Doctor
from datetime import date, datetime, timedelta
from collections import defaultdict
from operator import itemgetter 
from io import BytesIO
import base64
  
comp_bp = Blueprint('comp',__name__)

@comp_bp.route('/comp/')
def home():
    return render_template('Compounder/home.html')

@comp_bp.route('/queue/')
def queue():
    u = compounder_queue.query.all()    
    return render_template('Compounder/sites/comp_queue.html', list = u)

@comp_bp.route('/visit_patient/<username>')
def visit_patient(username):
    treatments = mongo.db.Treatment.find({"patient_userid": username })
    return render_template('Compounder/sites/visit_patient.html', username = username, treatments = treatments)

@comp_bp.route('/comp_start_new_treatment/<username>')
def comp_new_start_treatment(username):

    user = Patient.query.filter_by(username = username).first()
    doctor_list = Doctor.query.all()
    print(user.name)
    treatment = mongo.db.Treatment.find_one({ 'patient_userid' : username , 'status' : "compounder"  })

    if treatment != None:
        print("treatment is has already been started")
        return render_template('Compounder/sites/comp_start_treatment.html', treatment = treatment , doctor_list = doctor_list)
    elif treatment == None:
        #get total number of treatments from mongo and increment it by 1 and update it
        query_total_treat = { "Description": "Total number of treatments started" }
        doc_total_treat_cursor = mongo.db.Treatment.find(query_total_treat)
        doc_total_treat_list = list(doc_total_treat_cursor)
            
        bson_int64_treat_id = doc_total_treat_list[0].get('total_treatments')+1
        mongo.db.Treatment.update(query_total_treat,{"$set":{'total_treatments':bson_int64_treat_id}})
            
        #insert new treatment data
        mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'status' : "compounder", 'doctorid': '',  'doctor_name': '','patient_userid' : username, 'patient_name' : user.name, 'gender' : user.gender_user, 'age' : user.age , 'blood_group' : user.blood_group,'disease' : [], 'Referto' : "",'total_prescriptions' : 0,'time_stamp': datetime.now(), 'allergies': [], 'chronic':[], 'prescription' : []})
        treatment = mongo.db.Treatment.find_one({'treat_id' : bson_int64_treat_id })
        return render_template('Compounder/sites/comp_start_treatment.html', treatment = treatment , doctor_list = doctor_list)
    else :
        return "can't continue treatment"

@comp_bp.route('/comp_add_prescription/<treat_id>', methods=['GET', 'POST'])
def add_prescription(treat_id):

    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })

    if request.method == 'POST':
        temperature = request.form['temperature']
        Sys = request.form['Sys']
        Dia = request.form['Dia']
        allergies = request.form.getlist('allergies[]')
        chronic = request.form.getlist('chronic[]')
        if treatment['doctorid'] == '':
            doctorid = request.form['doctor']
        else:
            doctorid = treatment['doctorid']
        print(temperature)
        doctor = Doctor.query.filter_by(username = doctorid).first()
        #new treatment
        if treatment['total_prescriptions'] == 0:
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions': 1 , 'doctorid': doctorid , 'doctor_name': doctor.name,'status' : "assistant"}})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : 1, 'timestamp' : datetime.now(), 'blood_pressure' : Sys+'/'+Dia+'mm Hg' , 'temperature' : temperature + " F" } } })

            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{ 'allergies' : { '$each': allergies }}})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{ 'chronic' : { '$each': chronic }}})

        #existing treatment
        if treatment['total_prescriptions'] != 0:
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions': treatment['total_prescriptions'] + 1 , 'status' : "assistant"}})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : treatment['total_prescriptions'] + 1, 'timestamp' : datetime.now(), 'blood_pressure' : Sys+'/'+Dia+' mm Hg' , 'temperature' : temperature + " F"} } })

            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{ 'allergies' : { '$each': allergies }}})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{ 'chronic' : { '$each': chronic }}})

        flag = 0
        #add treatment to patient queue
        try:    
            doctor_username = doctorid
            doctor = Doctor.query.filter_by(username = doctor_username).first()
            patient = Patient.query.filter_by(username = treatment['patient_userid']).first()
            doctor_name = doctor.name
            patient = patient_queue(name = patient.name, username = patient.username, treat_id = treat_id, doctor = doctor_name,
            doctor_username = doctor_username)
            db.session.add(patient)
            db.session.commit()
            print('Successfully added to patient Queue')
            flag = 1
        except:
            db.session.rollback()

        if flag == 1 :
            try:
                u = compounder_queue.query.get(treatment['patient_userid'])
                db.session.delete(u)
                db.session.commit()
                print("Removed successfully!")
            except:
                db.session.rollback()
                print("Try again!")
            
    return redirect(url_for('comp.queue'))

@comp_bp.route('/comp_continue_treatment/<treat_id>')
def comp_continue_treatment(treat_id):
    mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'status' : "compounder"}})
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })
    doctor_list = Doctor.query.all()
    return render_template('Compounder/sites/comp_start_treatment.html', treatment = treatment, doctor_list = doctor_list)

@comp_bp.route('/comp-view_profile',methods = ['GET','POST'])
def view_profile():
    compounder = user_role.query.filter_by(role = "compounder").first()
    print(compounder)
    image = base64.b64encode(compounder.File).decode('ascii')
    return render_template('Compounder/sites/view_profile.html',user = compounder,image = image)

@comp_bp.route('/comp-update_profile',methods = ['GET','POST'])
def update_profile():
    if request.method == "POST":
        file = request.files['profile_photo']

        u = user_role.query.filter_by(role = "compounder").first()

        if file and file.filename != "":
            u.File = file.read()

        u.name = request.form['name']
        u.age = request.form['age']
        u.address = request.form['address']
        u.contact_number = request.form['contact_number']
        u.gender = request.form['gender']
        u.work_timings = request.form['work_timings']

        try:
            db.session.commit()
            flash("Updated successfully!")
        except:
            db.session.rollback()
            flash("Try Again!")    
    u = user_role.query.filter_by(role = "compounder").first()
    image = base64.b64encode(u.File).decode('ascii')         
    return render_template('Compounder/sites/update_profile.html',user = u,image = image)

@comp_bp.route('/comp-change_password',methods = ['GET','POST'])
def change_password():
    form = change_password_form()
    if form.validate_on_submit():
        
        current_user.set_password(form.password.data)
        try:
            db.session.commit()
            flash("Updated successfully")
        except:
            db.session.rollback()
            flash("Try Again")

    return render_template('Compounder/sites/change_password.html',form = form)

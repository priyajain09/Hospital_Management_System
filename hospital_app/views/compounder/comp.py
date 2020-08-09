from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
from hospital_app.models import User,Doctor, Patient, patient_queue,compounder_queue
from hospital_app import db
import json
from flask_login import current_user
from hospital_app.forms import update_doctor_form
from hospital_app.models import Doctor
from datetime import date, datetime, timedelta
from collections import defaultdict
from operator import itemgetter 
  
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
    print(user.name)
    #data from start treatment form

    #get total number of treatments from mongo and increment it by 1 and update it
    query_total_treat = { "Description": "Total number of treatments started" }
    doc_total_treat_cursor = mongo.db.Treatment.find(query_total_treat)
    doc_total_treat_list = list(doc_total_treat_cursor)
            
    bson_int64_treat_id = doc_total_treat_list[0].get('total_treatments')+1
    mongo.db.Treatment.update(query_total_treat,{"$set":{'total_treatments':bson_int64_treat_id}})
            
    #insert new treatment data
    mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'patient_userid' : username, 'patient_name' : user.name, 'gender' : user.gender_user, 'age' : user.age , 'blood_group' : user.blood_group,'disease_name' : "", 'Referto' : "",'total_prescriptions' : 0,'time_stamp': datetime.now(), 'doctorid': '', 'allergies': [], 'chronic':[], 'prescription' : []})
    treatment = mongo.db.Treatment.find_one({'treat_id' : bson_int64_treat_id })
    return render_template('Compounder/sites/comp_start_treatment.html', treatment = treatment)

@comp_bp.route('/comp_add_prescription/<treat_id>', methods=['GET', 'POST'])
def add_prescription(treat_id):

    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })

    if request.method == 'POST':
        temperature = request.form['temperature']
        Sys = request.form['Sys']
        Dia = request.form['Dia']
        allergies = request.form['allergies']
        allergies = allergies.split()
        chronic = request.form['chronic']
        chronic = chronic.split()
        if treatment['doctorid'] == '':
            doctorid = request.form['doctor']
        else:
            doctorid = treatment['doctorid']
        print(temperature)

        #new treatment
        if treatment['total_prescriptions'] == 0:
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions': 1 , 'doctorid': doctorid }})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : 1, 'blood_pressure' : Sys+'/'+Dia+'mm Hg' , 'temperature' : temperature } } })

            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{ 'allergies' : { '$each': allergies }}})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{ 'chronic' : { '$each': chronic }}})

        #existing treatment
        if treatment['total_prescriptions'] != 0:
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions': treatment['total_prescriptions'] + 1 }})
            mongo.db.Treatment.update({ "treat_id": int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : treatment['total_prescriptions'] + 1, 'blood_pressure' : Sys+'/'+Dia+' mm Hg' , 'temperature' : temperature } } })

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
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })

    return render_template('Compounder/sites/comp_start_treatment.html', treatment = treatment)

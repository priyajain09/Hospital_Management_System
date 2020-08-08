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
    treatment = mongo.db.Treatment.find({"patient_userid": username })
    return render_template('Compounder/sites/visit_patient.html', username = username, treatment = treatment)

@comp_bp.route('/comp_start_treatment/<username>')
def comp_start_treatment(username):

    user = Patient.query.filter_by(username = username).first()
    print(user.name)
    #data from start treatment form

    doctor_inputs = []
    doctor_closed = []
    #get total number of treatments from mongo and increment it by 1 and update it
    query_total_treat = { "Description": "Total number of treatments started" }
    doc_total_treat_cursor = mongo.db.Treatment.find(query_total_treat)
    doc_total_treat_list = list(doc_total_treat_cursor)
            
    bson_int64_treat_id = doc_total_treat_list[0].get('total_treatments')+1
    mongo.db.Treatment.update(query_total_treat,{"$set":{'total_treatments':bson_int64_treat_id}})
            
    #insert new treatment data
    mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'patient_userid' : username, 'patient_name' : user.name,'disease_name' : "", 'Referto' : "",'total_prescriptions' : 0,'time_stamp': datetime.now(), 'alldoctors':doctor_inputs, 'doctor_closed' : doctor_closed})
    treatment = mongo.db.Treatment.find_one({'treat_id' : bson_int64_treat_id })
    return render_template('Compounder/sites/comp_start_treatment.html', treatment = treatment)


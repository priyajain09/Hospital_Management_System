from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
import json
# from datetime import date
from datetime import datetime

doctor_routes_bp = Blueprint('doctor_routes',__name__)

@doctor_routes_bp.route('/doctor')
def home_page():      
    return render_template('Doctor/home.html')

@doctor_routes_bp.route('/rough', methods=['GET', 'POST'])
def rough():
    if request.method == 'POST':
            patient_userid = request.form['patient_userid']
            patient_name = request.form['patient_name']
            doctor_inputs = request.form.getlist('doctor_inputs[]')
            today = date.today()
            print(type(request.form['doctor_inputs[]']))
            print(patient_name)
            print(type(doctor_inputs))
            for x in range(len(doctor_inputs)): 
                print(doctor_inputs[x]) 
            #mongo.db.Treatment.insert(x)      
    return render_template('rough.html')


@doctor_routes_bp.route('/start_treatment', methods=['GET', 'POST'])
def start_treatment():      
    
    if request.method == 'POST':
            #data from start treatment form
            patient_userid = request.form['patient_userid']
            patient_name = request.form['patient_name']
            doctor_inputs = request.form.getlist('doctor_inputs[]')
            
            #get total number of treatments from mongo and increment it by 1 and update
            query_total_treat = { "Description": "Total number of treatments started" }
            doc_total_treat_cursor = mongo.db.Treatment.find(query_total_treat)
            doc_total_treat_list = list(doc_total_treat_cursor)
            
            bson_int64_treat_id = doc_total_treat_list[0].get('total_treatments')+1
            mongo.db.Treatment.update(query_total_treat,{"$set":{'total_treatments':bson_int64_treat_id}})
            
            #insert new treatment data
            mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'patient_userid' : patient_userid, 'patient_name' : patient_name,'disease_name' : "", 'Referto' : "",'time_stamp': datetime.now(), 'alldoctors':doctor_inputs})
            
            return redirect(url_for('doctor_routes.home_page'))
        
    return render_template('Doctor/doctor_sites/Start_treatment.html')
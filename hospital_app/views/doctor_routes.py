from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
import json
from flask_login import current_user
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
            mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'patient_userid' : patient_userid, 'patient_name' : patient_name,'disease_name' : "", 'Referto' : "",'total_prescriptions' : 0,'time_stamp': datetime.now(), 'alldoctors':doctor_inputs})
            
            return redirect(url_for('doctor_routes.home_page'))
        
    return render_template('Doctor/doctor_sites/Start_treatment.html')

@doctor_routes_bp.route('/current_treatment_list', methods=['GET', 'POST'])
def current_treatment_list():
    doc_treatment_cursor = mongo.db.Treatment.find({ "treat_id": { "$ne": 0 } })
    return render_template('Doctor/doctor_sites/current_treatment_list.html',treatment=doc_treatment_cursor)
    
@doctor_routes_bp.route('/treatment_info/<treat_id>', methods=['GET', 'POST'])
def treatment_info(treat_id):
    doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) })
    print(doc_treatment)
    total_prescriptions = doc_treatment['total_prescriptions']
    print(total_prescriptions)
    print(type(total_prescriptions))
    #to be done : editing some attributes of treatment document like disease_name, alldoctors etc.
    if total_prescriptions == 0 :
        return render_template('Doctor/doctor_sites/treatment_info.html', treatment=doc_treatment, treat_id = treat_id)
    else :
        return render_template('Doctor/doctor_sites/treatment_info.html', treatment=doc_treatment, treat_id = treat_id, prescriptions=doc_treatment["prescription"])

@doctor_routes_bp.route('/add_prescription/<treat_id>', methods=['GET', 'POST'])
def add_prescription(treat_id):
    if request.method == 'POST':
        #data from start treatment form
        tests = request.form['tests']
        diet_plan = request.form['diet_plan']
        str_next_visit_date = request.form['next_visit_date']
        medicines_inputs = request.form.getlist('medicines_inputs[]')
        symptoms_inputs = request.form.getlist('symptoms_inputs[]')

        #get and update total prescription under a treatment
        doc_treatment = mongo.db.Treatment.find({ "treat_id": int(treat_id) })
        doc_treatment_list = list(doc_treatment)
        presc_id = doc_treatment_list[0].get('total_prescriptions')+1

        #update total prescriptions number under a treatment
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions':presc_id }})
        
        #insert new prescription data
        mongo.db.Treatment.update({'treat_id' : int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : presc_id , 'pres_doctor_userid' : current_user.username , 'time_stamp': datetime.now(), 'tests' : tests , 'diet_plan' : diet_plan, 'str_next_visit_date' : str_next_visit_date , 'medicines_inputs' : medicines_inputs , 'symptoms_inputs' : symptoms_inputs }}})

    return redirect(url_for('doctor_routes.treatment_info', treat_id = treat_id))
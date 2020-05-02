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
    # if request.method == 'POST':
    #         patient_userid = request.form['patient_userid']
    #         patient_name = request.form['patient_name']
    #         doctor_inputs = request.form.getlist('doctor_inputs[]')
           
    #         print(type(request.form['doctor_inputs[]']))
    #         print(patient_name)
    #         print(type(doctor_inputs))
    #         for x in range(len(doctor_inputs)): 
    #             print(doctor_inputs[x]) 
            #mongo.db.Treatment.insert(x)      
    return render_template('rough.html')


@doctor_routes_bp.route('/start_treatment', methods=['GET', 'POST'])
def start_treatment():      
    
    if request.method == 'POST':
            #data from start treatment form
            patient_userid = request.form['patient_userid']
            patient_name = request.form['patient_name']
            doctor_inputs = request.form.getlist('doctor_inputs[]')
            doctor_closed = []
            #get total number of treatments from mongo and increment it by 1 and update
            query_total_treat = { "Description": "Total number of treatments started" }
            doc_total_treat_cursor = mongo.db.Treatment.find(query_total_treat)
            doc_total_treat_list = list(doc_total_treat_cursor)
            
            bson_int64_treat_id = doc_total_treat_list[0].get('total_treatments')+1
            mongo.db.Treatment.update(query_total_treat,{"$set":{'total_treatments':bson_int64_treat_id}})
            
            #insert new treatment data
            mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'patient_userid' : patient_userid, 'patient_name' : patient_name,'disease_name' : "", 'Referto' : "",'total_prescriptions' : 0,'time_stamp': datetime.now(), 'alldoctors':doctor_inputs, 'doctor_closed' : doctor_closed})
            
            return redirect(url_for('doctor_routes.home_page'))
        
    return render_template('Doctor/doctor_sites/Start_treatment.html')

@doctor_routes_bp.route('/current_treatment_list', methods=['GET', 'POST'])
def current_treatment_list():
    doc_treatment_cursor = mongo.db.Treatment.find({ "treat_id": { "$ne": 0 } })
    return render_template('Doctor/doctor_sites/current_treatment_list.html',treatment=doc_treatment_cursor)
    
@doctor_routes_bp.route('/treatment_info/<treat_id>', methods=['GET', 'POST'])
def treatment_info(treat_id):
    if request.method == 'POST':    
        disease_name = request.form['disease_name']

        alldoctors = request.form.getlist('doctor_inputs[]')
        print(alldoctors)
        print(disease_name)

        doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) })
        Doctors = doc_treatment['alldoctors']
        print(type(Doctors))
        print(Doctors)
        print(type(alldoctors))
        print(type(alldoctors[0]))
        for doctor in alldoctors :
            Doctors.append(doctor)
        print(Doctors)
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'disease_name':disease_name , "alldoctors" : Doctors }})

    doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) })
    #print(doc_treatment)
    total_prescriptions = doc_treatment['total_prescriptions']
    #print(total_prescriptions)
    #print(type(total_prescriptions))
    #to be done : editing some attributes of treatment document like disease_name, alldoctors etc.


    if total_prescriptions == 0 :
        return render_template('Doctor/doctor_sites/treatment_info.html', treatment=doc_treatment, treat_id = treat_id)
    else :
        return render_template('Doctor/doctor_sites/treatment_info.html', treatment=doc_treatment, treat_id = treat_id, prescriptions=doc_treatment["prescription"])


@doctor_routes_bp.route('/treatment_info/<treat_id>/refer', methods=['GET', 'POST'])
def refer_info(treat_id):
    if request.method == 'POST':    
        Referto = request.form['Referto']
        print(Referto)
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{ 'Referto':Referto , 'treat_closed_on': datetime.now()}})
        doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) }) 
        mongo.db.Past_Treatments.insert(doc_treatment)
        mongo.db.Treatment.remove({ "treat_id": int(treat_id) })       
    return redirect(url_for('doctor_routes.home_page'))

@doctor_routes_bp.route('/add_prescription/<treat_id>', methods=['GET', 'POST'])
def add_prescription(treat_id):
    if request.method == 'POST':
        #data from prescription form
        tests = request.form['tests']
        diet_plan = request.form['diet_plan']
        str_next_visit_date = request.form['next_visit_date']
        medicines_inputs = request.form.getlist('medicines_inputs[]')
        symptoms_inputs = request.form.getlist('symptoms_inputs[]')
        reports_inputs = request.form.getlist('reports_inputs[]')

        #get and update total prescription under a treatment
        doc_treatment = mongo.db.Treatment.find({ "treat_id": int(treat_id) })
        doc_treatment_list = list(doc_treatment)
        presc_id = doc_treatment_list[0].get('total_prescriptions')+1

        #update total prescriptions number under a treatment
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'total_prescriptions':presc_id }})
        
        #insert new prescription data
        mongo.db.Treatment.update({'treat_id' : int(treat_id) },{'$push':{"prescription" :{ 'pres_id' : presc_id , 'pres_doctor_userid' : current_user.username , 'time_stamp': datetime.now(), 'tests' : tests , 'diet_plan' : diet_plan, 'str_next_visit_date' : str_next_visit_date , 'medicines_inputs' : medicines_inputs , 'symptoms_inputs' : symptoms_inputs, 'reports_inputs' : reports_inputs }}})

    return redirect(url_for('doctor_routes.treatment_info', treat_id = treat_id))

@doctor_routes_bp.route('/close_treatment/<treat_id>')
def close_treatment(treat_id):
    #print(treat_id)
    doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) })
    Doctors_closed = doc_treatment['doctor_closed']
    Doctors_closed.append(current_user.username)
    #print(Doctors_closed)    

    
    alldoctors = doc_treatment['alldoctors']
    #print(alldoctors)
    alldoctors.remove(current_user.username)
    #print(alldoctors)

    mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'doctor_closed':Doctors_closed , 'alldoctors' : alldoctors}})
    #if all doctors have closed the treatment, shift doc to past treatments collection
    if len(alldoctors) == 0:
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{ 'treat_closed_on': datetime.now()}})
        doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) }) 
        mongo.db.Past_Treatments.insert(doc_treatment)
        mongo.db.Treatment.remove({ "treat_id": int(treat_id) })
    return redirect(url_for('doctor_routes.home_page'))

@doctor_routes_bp.route('/past_treatments')
def past_treatments():
    past_treatment = mongo.db.Past_Treatments.find( { 'alldoctors' : { '$in': [ current_user.username ] } })
    closed_treatment = mongo.db.Treatment.find( { 'doctor_closed' : { '$in': [ current_user.username ] } })
    
    return render_template('Doctor/doctor_sites/past_treatments.html', past_treatment = past_treatment, closed_treatment = closed_treatment)

@doctor_routes_bp.route('/doctor/past_treatment/<int:treat_id>/prescriptions')
def deleted_prescriptions(treat_id):
    treatment = mongo.db.Past_Treatments.find_one({"treat_id":treat_id})
    return render_template('Doctor/doctor_sites/past_prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)

@doctor_routes_bp.route('/doctor/past_treatment/<int:treat_id>/prescriptions')
def ongoing_deleted_prescriptions(treat_id):
    treatment = mongo.db.Treatment.find_one({"treat_id":int(treat_id)})
    if treatment['total_prescriptions'] == 0:
        print('no prescriptions')
        return redirect(url_for('doctor_routes.home_page'))
    else:
        return render_template('Doctor/doctor_sites/past_prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)

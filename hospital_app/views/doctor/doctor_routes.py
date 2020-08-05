from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
from hospital_app.models import User,Doctor
from hospital_app import db
import json
from flask_login import current_user
from hospital_app.forms import update_doctor_form
from hospital_app.models import Doctor
from datetime import date, datetime, timedelta
from collections import defaultdict

doctor_routes_bp = Blueprint('doctor_routes',__name__)

@doctor_routes_bp.route('/doctor')
def home_page():      
    return render_template('Doctor/home.html')


@doctor_routes_bp.route('/start_treatment', methods=['GET', 'POST'])
def start_treatment():      
    #user/patient data 
    users = User.query.filter_by(role='user').all()
    if request.method == 'POST':
            #data from start treatment form
            patient_userid = request.form['patient_userid']
            patient_name = request.form['patient_name']
            doctor_inputs = [current_user.username]
            doctor_closed = []
            #get total number of treatments from mongo and increment it by 1 and update it
            query_total_treat = { "Description": "Total number of treatments started" }
            doc_total_treat_cursor = mongo.db.Treatment.find(query_total_treat)
            doc_total_treat_list = list(doc_total_treat_cursor)
            
            bson_int64_treat_id = doc_total_treat_list[0].get('total_treatments')+1
            mongo.db.Treatment.update(query_total_treat,{"$set":{'total_treatments':bson_int64_treat_id}})
            
            #insert new treatment data
            mongo.db.Treatment.insert({'treat_id' : bson_int64_treat_id, 'patient_userid' : patient_userid, 'patient_name' : patient_name,'disease_name' : "", 'Referto' : "",'total_prescriptions' : 0,'time_stamp': datetime.now(), 'alldoctors':doctor_inputs, 'doctor_closed' : doctor_closed})
            
            return redirect(url_for('doctor_routes.current_treatment_list'))
        
    return render_template('Doctor/doctor_sites/Start_treatment.html', users = users)

@doctor_routes_bp.route('/current_treatment_list', methods=['GET', 'POST'])
def current_treatment_list():
    doc_treatment = mongo.db.Treatment.find( { 'alldoctors' : { '$in': [ current_user.username ] } }).sort([("time_stamp", -1)])
    return render_template('Doctor/doctor_sites/current_treatment_list.html',treatment=doc_treatment)

@doctor_routes_bp.route('/treatment_info/<treat_id>', methods=['GET', 'POST'])
def treatment_info(treat_id):

    doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) })
    total_prescriptions = doc_treatment['total_prescriptions']

    if total_prescriptions == 0 :
        return render_template('Doctor/doctor_sites/treatment_info.html', treatment=doc_treatment, treat_id = treat_id)
    else :
        return render_template('Doctor/doctor_sites/treatment_info.html', treatment=doc_treatment, treat_id = treat_id, prescriptions=doc_treatment["prescription"])

@doctor_routes_bp.route('/treatment_info/update_disease/<treat_id>', methods=['GET', 'POST'])
def update_disease(treat_id):
    if request.method == 'POST':    
        disease_name = request.form['disease_name']
        print(disease_name)
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{'disease_name':disease_name }})
    
    return redirect(url_for('doctor_routes.treatment_info', treat_id = treat_id))

@doctor_routes_bp.route('/treatment_info/add_doctor/<treat_id>', methods=['GET', 'POST'])
def add_doctor(treat_id):
    if request.method == 'POST':    
        alldoctors = request.form.getlist('doctor_inputs[]')

        print(alldoctors)

        doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) })
        Doctors = doc_treatment['alldoctors']

        print(type(Doctors))
        print(Doctors)
        print(type(alldoctors))
        print(type(alldoctors[0]))
        for doctor in alldoctors :
            Doctors.append(doctor)

        print(Doctors)
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{"alldoctors" : Doctors }})
    
    return redirect(url_for('doctor_routes.treatment_info', treat_id = treat_id))


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
    mongo.db.Treatment.update({'treat_id' : int(treat_id) },{'$push':{"Doctor_closed_time" :{ 'doct_id' : current_user.username,'time_stamp': datetime.now()}}})
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

@doctor_routes_bp.route('/doctor/past_treatment/<int:treat_id>/ongoing_prescriptions')
def ongoing_deleted_prescriptions(treat_id):
    print(treat_id)
    treatment = mongo.db.Treatment.find_one({"treat_id":int(treat_id)})
    print(treatment)
    return render_template('Doctor/doctor_sites/past_prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)

@doctor_routes_bp.route('/doctor/view_profile',methods = ['GET','POST'])
def view_profile():
    doctor = current_user.doctor
    return render_template('Doctor/doctor_sites/view_profile.html',doctor = doctor)

@doctor_routes_bp.route('/doctor/update_profile',methods = ['GET','POST'])
def update_profile():
    form = update_doctor_form(obj = current_user.doctor)
    if form.validate_on_submit():
        form.populate_obj(current_user.doctor)
        db.session.commit()
    return render_template('Doctor/doctor_sites/update_profile.html',form = form)


@doctor_routes_bp.route('/doctor/current_symptoms_stats',methods = ['GET','POST'])
def current_symptoms_stats():
    
    symp_stat = defaultdict(int) 
    dt = datetime.now() - timedelta(30)
    print('5 days before Current Date :',dt)
    print(type(dt))
    docs = mongo.db.Treatment.find({ 'prescription' : { '$elemMatch': {'time_stamp' : {'$gte': dt}}}})
    #print(list(docs[0]['prescription']))
    docs_past = mongo.db.Past_Treatments.find({ 'prescription' : { '$elemMatch': {'time_stamp' : {'$gte': dt }}}})        
    #print(list(docs[0]['prescription']))
    docs = list(docs) + list(docs_past)
    for treatment in docs:
        print(treatment)
        for prescription in treatment['prescription']:
            print(prescription['symptoms_inputs']) 
            for symptom in prescription['symptoms_inputs']:
                print(symptom)
                symp_stat[symptom] += 1
    
    print(symp_stat)
    
    label = []
    data = []

    for symptom , no_cases  in symp_stat.items():
        label.append(symptom)
        data.append(no_cases)

    return render_template('Doctor/doctor_sites/current_symptoms_stats.html', symp_stat = symp_stat, str_from_date = dt, str_to_date = datetime.now(), label = label, data = data)

@doctor_routes_bp.route('/doctor/symptoms_stats',methods = ['GET','POST'])
def symptoms_stats():
    if request.method == 'POST':
        str_from_date1 = request.form['from_date']
        str_to_date1 = request.form['to_date']

        str_from_date = str_from_date1 + " "+ "00:00:00.000000"
        str_to_date = str_to_date1 + " "+ "00:00:00.000000"

        print(str_from_date)
        print(type(str_from_date))

        from_date = datetime.strptime(str_from_date, '%Y-%m-%d %H:%M:%S.%f') 
        print(from_date)
        print(type(from_date))

        to_date = datetime.strptime(str_to_date, '%Y-%m-%d %H:%M:%S.%f') 
        print(to_date)
        print(type(to_date))             

        symp_stat = defaultdict(int) 
        dt = datetime.now() - timedelta(30)
        print('5 days before Current Date :',dt)
        print(type(dt))
        docs = mongo.db.Treatment.find({ 'prescription' : { '$elemMatch': {'time_stamp' : {'$gte': from_date , '$lt': to_date }}}})
        docs_past = mongo.db.Past_Treatments.find({ 'prescription' : { '$elemMatch': {'time_stamp' : {'$gte': from_date , '$lt': to_date }}}})        
        #print(list(docs[0]['prescription']))
        docs = list(docs) + list(docs_past)
        for treatment in docs:
            print(treatment)
            for prescription in treatment['prescription']:
                print(prescription['symptoms_inputs']) 
                for symptom in prescription['symptoms_inputs']:
                    print(symptom)
                    symp_stat[symptom] += 1
    
        print(symp_stat)
        sort_symp_stat = sorted(symp_stat.items(), key=lambda x: x[1], reverse=True)
        print(sort_symp_stat)
        return render_template('Doctor/doctor_sites/symptoms_stat.html', symp_stat = sort_symp_stat, str_from_date = str_from_date1, str_to_date = str_to_date1)

    symp_stat = {}
    str_from_date = '___'
    str_to_date = '___'
    return render_template('Doctor/doctor_sites/symptoms_stat.html', symp_stat = symp_stat, str_from_date = str_from_date, str_to_date = str_to_date)

@doctor_routes_bp.route('/doctor/query',methods = ['GET','POST'])
def query():
    if request.method == 'POST':    
        symptoms_inputs = request.form.getlist('symptoms_inputs[]')
        print(symptoms_inputs)
        docs = mongo.db.Past_Treatments.find({ 'prescription' :{ '$elemMatch': {  'symptoms_inputs':{ '$all': symptoms_inputs }}}})
        predocs = mongo.db.Treatment.find({ 'prescription' :{ '$elemMatch': {  'symptoms_inputs':{ '$all': symptoms_inputs }}}})
        return render_template('Doctor/doctor_sites/query.html', docs = docs, predocs = predocs)
    return render_template('Doctor/doctor_sites/query.html')    
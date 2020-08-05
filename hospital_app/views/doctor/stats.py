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

stats_bp = Blueprint('stats',__name__, url_prefix='/doctor')

@stats_bp.route('/symptoms-stats',methods = ['GET','POST'])
def symptoms_stats():
    if request.method == 'POST':
        str_date_range = request.form['daterange']
        list_date_range = str_date_range.split() 
        str_from_date = list_date_range[0] + " "+ "00:00:00.000000"
        str_to_date = list_date_range[2] + " "+ "00:00:00.000000"

        from_date = datetime.strptime(str_from_date, '%m/%d/%Y %H:%M:%S.%f') 
        print(from_date)
        print(type(from_date))

        to_date = datetime.strptime(str_to_date, '%m/%d/%Y %H:%M:%S.%f') 
        print(to_date)
        print(type(to_date))             
        symp_stat = defaultdict(int)
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
        return render_template('Doctor/doctor_sites/current_symptoms_stats.html', symp_stat = symp_stat)

    return render_template('Doctor/doctor_sites/current_symptoms_stats.html')


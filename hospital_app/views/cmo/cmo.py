from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
from hospital_app.models import User,Doctor , patient_queue
from hospital_app import db
import json
from flask_login import current_user
from hospital_app.forms import update_doctor_form
from hospital_app.models import Doctor
from datetime import date, datetime, timedelta
from collections import defaultdict

cmo_bp = Blueprint('cmo',__name__)

@cmo_bp.route('/cmo')
def home_page():      
    return render_template('CMO/home.html')

@cmo_bp.route('/cmo_acitve_treatment', methods=['GET', 'POST'])
def active_treatment():
    doc_treatment = mongo.db.Treatment.find({ 'treat_id': { '$ne': 0 } }).sort([("time_stamp", -1)])
    return render_template('CMO/sites/treatment.html',treatment=doc_treatment, Status = 'Active')

@cmo_bp.route('/cmo_closed_treatment', methods=['GET', 'POST'])
def closed_treatment():
    doc_treatment = mongo.db.Past_Treatments.find().sort([("time_stamp", -1)])
    return render_template('CMO/sites/treatment.html',treatment=doc_treatment, Status = 'Closed')

@cmo_bp.route('/cmo_all_treatment', methods=['GET', 'POST'])
def all_treatment():
    doc_treatment = mongo.db.Past_Treatments.find().sort([("time_stamp", -1)])

    doc_treatment = mongo.db['Past_Treatments'].aggregate( 
    [
        # this code is used to take the union of past_treatments table and treatment table
        { '$limit': 1 },
        { '$project': { '_id': '$$REMOVE' } },

        { '$lookup': { 'from': 'Past_Treatments','localField':'null','foreignField':'null', 'as': 'Past_Treatment' } },
        { '$lookup': { 'from': 'Treatment', 'localField':'null','foreignField':'null', 'as': 'treatment' } },

        { '$project': { 'union': { '$concatArrays': ["$Past_Treatment", "$treatment"] } } },

        { '$unwind': '$union' },
        { '$replaceRoot': { 'newRoot': '$union' } },
        {
            '$match': 
            { 
                'treat_id': {'$ne': 0}
            }
       },
  
        # upto here
        # sorted in the descending order of count
        {
            '$sort' : { 'count': -1 }
        }
    ]
    )

    print(type(doc_treatment))
    return render_template('CMO/sites/treatment.html',treatment=doc_treatment, Status = 'All')

@cmo_bp.route('/cmo-prescription-history/<treat_id>')
def prescription_history(treat_id):
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) }) 
    if treatment == None :
        treatment = mongo.db.Past_Treatments.find_one({'treat_id' : int(treat_id) })
    if treatment == None :
        return "This Treatment does not exist"
    prescriptions = reversed(treatment['prescription'])
    return render_template('CMO/sites/prescription.html', prescriptions = prescriptions)

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
from operator import itemgetter 
from _datetime import datetime
import datetime
  
stats_bp = Blueprint('stats',__name__)

@stats_bp.route('/symptoms-stats',methods = ['GET','POST'])
def symptoms_stats():
    if request.method == 'POST':
        str_date_range = request.form['daterange']
        list_date_range = str_date_range.split() 
        str_from_date = list_date_range[0] + " "+ "00:00:00.000000"
        str_to_date = list_date_range[2] + " "+ "00:00:00.000000"

        from_date = datetime.datetime.strptime(str_from_date, '%m/%d/%Y %H:%M:%S.%f') 
        print(from_date)
        print(type(from_date))

        to_date = datetime.datetime.strptime(str_to_date, '%m/%d/%Y %H:%M:%S.%f') 
        print(to_date)
        print(type(to_date))             
        symp_stat = defaultdict(int)
        docs = mongo.db.Treatment.find({ 'prescription' : { '$elemMatch': {'timestamp' : {'$gte': from_date , '$lt': to_date }}}})
        docs_past = mongo.db.Past_Treatments.find({ 'prescription' : { '$elemMatch': {'timestamp' : {'$gte': from_date , '$lt': to_date }}}})        
        #print(list(docs[0]['prescription']))
        docs = list(docs) + list(docs_past)
        for treatment in docs:
            print(treatment)
            for prescription in treatment['prescription']:
                for symptom in prescription['symptoms']:
                    symp_stat[symptom] += 1
    
        print(symp_stat)
        symp_table_data = dict(sorted(symp_stat.items(), key = itemgetter(1), reverse = True))
        symp_stat = dict(sorted(symp_stat.items(), key = itemgetter(1), reverse = True)[0:10])
        print(symp_stat)
        return render_template('CMO/sites/Stats/current_symptoms_stats.html', symp_stat = symp_stat, symp_table_data = symp_table_data)

    symp_stat = defaultdict(int) 
    return render_template('CMO/sites/Stats/current_symptoms_stats.html', symp_stat = symp_stat)









@stats_bp.route('/disease-stats',defaults = {'year':None})
@stats_bp.route('/disease-stats/<int:year>', methods = ['GET','POST'])
def disease_stats(year):
    now = datetime.datetime.now()
    current_year = now.year

    if year:
        d = year
    else:
        d = current_year    


    
    collection = mongo.db['Past_Treatments'].aggregate( 
    [
        # this code is used to take the union of past_treatments table and treatment table
        { '$limit': 1 },
        { '$project': { '_id': '$$REMOVE' } },

        { '$lookup': { 'from': 'Past_Treatments','localField':'null','foreignField':'null', 'as': 'Past_Treatment' } },
        { '$lookup': { 'from': 'Treatment', 'localField':'null','foreignField':'null', 'as': 'treatment' } },

        { '$project': { 'union': { '$concatArrays': ["$Past_Treatment", "$treatment"] } } },

        { '$unwind': '$union' },
        { '$replaceRoot': { 'newRoot': '$union' } },

        # upto here

        # using project im taking only the two columns and that are : disease name and year.

        {
            '$project': {'disease_name':1,'year':{'$year':"$time_stamp"} }
        },

        # putting a condition on year.
        {
            '$match' : { 'year':d }
        },

        # grouped using disease name and counted the treatments having the same disease name
        {
            '$group' : {
                         '_id' : "$disease_name" ,
                        'count': { '$sum': 1 }
                        }
        },

        # sorted in the descending order of count
        {
            '$sort' : { 'count': -1 }
        }
    ]
    )
   

    labels = []
    values = []
    i = 0
    for row in collection:
        if (i<15):
            labels.append(row['_id'])
            values.append(row['count'])
            i = i+ 1
        else:
            break    

    print(labels)
    print(values)
    return render_template('CMO/sites/Stats/diseases.html',title = "Disease Statistics", max = 10, values = values, labels= labels, year = current_year)
    

@stats_bp.route('/treatment-stats',defaults = {'year':None})
@stats_bp.route('/treatment-stats/<int:year>', methods = ['GET','POST'])
def treatment_stats(year):
    now = datetime.datetime.now()
    current_year = now.year

    if year:
        d = year
    else:
        d = current_year    


    
    collection = mongo.db['Past_Treatments'].aggregate( 
    [
        { '$limit': 1 },
        { '$project': { '_id': '$$REMOVE' } },

        { '$lookup': { 'from': 'Past_Treatments','localField':'null','foreignField':'null', 'as': 'Past_Treatment' } },
        { '$lookup': { 'from': 'Treatment', 'localField':'null','foreignField':'null', 'as': 'freelancers' } },

        { '$project': { 'union': { '$concatArrays': ["$Past_Treatment", "$freelancers"] } } },

        { '$unwind': '$union' },
        { '$replaceRoot': { 'newRoot': '$union' } },

        {
            '$project': {'month':{'$month':"$time_stamp"},'year':{'$year':"$time_stamp"} }
        },

    
        {
            '$match' : { 'year':d }
        },

        {
            '$group' : {
                         '_id' : "$month" ,
                        'count': { '$sum': 1 }
                        }
        },

        {
            '$sort' : { 'month': 1 }
        }
    ]
    )
   

    labels = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    values = [0]*12
    i = 0
    for row in collection:
         values[row['_id']] = row['count']

    print(labels)
    print(values)
    return render_template('CMO/sites/Stats/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year)

def numberOfDays(y, m):
      leap = 0
      if y% 400 == 0:
         leap = 1
      elif y % 100 == 0:
         leap = 0
      elif y% 4 == 0:
         leap = 1
      if m==2:
         return 28 + leap
      list = [1,3,5,7,8,10,12]
      if m in list:
         return 31
      return 30 


@stats_bp.route('/particular_disease-stats',methods = ['GET','POST'])
def particular_disease():

    now = datetime.datetime.now()
    current_year = now.year

    form = disease_statistic_form() 

    if form.validate_on_submit():
        disease_name = form.disease_name.data
        month = form.month.data
        year = form.year.data

        if month == "ALL":
            collection = mongo.db['Past_Treatments'].aggregate([
            { '$limit': 1 },
            { '$project': { '_id': '$$REMOVE' } },

            { '$lookup': { 'from': 'Past_Treatments','localField':'null','foreignField':'null', 'as': 'Past_Treatment' } },
            { '$lookup': { 'from': 'Treatment', 'localField':'null','foreignField':'null', 'as': 'freelancers' } },

            { '$project': { 'union': { '$concatArrays': ["$Past_Treatment", "$freelancers"] } } },

            { '$unwind': '$union' },
            { '$replaceRoot': { 'newRoot': '$union' } },

            {
                '$project': {'disease_name':1, 'month':{'$month':"$time_stamp"},'year':{'$year':"$time_stamp"} }
            },

        
            {
                '$match' :  {'$and': [{ 'year':year }, {'disease_name':disease_name}]} 
            },

            {
                '$group' : {
                            '_id' : "$month" ,
                            'count': { '$sum': 1 }
                            }
            },

            {
                '$sort' : { 'month': 1 }
            }
            ])
        

            labels = ["January","February","March","April","May","June","July","August","September","October","November","December"]
            values = [0]*12
            i = 0
            for row in collection:
                values[row['_id']] = row['count']

            print(labels)
            print(values)
            return render_template('CMO/sites/Stats/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year,form = form)
            

        else :
            collection = mongo.db['Past_Treatments'].aggregate([
                { '$limit': 1 },
                { '$project': { '_id': '$$REMOVE' } },

                { '$lookup': { 'from': 'Past_Treatments','localField':'null','foreignField':'null', 'as': 'Past_Treatment' } },
                { '$lookup': { 'from': 'Treatment', 'localField':'null','foreignField':'null', 'as': 'freelancers' } },

                { '$project': { 'union': { '$concatArrays': ["$Past_Treatment", "$freelancers"] } } },

                { '$unwind': '$union' },
                { '$replaceRoot': { 'newRoot': '$union' } },

                {
                    '$project': {'disease_name':1, 'month':{'$month':"$time_stamp"},'year':{'$year':"$time_stamp"}, 'date':{'$date':"$time_stamp"}}
                },

            
                {
                    '$match' :  {'$and': [{ 'year':year }, {'disease_name':disease_name}, {'month':month}]} 
                },

                {
                    '$group' : {
                                '_id' : "$date" ,
                                'count': { '$sum': 1 }
                                }
                },

                {
                    '$sort' : { 'date': 1 }
                }
            ]
            )

            num_days = numberOfDays(year, month)
            values = [0]*num_days
            labels = []

            for i in range(1,num_days+1):
                labels.append[i]


            for row in collection:
                values[row['_id']] = row['count']

            print(labels)
            print(values)
            return render_template('CMO/sites/Stats/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year,form = form)
                
    else:
        labels = []
        values = []
        return render_template('CMO/sites/Stats/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year,form = form)

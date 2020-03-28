# from flask import Blueprint, render_template, redirect,url_for, request, flash
# from hospital_app import mongo
# import json
# doctor_routes_bp = Blueprint('doctor_routes',__name__)

# @doctor_routes_bp.route('/doctor')
# def doctor():       #pass user_id as parameter
#     return render_template('Doctor/home.html')

# @doctor_routes_bp.route('/start_treatment', methods=['GET', 'POST'])
# def start_treatment():       #pass user_id as parameter
    
#     if request.method == 'POST':
#             x =  { "name":"John", "age":30, "city":"New York"}
#             #mongo.db.Treatment.insert({'Disease name' : request.form['Disease'], 'Doctors involved' : request.form['Doctor']})
#             mongo.db.Treatment.insert(x)
#             return redirect(url_for('doctor_routes.doctor'))
        
#     return render_template('Doctor/Start_treatment.html')
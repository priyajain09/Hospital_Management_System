from hospital_app.models import User,Doctor
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import db
from hospital_app import mongo
import json
from flask_login import current_user
from hospital_app import user_collection
from hospital_app.forms import search_doctor_form
from hospital_app.models import Doctor

user_bp = Blueprint('user', __name__)
@user_bp.route('/user/home_page')
def home_page():
    return render_template('User/home_page.html')

@user_bp.route('/user/current_treatments')
def current_treatments():
    treatment = mongo.db.Treatment.find({"patient_userid":"pj234"})
    return render_template('User/user_sites/current_treatments.html',treatment=treatment)

@user_bp.route('/user/treatment/prescriptions')
def prescriptions():
    treatment = mongo.db.Treatment.find_one()
    return render_template('User/user_sites/prescriptions.html',prescriptions=treatment["prescription"])

@user_bp.route('/user/doctor',methods = ['GET','POST'])
def doctor():
    d = Doctor.query.all()
    form = search_doctor_form()
    if form.validate_on_submit():
        # return str(form.specialization.data)
        d = Doctor.query.filter_by(specialization = str(form.specialization.data)).all()
        return render_template('User/user_sites/list_of_doctors.html',q=d,form=form)
    return render_template('User/user_sites/list_of_doctors.html',q=d,form=form)
        


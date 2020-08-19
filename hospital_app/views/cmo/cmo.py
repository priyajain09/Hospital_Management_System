from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
from hospital_app.models import User,Doctor , user_role, past_user_role,patient_queue, user_role, specialization, Patient, deleted_doctors,deleted_patients,is_user_deleted, temporary_users,temporary_role_users
from hospital_app import db
import json
from flask_login import current_user
from hospital_app.forms import update_doctor_form , change_password_form
from hospital_app.models import Doctor
from datetime import date, datetime, timedelta
from collections import defaultdict
from io import BytesIO
import base64

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
            '$sort' : { 'time_stamp': -1 }
        }
    ]
    )

    print(type(doc_treatment))
    print(doc_treatment)
    return render_template('CMO/sites/treatment.html',treatment=doc_treatment, Status = 'All')

@cmo_bp.route('/cmo-prescription-history/<treat_id>')
def prescription_history(treat_id):
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) }) 
    if treatment == None :
        treatment = mongo.db.Past_Treatments.find_one({'treat_id' : int(treat_id) })
    if treatment == None :
        return "This Treatment does not exist"
    prescriptions = reversed(treatment['prescription'])
    return render_template('CMO/sites/prescription.html', prescriptions = prescriptions, treatment = treatment)

@cmo_bp.route('/cmo-view_profile',methods = ['GET','POST'])
def view_profile():
    cmo = user_role.query.filter_by(role = "chief_doctor").first()
    print(cmo)
    image = base64.b64encode(cmo.File).decode('ascii')
    return render_template('CMO/sites/view_profile.html',user = cmo,image = image)

@cmo_bp.route('/cmo-update_profile',methods = ['GET','POST'])
def update_profile():
    if request.method == "POST":
        file = request.files['profile_photo']

        u = user_role.query.filter_by(role = "chief_doctor").first()

        if file and file.filename != "":
            u.File = file.read()

        u.name = request.form['name']
        u.age = request.form['age']
        u.address = request.form['address']
        u.contact_number = request.form['contact_number']
        u.gender = request.form['gender']
        u.work_timings = request.form['work_timings']

        try:
            db.session.commit()
            flash("Updated successfully!")
        except:
            db.session.rollback()
            flash("Try Again!")    
    u = user_role.query.filter_by(role = "chief_doctor").first()
    image = base64.b64encode(u.File).decode('ascii')         
    return render_template('CMO/sites/update_profile.html',user = u,image = image)

@cmo_bp.route('/cmo-change_password',methods = ['GET','POST'])
def change_password():
    form = change_password_form()
    if form.validate_on_submit():
        
        current_user.set_password(form.password.data)
        try:
            db.session.commit()
            flash("Updated successfully")
        except:
            db.session.rollback()
            flash("Try Again")

    return render_template('CMO/sites/change_password.html',form = form)

# *********************************************************************************
##### View Deleted Hosptial staff and there details

# View Users and Doctors
# here users are used to denote patients
@cmo_bp.route('/cmo-doctor_list',methods = ['GET','POST'])
def doctor_list():
    q = db.session.query(User,Doctor).join(Doctor).all()
    return render_template('CMO/sites/list_of_doctors.html',q=q)

@cmo_bp.route('/cmo-user_list',methods = ['GET','POST'])
def user_list():
    users = db.session.query(User,Patient).join(Patient).filter(User.role == "user")
    return render_template('CMO/sites/list_of_users.html',list=users)

@cmo_bp.route('/cmo-users/<username>/<email>')
def user_details(username,email):
    q = Patient.query.filter_by(username = username).first()
    image = base64.b64encode(q.File).decode('ascii')
    return render_template('CMO/sites/user_details.html',user=q,email = email,image = image)

@cmo_bp.route('/cmo-doctor_details/<username>')
def doctor_details(username):
    q = Doctor.query.filter_by(username = username).first()
    image = base64.b64encode(q.File).decode('ascii')
    return render_template('CMO/sites/doctor_details.html',row=q,image = image)


@cmo_bp.route('/cmo-deleted_users',methods=['GET','POST'])
def deleted_users(): 
    u = deleted_patients.query.all()
    return render_template('CMO/sites/deleted_users.html',users = u)

@cmo_bp.route('/cmo-patient_details/<username>')
def deleted_user_details(username):
    u = deleted_patients.query.get(username)
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('CMO/sites/deleted_user_details.html',user = u,image = image)

@cmo_bp.route('/cmo-deleted_doctor_details/<username>')
def deleted_doctor_details(username):
    u = deleted_doctors.query.get(username)
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('CMO/sites/deleted_doctor_details.html',row = u,image = image)

@cmo_bp.route('/cmo-deleted_doctors',methods=['GET','POST'])
def deleted_doctors_func():
    u = deleted_doctors.query.all()
    return render_template('CMO/sites/deleted_doctors.html',doctors = u)

# View assisstant

@cmo_bp.route('/cmo-current_assistant/<username>')
def current_assistant(username):
    u = user_role.query.filter_by(role = "assistant",doctor_username = username).first()
    if u is not None:
        image = base64.b64encode(u.File).decode('ascii')
        return render_template('CMO/sites/current_assistants.html',row = u,username = username,image = image)
    else:
        flash("Assistant is not assigned")
        return render_template('CMO/sites/current_assistants.html',row = u,username = username)

@cmo_bp.route('/cmo-past_assistants/<username>')
def past_assistant(username):
    u = past_user_role.query.filter_by(role = "assistant", doctor_username = username).all()
    images = []
    for i in u:
        images.append(base64.b64encode(i.File).decode('ascii'))
    if len(u) == 0:
        flash("No past assistants")
    return render_template('CMO/sites/past_assistants.html',users = u,username = username,images = images)

# View role users , compunder, receptionist

@cmo_bp.route('/cmo-role_user/<role>')
def role_user(role):
     u = user_role.query.filter_by(role = role).first()
     if u:
        image = base64.b64encode(u.File).decode('ascii')
        past_role_users = past_user_role.query.filter_by(role = role).all()
        return render_template('CMO/sites/role_user_page.html',row = u, past_users = past_role_users,role = role,image = image)
     past_role_users = past_user_role.query.filter_by(role = role).all()
     return render_template('CMO/sites/role_user_page.html',row = u, past_users = past_role_users,role = role)    

@cmo_bp.route('/cmo-deleted_role_user_details/<id>')
def deleted_role_user_details(id):
    u = past_user_role.query.get(id)
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('CMO/sites/deleted_role_user.html',row = u,image = image)

######################################################
####### View Departments 

@cmo_bp.route('/cmo-departments', methods = ['GET','POST'])
def departments():
    q = specialization.query.all()    
    return render_template('CMO/sites/departments.html', q=q)


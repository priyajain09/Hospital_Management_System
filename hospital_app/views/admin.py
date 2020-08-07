from hospital_app.models import User,Doctor,specialization, Patient, deleted_doctors,deleted_patients,is_user_deleted, temporary_users,temporary_role_users
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm, specialization_form, search_user,search_doctor_form,disease_statistic_form
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app import db,mongo
from _datetime import datetime
from hospital_app.email import send_request_accepted_mail, send_request_rejected_mail
import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/home_page')
def home_page():
    return render_template('Admin/home_page.html')

@admin_bp.route('/admin/doctor_list',methods = ['GET','POST'])
def doctor_list():
    form = search_doctor_form()
    if form.validate_on_submit():
        doctors = db.session.query(User,Doctor).join(Doctor).filter(Doctor.specialization == str(form.specialization.data)).all()
        if len(doctors) == 0:
            flash("No Doctors")
        return render_template('Admin/admin_sites/list_of_doctors.html',q=doctors,form = form)
    q = db.session.query(User,Doctor).join(Doctor).all()
    if len(q) == 0:
            flash("No Doctors")
    return render_template('Admin/admin_sites/list_of_doctors.html',q=q,form = form)

@admin_bp.route('/admin/user_list',methods = ['GET','POST'])
def user_list():
    form = search_user()
    if form.validate_on_submit():
        user = User.query.filter_by(role='user',username = form.username.data).all()
        if len(user) ==  0:
            flash('User does not exist with the given username!')
        return render_template('Admin/admin_sites/list_of_users.html',q = user,form=form)    
    q = User.query.filter_by(role='user').all()
    if len(q) == 0:
        flash('No users')
    return render_template('Admin/admin_sites/list_of_users.html',q=q,form= form)


@admin_bp.route('/admin/registration_request/<username>')
def action_reg_request(username):
    q = temporary_users.query.get(username)
    return render_template('Admin/admin_sites/registration_request_action.html',row=q)

@admin_bp.route('/admin/<username>/<action>')
def action_taken_on_request(username,action):
    if action == "Reject":
        # due to cascading its corresponding entry from doctor table gets deleted automatically.
        x = temporary_users.query.get(username) 
        db.session.delete(x) 
        db.session.commit()
        send_request_rejected_mail(x)
    elif action == "Accept":
        user = temporary_users.query.get(username)
        u = User(username = user.username, email = user.email, password_hash = user.password_hash, 
        role = 'doctor')
        y = Doctor(username = user.username, name = user.name, qualification = user.qualification, experience = user.experience
        , specialization = user.specialization, timestamp = user.timestamp, contact_number = user.contact_number)
        db.session.delete(user) 
        db.session.commit()
        db.session.add(u)
        db.session.commit()
        db.session.add(y)
        db.session.commit()
        # send_request_accepted_mail(y)
    return redirect(url_for('admin.registration_request'))   



@admin_bp.route('/admin/registration_requests')
def registration_request():
    q = temporary_users.query.filter_by(role='doctor').all()
    if len(q) == 0:
        flash("No pending requests")
    return render_template('Admin/admin_sites/registration_request.html',q=q)

@admin_bp.route('/admin/departments', methods = ['GET','POST'])
def departments():
    form = specialization_form()
    if form.validate_on_submit():
        spez = specialization(specialization = form.specialization_name.data)
        db.session.add(spez)
        db.session.commit()
    q = specialization.query.all()    
    return render_template('Admin/admin_sites/departments.html', q=q, form = form)


@admin_bp.route('/admin/users/<username>')
def user_details(username):
    q = Patient.query.filter_by(username = username).first()
    return render_template('Admin/admin_sites/user_details.html',user=q)

# ******************************************************************************
# To be done later: move ongoing treatments to closed treatments and send an email for the same
# here user is used to denote patient
@admin_bp.route('/admin/delete_user/<username>')
def delete_user(username):
    # before deleting patient populate deleted_patients table
    user = User.query.get(username)
    patient = user.patient
    u = deleted_patients(username = user.username,email=user.email,name= patient.name,age = patient.age,blood_group = patient.blood_group,contact_number = patient.contact_number,address = patient.address,gender_user = patient.gender_user)
    x = is_user_deleted.query.get(user.username)
    x.is_deleted = True
    db.session.add(u)
    db.session.commit()
    q = User.query.get(username)
    if q is not None:
        db.session.delete(q)
        db.session.commit()
    return redirect(url_for('admin.user_list'))

# ********************************************************************************

@admin_bp.route('/admin/doctor_details/<username>')
def doctor_details(username):
    q = Doctor.query.filter_by(username = username).first()
    return render_template('Admin/admin_sites/doctor_details.html',doctor=q)


# **********************************************************************************
# To be done later: Check if the doctor is involved in ongoing treatments or not and send email to him
@admin_bp.route('/admin/delete_doctor/<username>')
def delete_doctor(username):
    user = User.query.get(username)
    doctor = user.doctor
    u = deleted_doctors(username = str(user.username),email=user.email,name=doctor.name,gender_doctor=doctor.gender_doctor,
    age=doctor.age,blood_group=doctor.blood_group,contact_number=doctor.contact_number,address=doctor.address,qualification=doctor.qualification,
    experience=doctor.experience,specialization=doctor.specialization,date_of_joining=doctor.date_of_joining)
    x = is_user_deleted.query.get(username)
    x.is_deleted = True
    db.session.add(u)
    db.session.commit()
    q = User.query.get(username)
    if q is not None:
        db.session.delete(q)
        db.session.commit()
    return redirect(url_for('admin.doctor_list'))

# *********************************************************************************

# here users are used to denote patients
@admin_bp.route('/admin/deleted_users',methods=['GET','POST'])
def deleted_users():
    form = search_user()
    if form.validate_on_submit():
        user = deleted_users.query.filter_by(username = form.username.data).all()
        if len(user) ==  0:
            flash('User does not exist with the given username!')
        return render_template('Admin/admin_sites/deleted_users.html',users = user,form=form)    
    u = deleted_patients.query.all()
    if len(u)==0:
        flash("No deleted users")
    return render_template('Admin/admin_sites/deleted_users.html',users = u,form=form)


@admin_bp.route('/admin/deleted_doctors',methods=['GET','POST'])
def deleted_doctors_func():
    form = search_doctor_form()
    if form.validate_on_submit():
        doctors = deleted_doctors.query.filter_by(specialization=str(form.specialization.data)).all()
        if len(doctors) == 0:
            flash("No Doctors")
        return render_template('Admin/admin_sites/deleted_doctors.html',doctors=doctors,form = form)
    u = deleted_doctors.query.all()
    if len(u)==0:
        flash("No deleted doctors")
    return render_template('Admin/admin_sites/deleted_doctors.html',doctors = u,form = form)

@admin_bp.route('/admin/assistant_registration_requests/<role>')
def assistant_registration_requests(role):
    u = temporary_role_users.query.filter_by(role = role).all()
    if (len(u) == 0):
        flash("No pending requests")

    if role == "assistant":    
        return render_template('Admin/admin_sites/assistant_requests.html',list = u)   
    elif role =="compounder":
        return render_template('Admin/admin_sites/compounder_requests.html',list = u)  
    elif role == "reception":
        return render_template('Admin/admin_sites/reception_requests.html',list = u)  
        
@admin_bp.route('/admin/assistant_registration_requests/<username>/<action>/<role>')
def action_role_reg(username,action,role):

    if action == "Accept":
        user = temporary_role_users.query.filter_by(username=username).first()
        if user is not None:
            u = User(username = user.username, email = user.email, role = user.role, password_hash = user.password)
            db.session.add(u)
            db.session.commit()
            u = user_role(username = user.username, name = user.name,role = user.role, birthdate = user.birthdate,age = user.age,
            contact_number = user.contact_number, address = user.address, gender = user.gender, work_timings = user.work_timings,
            timestamp = user.timestamp, doctor_username = user.doctor_username,date_of_joining = datetime.datetime.now())
            db.session.add(u)
            db.session.commit()
            
    elif action == "Reject":
        user = temporary_role_users.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
    return  redirect(url_for('admin.assistant_registration_requests',role=role))
# *******************************************************************************************************

# Statistics
@admin_bp.route('/admin/statistics')
def stats():
    return render_template('/Admin/admin_sites/statistics.html')




@admin_bp.route('/admin/statistics/diseases',defaults = {'year':None})
@admin_bp.route('/admin/statistics/diseases/<int:year>', methods = ['GET','POST'])
def diseases_statistics(year):
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
    return render_template('Admin/admin_sites/statistics/diseases.html',title = "Disease Statistics", max = 10, values = values, labels= labels, year = current_year)
    

@admin_bp.route('/admin/statistics/treatments',defaults = {'year':None})
@admin_bp.route('/admin/statistics/treatments/<int:year>', methods = ['GET','POST'])
def treatments_statistics(year):
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
    return render_template('Admin/admin_sites/statistics/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year)

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


@admin_bp.route('/admin/statistics/particular_disease',methods = ['GET','POST'])
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
            return render_template('Admin/admin_sites/statistics/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year,form = form)
            

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
            return render_template('Admin/admin_sites/statistics/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year,form = form)
                
    else:
        labels = []
        values = []
        return render_template('Admin/admin_sites/statistics/diseases.html',title = "Treatments Statistics", max = 10, values = values, labels= labels, year = current_year,form = form)

        
        





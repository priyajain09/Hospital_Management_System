from hospital_app.models import User,Doctor,specialization, Patient, deleted_doctors,deleted_patients,is_user_deleted, temporary_users,temporary_role_users
from hospital_app.models import user_role, past_user_role
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm, specialization_form, search_user,search_doctor_form,disease_statistic_form
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app import db,mongo
from _datetime import datetime
from hospital_app.email import send_request_accepted_mail, send_request_rejected_mail
import datetime
from flask_login import current_user, login_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/home_page')
@login_required
def home_page():
    return render_template('Admin/home_page.html')

@admin_bp.route('/admin/doctor_list',methods = ['GET','POST'])
@login_required
def doctor_list():
    q = db.session.query(User,Doctor).join(Doctor).all()
    return render_template('Admin/admin_sites/list_of_doctors.html',q=q)

@admin_bp.route('/admin/user_list',methods = ['GET','POST'])
def user_list():
    users = db.session.query(User,Patient).join(Patient).filter(User.role == "user")
    return render_template('Admin/admin_sites/list_of_users.html',list=users)


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
    len_doctor = len(q)
    len_assistant = len(temporary_role_users.query.filter_by(role = "assistant").all())
    len_recep = len(temporary_role_users.query.filter_by(role = "reception").all())
    len_comp = len(temporary_role_users.query.filter_by(role = "compounder").all())
    len_chief = len(temporary_role_users.query.filter_by(role = "chief_doctor").all())
    return render_template('Admin/admin_sites/registration_request.html',q=q,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief)

@admin_bp.route('/admin/departments', methods = ['GET','POST'])
def departments():
    form = specialization_form()
    if form.validate_on_submit():
        spez = specialization(specialization = form.specialization_name.data)
        db.session.add(spez)
        db.session.commit()
    q = specialization.query.all()    
    return render_template('Admin/admin_sites/departments.html', q=q, form = form)


@admin_bp.route('/admin/users/<username>/<email>')
def user_details(username,email):
    q = Patient.query.filter_by(username = username).first()
    return render_template('Admin/admin_sites/user_details.html',user=q,email = email)

# ******************************************************************************
# To be done later: move ongoing treatments to closed treatments and send an email for the same
# here user is used to denote patient
@admin_bp.route('/admin/delete_user/<username>')
def delete_user(username):
    # before deleting patient populate deleted_patients table
    user = User.query.get(username)
    patient = user.patient
    u = deleted_patients(username = user.username,email=user.email,name= patient.name,age = patient.age,blood_group = patient.blood_group,
    contact_number = patient.contact_number,address = patient.address,gender_user = patient.gender_user,joined_on = patient.timestamp)
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
    return render_template('Admin/admin_sites/doctor_details.html',row=q)


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
    u = deleted_patients.query.all()
    return render_template('Admin/admin_sites/deleted_users.html',users = u)

@admin_bp.route('/admin/patient_details/<username>')
def deleted_user_details(username):
    u = deleted_patients.query.get(username)
    return render_template('Admin/admin_sites/deleted_user_details.html',user = u)

@admin_bp.route('/admin/deleted_doctor_details/<username>')
def deleted_doctor_details(username):
    u = deleted_doctors.query.get(username)
    return render_template('Admin/admin_sites/deleted_doctor_details.html',row = u)



@admin_bp.route('/admin/deleted_doctors',methods=['GET','POST'])
def deleted_doctors_func():
    u = deleted_doctors.query.all()
    return render_template('Admin/admin_sites/deleted_doctors.html',doctors = u)

@admin_bp.route('/admin/assistant_registration_requests/<role>')
def assistant_registration_requests(role):
    u = temporary_role_users.query.filter_by(role = role).all()
    if (len(u) == 0):
        flash("No pending requests")

    if role == "assistant":
        len_assistant = len(u)
        len_doctor = len(temporary_users.query.filter_by(role='doctor').all())
        len_recep = len(temporary_role_users.query.filter_by(role = "reception").all())
        len_comp = len(temporary_role_users.query.filter_by(role = "compounder").all())
        len_chief = len(temporary_role_users.query.filter_by(role = "chief_doctor").all())   
    elif role == "reception":
        len_recep = len(u)
        len_doctor = len(temporary_users.query.filter_by(role='doctor').all())
        len_assistant = len(temporary_role_users.query.filter_by(role = "assistant").all())
        len_comp = len(temporary_role_users.query.filter_by(role = "compounder").all())
        len_chief = len(temporary_role_users.query.filter_by(role = "chief_doctor").all())  
    elif role == "compounder":
        len_comp = len(u)
        len_doctor = len(temporary_users.query.filter_by(role='doctor').all())
        len_assistant = len(temporary_role_users.query.filter_by(role = "assistant").all())
        len_recep = len(temporary_role_users.query.filter_by(role = "reception").all())
        len_chief = len(temporary_role_users.query.filter_by(role = "chief_doctor").all()) 
    elif role == "chief_doctor":
        len_chief = len(u)
        len_doctor = len(temporary_users.query.filter_by(role='doctor').all())
        len_assistant = len(temporary_role_users.query.filter_by(role = "assistant").all())
        len_recep = len(temporary_role_users.query.filter_by(role = "reception").all())
        len_comp = len(temporary_role_users.query.filter_by(role = "compounder").all()) 
    

    if role == "assistant":    
        return render_template('Admin/admin_sites/assistant_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief)   
    elif role =="compounder":
        return render_template('Admin/admin_sites/compounder_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief)  
    elif role == "reception":
        return render_template('Admin/admin_sites/reception_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief) 
    elif role == "chief_doctor":
        return render_template('Admin/admin_sites/chief_doctor_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief) 


@admin_bp.route('/admin/registration_requests/<username>/<action>/<role>')
def action_role_reg(username,action,role):

    if action == "Accept":
        user = temporary_role_users.query.filter_by(username=username).first()
        if (role == "assistant"):
            x = user_role.query.filter_by(role = "assistant",doctor_username = user.doctor_username).first()
            if x is not None:
                flash("Assistant for doctor "+user.doctor_username+" already exists. To add this assistant remove the existing one.")
        else:
            x = user_role.query.filter_by(role = role).first()
            if x is not None:
                flash("Already exists a person for "+role+" role. Remove the existing person to add new.")
        if user is not None:
            u = User(username = user.username, email = user.email, role = user.role, password_hash = user.password)
            db.session.add(u)
            db.session.commit()
            u = user_role(username = user.username, name = user.name,role = user.role, birthdate = user.birthdate,age = user.age,
            contact_number = user.contact_number, address = user.address, gender = user.gender, work_timings = user.work_timings,
            timestamp = user.timestamp, doctor_username = user.doctor_username,date_of_joining = datetime.datetime.now())
            db.session.add(u)
            db.session.delete(user)
            db.session.commit()
            
    elif action == "Reject":
        user = temporary_role_users.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
    return  redirect(url_for('admin.assistant_registration_requests',role=role))



@admin_bp.route('/admin/role_user/<role>')
def role_user(role):
     u = user_role.query.filter_by(role = role).first()
     past_role_users = past_user_role.query.filter_by(role = role).all()
     return render_template('Admin/admin_sites/role_user_page.html',row = u, past_users = past_role_users,role = role)    

@admin_bp.route('/admin/assistants')
def role_user_assistant():
    u = user_role_query.query.all(role = "assistant").all()

@admin_bp.route('/admin/delete_role_user/<id>/<role>')
def delete_role_user(id,role):
    now = datetime.datetime.now()
    u = user_role.query.get(id)
    db.session.delete(u)
    x = past_user_role(username = u.username, name = u.name, birthdate = u.birthdate,age = u.age,contact_number=u.contact_number,
    address = u.address, gender_user = u.gender,work_timings = u.work_timings,date_of_joining = u.date_of_joining,end_date = now ,role = u.role)
    db.session.add(x)
    try:
        db.session.commit()
        flash("Removed successfully!")
    except:
        db.session.rollback()
        flash("Try again") 
    return redirect(url_for('admin.role_user',role = role))     

@admin_bp.route('/admin/deleted_role_user_details/<id>')
def deleted_role_user_details(id):
    u = past_role_user.query.get(id)
    return render_template('Admin/admin_sites/deleted_role_user.html',row = u)
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

        
        





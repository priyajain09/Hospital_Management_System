from hospital_app.models import User,Doctor,specialization, Patient, deleted_doctors,deleted_patients,is_user_deleted, temporary_users,temporary_role_users
from hospital_app.models import user_role, past_user_role,patient_queue,compounder_queue
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm, specialization_form, search_user,search_doctor_form,disease_statistic_form
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app import db,mongo
from _datetime import datetime
from hospital_app.email import send_request_accepted_mail, send_request_rejected_mail
import datetime
from flask_login import current_user, login_required
import base64
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/home_page')
@login_required
def home_page():
    return render_template('Admin/registration_request.html')

@admin_bp.route('/admin/change_password',methods = ['GET','POST'])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form['old_pass']  
        if check_password_hash(current_user.password_hash, old_password) == False:
            message = "Wrong Password!"
            return render_template('User/user_sites/change_password.html',message = message) 
        
        new_password = request.form['new_pass']
        current_user.set_password(new_password)
        try:
            db.session.commit()
            flash("Password changed!")
        except:
            db.session.rollback()
            flash("Try again!")    
    return render_template('Admin/admin_sites/change_password.html')    

@admin_bp.route('/admin/doctor_list',methods = ['GET','POST'])
@login_required
def doctor_list():
    q = db.session.query(User,Doctor).join(Doctor).all()
    return render_template('Admin/admin_sites/list_of_doctors.html',q=q)

@admin_bp.route('/admin/user_list',methods = ['GET','POST'])
@login_required
def user_list():
    users = db.session.query(User,Patient).join(Patient).filter(User.role == "user")
    return render_template('Admin/admin_sites/list_of_users.html',list=users)


@admin_bp.route('/admin/<username>/<action>')
@login_required
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
        , specialization = user.specialization, timestamp = user.timestamp, contact_number = user.contact_number,File = user.File)
        x = is_user_deleted(username = user.username)
        try:
            db.session.delete(user) 
            db.session.commit()
            db.session.add(u)
            db.session.commit()
            db.session.add(y)
            db.session.commit()
            db.session.add(x)
            db.session.commit()
        except:
            db.session.rollback()    
        # send_request_accepted_mail(y)
    return redirect(url_for('admin.registration_request'))   

@admin_bp.route('/admin/registration_requests')
@login_required
def registration_request():
    q = temporary_users.query.filter_by(role='doctor').all()
    images = []
    for i in q:
        images.append(base64.b64encode(i.File).decode('ascii'))

    if len(q) == 0:
        flash("No pending requests")
    len_doctor = len(q)
    len_assistant = len(temporary_role_users.query.filter_by(role = "assistant").all())
    len_recep = len(temporary_role_users.query.filter_by(role = "reception").all())
    len_comp = len(temporary_role_users.query.filter_by(role = "compounder").all())
    len_chief = len(temporary_role_users.query.filter_by(role = "chief_doctor").all())
    return render_template('Admin/admin_sites/registration_request.html',q=q,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief,images = images)

@admin_bp.route('/admin/departments', methods = ['GET','POST'])
@login_required
def departments():
    form = specialization_form()
    if form.validate_on_submit():
        spez = specialization(specialization = form.specialization_name.data)
        db.session.add(spez)
        db.session.commit()
    q = specialization.query.all()    
    return render_template('Admin/admin_sites/departments.html', q=q, form = form)


@admin_bp.route('/admin/users/<username>/<email>')
@login_required
def user_details(username,email):
    q = Patient.query.filter_by(username = username).first()
    image = base64.b64encode(q.File).decode('ascii')
    return render_template('Admin/admin_sites/user_details.html',user=q,email = email,image = image)

# ******************************************************************************
# To be done later: move ongoing treatments to closed treatments and send an email for the same
# here user is used to denote patient
@admin_bp.route('/admin/delete_user/<username>')
@login_required
def delete_user(username):
    # before deleting patient populate deleted_patients table
    p = patient_queue.query.filter_by(username = username).first()
    c = compounder_queue.query.get(username)
    if p is not None:
        db.session.delete(p)
    if c is not None:
        db.session.delete(c)
    db.session.commit()

    user = User.query.get(username)
    mongo.db.Treatment.aggregate([{'$match':{"patient_userid":username}},{'$out':"Past_Treatments"}])
    mongo.db.Treatment.delete_many({"patient_userid":username})
    mongo.db.Past_Treatments.update_many({"patient_userid":username},{'$currentDate':{"treat_closed_on":{ '$type':"date"}}})

    patient = user.patient
    u = deleted_patients(username = user.username,email=user.email,name= patient.name,age = patient.age,blood_group = patient.blood_group,
    contact_number = patient.contact_number,address = patient.address,gender_user = patient.gender_user,joined_on = patient.timestamp,File = patient.File)
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
@login_required
def doctor_details(username):
    q = Doctor.query.filter_by(username = username).first()
    
    image = base64.b64encode(q.File).decode('ascii')
    return render_template('Admin/admin_sites/doctor_details.html',row=q,image = image)


# **********************************************************************************
# To be done later: Check if the doctor is involved in ongoing treatments or not and send email to him
@admin_bp.route('/admin/delete_doctor/<username>')
@login_required
def delete_doctor(username):
    user = User.query.get(username)
    doctor = user.doctor
    p = patient_queue.query.filter_by(doctor_username = username).first()

    if p is not None:
        flash("Doctor cannot be removed! There are some patients in the doctor's queue.")
        return redirect(url_for('admin.doctor_details',username = username))

    mongo.db.Treatment.aggregate([{'$match':{"doctorid":username}},{'$out':"Past_Treatments"}])
    mongo.db.Treatment.delete_many({"doctorid":username})
    mongo.db.Past_Treatments.update_many({"doctorid":username},{'$currentDate':{"treat_closed_on":{ '$type':"date"}}})

    u = deleted_doctors(username = str(user.username),email=user.email,name=doctor.name,gender_doctor=doctor.gender_doctor,
    age=doctor.age,blood_group=doctor.blood_group,contact_number=doctor.contact_number,address=doctor.address,qualification=doctor.qualification,
    experience=doctor.experience,specialization=doctor.specialization,date_of_joining=doctor.date_of_joining,File = doctor.File)
    x = is_user_deleted.query.get(username)
    x.is_deleted = True
    db.session.add(u)
    db.session.commit()
    q = User.query.get(username)
    if q is not None:
        try:
            db.session.delete(q)
            db.session.commit()
        except:
            db.session.rollback()
            flash("Try Again!")   
            return redirect(url_for(admin.doctor_details,username = username))
    return redirect(url_for('admin.doctor_list'))

# *********************************************************************************

# here users are used to denote patients
@admin_bp.route('/admin/deleted_users',methods=['GET','POST'])
@login_required
def deleted_users(): 
    u = deleted_patients.query.all()
    return render_template('Admin/admin_sites/deleted_users.html',users = u)

@admin_bp.route('/admin/patient_details/<username>')
@login_required
def deleted_user_details(username):
    u = deleted_patients.query.get(username)
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('Admin/admin_sites/deleted_user_details.html',user = u,image = image)

@admin_bp.route('/admin/deleted_doctor_details/<username>')
@login_required
def deleted_doctor_details(username):
    u = deleted_doctors.query.get(username)
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('Admin/admin_sites/deleted_doctor_details.html',row = u,image = image)

@admin_bp.route('/admin/deleted_doctors',methods=['GET','POST'])
@login_required
def deleted_doctors_func():
    u = deleted_doctors.query.all()
    return render_template('Admin/admin_sites/deleted_doctors.html',doctors = u)

@admin_bp.route('/admin/assistant_registration_requests/<role>')
@login_required
def assistant_registration_requests(role):
    u = temporary_role_users.query.filter_by(role = role).all()
    images = []
    for i in u:
        images.append(base64.b64encode(i.File).decode('ascii'))
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
    len_comp= len_comp, len_chief = len_chief,images= images)   
    elif role =="compounder":
        return render_template('Admin/admin_sites/compounder_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief,images = images)  
    elif role == "reception":
        return render_template('Admin/admin_sites/reception_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief,images= images) 
    elif role == "chief_doctor":
        return render_template('Admin/admin_sites/chief_doctor_requests.html',list = u,len_doctor = len_doctor,len_assistant = len_assistant,len_recep = len_recep,
    len_comp= len_comp, len_chief = len_chief,images = images) 


@admin_bp.route('/admin/registration_requests/<username>/<action>/<role>')
@login_required
def action_role_reg(username,action,role):

    if action == "Accept":
        user = temporary_role_users.query.filter_by(username=username).first()
        if (role == "assistant"):
            x = user_role.query.filter_by(role = "assistant",doctor_username = user.doctor_username).first()
            if x is not None:
                flash("Assistant for doctor "+user.doctor_username+" already exists. To add this assistant remove the existing one.")
                return  redirect(url_for('admin.assistant_registration_requests',role=role))
        else:
            x = user_role.query.filter_by(role = role).first()
            if x is not None:
                flash("Already exists a person for "+role+" role. Remove the existing person to add new.")
                return  redirect(url_for('admin.assistant_registration_requests',role=role))
        if user is not None:
            u = User(username = user.username, email = user.email, role = user.role, password_hash = user.password)
            db.session.add(u)
            db.session.commit()
            u = user_role(username = user.username, name = user.name,role = user.role, birthdate = user.birthdate,age = user.age,
            contact_number = user.contact_number, address = user.address, gender = user.gender, work_timings = user.work_timings,
            timestamp = user.timestamp, doctor_username = user.doctor_username,date_of_joining = datetime.datetime.now(),File = user.File)
            db.session.add(u)
            db.session.delete(user)
            db.session.commit()
            
    elif action == "Reject":
        user = temporary_role_users.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
    return  redirect(url_for('admin.assistant_registration_requests',role=role))



@admin_bp.route('/admin/role_user/<role>')
@login_required
def role_user(role):
     u = user_role.query.filter_by(role = role).first()
     if u:
        image = base64.b64encode(u.File).decode('ascii')
        past_role_users = past_user_role.query.filter_by(role = role).all()
        return render_template('Admin/admin_sites/role_user_page.html',row = u, past_users = past_role_users,role = role,image = image)
     past_role_users = past_user_role.query.filter_by(role = role).all()
     return render_template('Admin/admin_sites/role_user_page.html',row = u, past_users = past_role_users,role = role)    



@admin_bp.route('/admin/delete_role_user/<id>/<role>')
@login_required
def delete_role_user(id,role):
    now = datetime.datetime.now()
    u = user_role.query.get(id)
    db.session.delete(u)
    x = past_user_role(username = u.username, name = u.name, birthdate = u.birthdate,age = u.age,contact_number=u.contact_number,
    address = u.address, gender_user = u.gender,work_timings = u.work_timings,date_of_joining = u.date_of_joining,end_date = now ,role = u.role,File = u.File)
    db.session.add(x)
    db.session.commit()
    flash("Removed successfully!")

    return redirect(url_for('admin.role_user',role = role))     

@admin_bp.route('/admin/deleted_role_user_details/<id>')
@login_required
def deleted_role_user_details(id):
    u = past_user_role.query.get(id)
    image = base64.b64encode(u.File).decode('ascii')
    return render_template('Admin/admin_sites/deleted_role_user.html',row = u,image = image)


@admin_bp.route('/admin/current_assistant/<username>')
@login_required
def current_assistant(username):
    u = user_role.query.filter_by(role = "assistant",doctor_username = username).first()
    if u is not None:
        image = base64.b64encode(u.File).decode('ascii')
        return render_template('Admin/admin_sites/current_assistants.html',row = u,username = username,image = image)
    else:
        flash("Assistant is not assigned")
        return render_template('Admin/admin_sites/current_assistants.html',row = u,username = username)

@admin_bp.route('/admin/past_assistants/<username>')
@login_required
def past_assistant(username):
    u = past_user_role.query.filter_by(role = "assistant", doctor_username = username).all()
    images = []
    for i in u:
        images.append(base64.b64encode(i.File).decode('ascii'))
    if len(u) == 0:
        flash("No past assistants")
    return render_template('Admin/admin_sites/past_assistants.html',users = u,username = username,images = images)

@admin_bp.route('/admin/remove_assistant/<username>')
@login_required
def remove_assistant(username):
    u = user_role.query.filter_by(role = "assistant",doctor_username = username).first()
    if u is not None:
        try:
            db.session.delete(u)
            db.session.commit()
            flash("Deleted successfully")
        except:
            flash("Try Again")
    return redirect(url_for('admin.current_assistant',username = username))             


# *******************************************************************************************************

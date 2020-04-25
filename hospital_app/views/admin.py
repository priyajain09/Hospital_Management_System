from hospital_app.models import User,Doctor,specialization, Patient, deleted_doctors,deleted_patients,is_user_deleted
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app.forms import LoginForm, specialization_form, search_user,search_doctor_form
from hospital_app.forms import ResetPasswordRequestForm, ResetPasswordForm
from hospital_app import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/home_page')
def home_page():
    return render_template('Admin/home_page.html')

@admin_bp.route('/admin/doctor_list',methods = ['GET','POST'])
def doctor_list():
    form = search_doctor_form()
    if form.validate_on_submit():
        doctors = db.session.query(User,Doctor).join(Doctor).filter(User.confirmed == True,Doctor.specialization == str(form.specialization.data)).all()
        if len(doctors) == 0:
            flash("No Doctors")
        return render_template('Admin/admin_sites/list_of_doctors.html',q=doctors,form = form)
    q = db.session.query(User,Doctor).join(Doctor).filter(User.confirmed == True).all()
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


@admin_bp.route('/admin/registration_request')
def registration_request():
    q = db.session.query(User,Doctor).join(Doctor).filter(User.confirmed == False).all()
    if len(q) == 0:
        flash("No pending requests")
    return render_template('Admin/admin_sites/registration_request.html',q=q)


@admin_bp.route('/admin/registration_request/<username>')
def action_reg_request(username):
    q = Doctor.query.filter_by(username = username).first()
    return render_template('Admin/admin_sites/registration_request_action.html',q=q)

@admin_bp.route('/admin/<username>/<action>')
def action_taken_on_request(username,action):
    if action=="Reject":
        # due to cascading its corresponding entry from doctor table gets deleted automatically.
        x = User.query.filter_by(username=username).first() 
        db.session.delete(x) 
        db.session.commit()
    else:
        x = User.query.filter_by(username=username).first() 
        x.confirmed = True
        u = is_user_deleted(username = username)
        db.session.add(u)
        db.session.commit()
    return redirect(url_for('admin.home_page'))
        # x = Doctor.query.filter_by(username=username).first() 
        # add doj later
    return redirect(url_for('admin.registration_request'))

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
    u = deleted_doctors(username = str(user.username),email=user.email,name=doctor.name,gender_doctor=doctor.gender_doctor,age=doctor.age,blood_group=doctor.blood_group,contact_number=doctor.contact_number,address=doctor.address,qualification=doctor.qualification,experience=doctor.experience,specialization=doctor.specialization,date_of_joining=doctor.date_of_joining)
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
    return render_template('Admin/admin_sites/deleted_doctors.html',doctors = u,form=form)




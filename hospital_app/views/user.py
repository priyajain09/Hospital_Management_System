from hospital_app.models import User,Doctor
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import db
from hospital_app import mongo
import json
from flask_login import current_user, login_required
from hospital_app import user_collection
from hospital_app.forms import search_doctor_form,update_user_form,change_password_form
from hospital_app.models import Doctor,upload_medical_records,Patient,compounder_queue,patient_queue
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from flask import send_file,Markup
from io import BytesIO
import base64
from werkzeug.security import generate_password_hash, check_password_hash


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

user_bp = Blueprint('user', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/user/home_page')
@login_required
def home_page():
    return redirect(url_for('user.doctor'))

@user_bp.route('/user/treatment/<int:treat_id>/prescriptions/')
@login_required
def prescriptions(treat_id):
    treatment = mongo.db.Treatment.find_one({"treat_id":treat_id})
    return render_template('User/user_sites/prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)

@user_bp.route('/user/doctor',methods = ['GET','POST'])
@login_required
def doctor():
    form = search_doctor_form()
    if form.validate_on_submit():
        d = Doctor.query.filter_by(specialization = str(form.specialization.data)).all()
    else:
        d = Doctor.query.all()
    if len(d) == 0:
        flash("No doctors")    
    images = []
    for u in d:
        images.append(base64.b64encode(u.File).decode('ascii'))

    return render_template('User/user_sites/doctors.html',doctors=d,images = images,form = form)
        
@user_bp.route('/user/view_profile',methods = ['GET','POST'])
def view_profile():
    patient = current_user.patient
    image = base64.b64encode(patient.File).decode('ascii')
    return render_template('User/user_sites/view_profile.html',user = patient,image = image)

@user_bp.route('/user/update_profile',methods = ['GET','POST'])
@login_required
def update_profile():
    if request.method == "POST":
        file = request.files['profile_photo']

        u = current_user.patient

        if file and file.filename != "":
            u.File = file.read()

        
        u.name = request.form['name']
        u.age = request.form['age']
        u.address = request.form['address']
        u.contact_number = request.form['contact_number']
        u.blood_group = request.form['blood_group']
        
        try:
            db.session.commit()
            flash("Updated successfully!")
        except:
            db.session.rollback()
            flash("Try Again!")    
    u = current_user.patient
    image = base64.b64encode(u.File).decode('ascii')         
    return render_template('User/user_sites/update_profile.html',user = current_user.patient,image = image)

@user_bp.route('/view_photo/<Id>')
@login_required
def view_photo(Id):
    u = Patient.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = "flask.png")

@user_bp.route('/change_password',methods = ['GET','POST'])
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
    return render_template('User/user_sites/change_password.html')



# /*********************************************************************************************/

@user_bp.route('/user/documents/<role>',methods=['GET','POST'])
@login_required
def upload_document(role):
    if request.method == "POST":
        file = request.files['in_file']
        u = upload_medical_records(treat_id = int(request.form['treat_id']),type_doc=str(request.form['type_doc']),date=request.form['date'],File=file.read(),
        name = request.form['filename'],filename = file.filename,username = current_user.username)
        db.session.add(u)
        try:
            db.session.commit()
            flash("uploaded file successfully!")
        except:
            db.session.rollback()    
            flash("Error! Try Again")
    pres = upload_medical_records.query.filter_by(type_doc = role,username = current_user.username).all()  
    if role == "Report":
        return render_template('User/user_sites/upload_document_report.html',pres = pres)
    elif role == "Invoice":
        return render_template('User/user_sites/upload_document_invoice.html',pres = pres)
    return render_template('User/user_sites/upload_document.html',pres = pres)

@user_bp.route('/delete_document/<Id>')
@login_required
def remove_document(Id):
    u = upload_medical_records.query.get(Id)
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for('user.upload_document',role = u.type_doc))      

@user_bp.route('/download/<Id>')
@login_required
def download(Id):
    u = upload_medical_records.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = u.filename, as_attachment = True)

@user_bp.route('/view_document/<Id>')
@login_required
def view_document(Id):
    u = upload_medical_records.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = u.filename)

# /***********************************************************************************/

@user_bp.route('/user/close_treatment/<int:treat_id>')
@login_required
def close_treatment(treat_id):
    mongo.db.Treatment.aggregate([{'$match':{"treat_id":treat_id}},{'$out':"Past_Treatments"}])
    mongo.db.Treatment.delete_one({"treat_id":treat_id})
    mongo.db.Past_Treatments.update_one({"treat_id":treat_id},{'$currentDate':{"treat_closed_on":{ '$type':"date"}}})
    return redirect(url_for('user.active_treatments'))

@user_bp.route('/user/past_treatments')
@login_required
def past_treatments():
    treatment = mongo.db.Past_Treatments.find({"patient_userid":current_user.username})
    return render_template('User/user_sites/closed_treatments.html',treatments=treatment)

@user_bp.route('/user/closed_treatment/<int:treat_id>/prescriptions')
@login_required
def deleted_prescriptions(treat_id):
    treatment = mongo.db.Past_Treatments.find_one({"treat_id":treat_id})
    return render_template('User/user_sites/deleted_prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)

@user_bp.route('/user/active_treatments')
@login_required
def active_treatments():
    treatments = mongo.db.Treatment.find({"patient_userid":current_user.username})
    if treatments.count() == 0:
        flash("There are no ongoing treatments")
    return render_template('User/user_sites/active_treatments.html',treatments = treatments)

@user_bp.route('/user/active_treatment/<int:treat_id>')
@login_required
def active_treatment(treat_id):
    treatment = mongo.db.Treatment.find_one({"treat_id":treat_id})
    return render_template('User/user_sites/active_treatment.html',treatment = treatment)

@user_bp.route('/user/all_documents/<treat_id>')
@login_required
def documents(treat_id):
    documents = upload_medical_records.query.filter_by(treat_id = treat_id).all()
    return render_template('User/user_sites/documents.html',documents = documents,treat_id = treat_id)

@user_bp.route('/user/past_documents/<treat_id>')
@login_required
def past_documents(treat_id):
    documents = upload_medical_records.query.filter_by(treat_id = treat_id).all()
    return render_template('User/user_sites/past_documents.html',documents = documents,treat_id = treat_id)

@user_bp.route('/user/closed_treatment/<int:treat_id>')
@login_required
def closed_treatment(treat_id):
    treatment = mongo.db.Past_Treatments.find_one({"treat_id":treat_id})
    return render_template('User/user_sites/closed_treatment.html',treatment = treatment)    

@user_bp.route('/appointment')
@login_required
def appointment():
    num = 0
    val =0 
    username = current_user.username
    u = compounder_queue.query.get(username)
    if u is not None:
        message = "Currently in the compounder queue"
        a = compounder_queue.query.all()
        for i in a:
            val = val +1
            if i.username == username:
                num = val 
                break

    else:
        val = 0
        u = patient_queue.query.filter_by(username = username).first()
        if u is not None:
            message = "Currently in the "+u.doctor+" queue"
            a = patient_queue.query.all()
            for i in a:
                val = val +1
                if i.username == username:
                    num = val
                    break
        else:
            message = "No appointment"
        
        return render_template('User/user_sites/appointment.html',message = message,position = num)

@user_bp.route('/user/delete_account')
@login_required
def delete_account():
    p = patient_queue.query.filter_by(username = username).first()
    c = compounder_queue.query.get(username)
    db.session.delete(p)
    db.session.delete(c)
    db.session.commit()

    username = current_user.username

    mongo.db.Treatment.aggregate([{'$match':{"patient_userid":username}},{'$out':"Past_Treatments"}])
    mongo.db.Treatment.delete_many({"patient_userid":username})
    mongo.db.Past_Treatments.update_many({"patient_userid":username},{'$currentDate':{"treat_closed_on":{ '$type':"date"}}})

    
    user = User.query.get(username)
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
    return redirect(url_for('login.login'))
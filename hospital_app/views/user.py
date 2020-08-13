from hospital_app.models import User,Doctor
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import db
from hospital_app import mongo
import json
from flask_login import current_user, login_required
from hospital_app import user_collection
from hospital_app.forms import search_doctor_form,update_user_form
from hospital_app.models import Doctor,upload_medical_records,Patient
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from flask import send_file,Markup
from io import BytesIO
import base64


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

user_bp = Blueprint('user', __name__)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/user/home_page')
def home_page():
    return render_template('User/home.html')

@user_bp.route('/user/current_treatments')
def current_treatments():
    treatment = mongo.db.Treatment.find({"patient_userid":current_user.username})
    return render_template('User/user_sites/current_treatments.html',treatment=treatment)

@user_bp.route('/user/treatment/<int:treat_id>/prescriptions/')
def prescriptions(treat_id):
    treatment = mongo.db.Treatment.find_one({"treat_id":treat_id})
    return render_template('User/user_sites/prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)

@user_bp.route('/user/doctor',methods = ['GET','POST'])
def doctor():
    d = Doctor.query.all()
    return render_template('User/user_sites/doctors.html',doctors=d)
        
@user_bp.route('/user/view_profile',methods = ['GET','POST'])
def view_profile():
    patient = current_user.patient
    image = base64.b64encode(patient.File).decode('ascii')
    return render_template('User/user_sites/view_profile.html',user = patient,image = image)

@user_bp.route('/user/update_profile',methods = ['GET','POST'])
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

@user_bp.route('/view_document/<Id>')
def view_photo(Id):
    u = Patient.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = "flask.png")


# /*********************************************************************************************/

@user_bp.route('/user/documents/<role>',methods=['GET','POST'])
def upload_document(role):
    if request.method == "POST":
        file = request.files['in_file']
        u = upload_medical_records(treat_id = int(request.form['treat_id']),type_doc=str(request.form['type_doc']),date=request.form['date'],File=file.read(),name = request.form['filename'],filename = file.filename)
        db.session.add(u)
        try:
            db.session.commit()
            flash("uploaded file successfully!")
        except:
            db.session.rollback()    
            flash("Error! Try Again")
    pres = upload_medical_records.query.filter_by(type_doc = role).all()  
    if role == "Report":
        return render_template('User/user_sites/upload_document_report.html',pres = pres)
    elif role == "Invoice":
        return render_template('User/user_sites/upload_document_invoice.html',pres = pres)
    return render_template('User/user_sites/upload_document.html',pres = pres)

@user_bp.route('/delete_document/<Id>')
def remove_document(Id):
    u = upload_medical_records.query.get(Id)
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for('user.upload_document',role = u.type_doc))      

@user_bp.route('/download/<Id>')
def download(Id):
    u = upload_medical_records.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = u.filename, as_attachment = True)

@user_bp.route('/view_document/<Id>')
def view_document(Id):
    u = upload_medical_records.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = u.filename)

# /***********************************************************************************/

@user_bp.route('/user/close_treatment/<int:treat_id>')
def close_treatment(treat_id):
    mongo.db.Treatment.aggregate([{'$match':{"treat_id":treat_id}},{'$out':"Past_Treatments"}])
    mongo.db.Treatment.delete_one({"treat_id":treat_id})
    mongo.db.Past_Treatments.update_one({"treat_id":treat_id},{'$currentDate':{"treat_closed_on":{ '$type':"date"}}})
    return redirect(url_for('user.current_treatments'))

@user_bp.route('/user/past_treatments')
def past_treatments():
    treatment = mongo.db.Past_Treatments.find({"patient_userid":current_user.username})
    return render_template('User/user_sites/past_treatments.html',treatment=treatment)

@user_bp.route('/user/closed_treatment/<int:treat_id>/prescriptions')
def deleted_prescriptions(treat_id):
    treatment = mongo.db.Past_Treatments.find_one({"treat_id":treat_id})
    return render_template('User/user_sites/deleted_prescriptions.html',prescriptions=treatment["prescription"],treat_id=treat_id)







    
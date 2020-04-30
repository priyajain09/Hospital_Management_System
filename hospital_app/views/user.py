from hospital_app.models import User,Doctor
from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import db
from hospital_app import mongo
import json
from flask_login import current_user
from hospital_app import user_collection
from hospital_app.forms import search_doctor_form,update_user_form
from hospital_app.models import Doctor,upload_medical_records,upload_report
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from flask import send_file
from io import BytesIO


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

user_bp = Blueprint('user', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/user/home_page')
def home_page():
    return render_template('User/home_page.html')

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
    form = search_doctor_form()
    if form.validate_on_submit():
        # return str(form.specialization.data)
        d = Doctor.query.filter_by(specialization = str(form.specialization.data)).all()
        return render_template('User/user_sites/list_of_doctors.html',q=d,form=form)
    return render_template('User/user_sites/list_of_doctors.html',q=d,form=form)
        
@user_bp.route('/user/view_profile',methods = ['GET','POST'])
def view_profile():
    patient = current_user.patient
    return render_template('User/user_sites/view_profile.html',patient = patient)

@user_bp.route('/user/update_profile',methods = ['GET','POST'])
def update_profile():
    form = update_user_form(obj = current_user.patient)
    if form.validate_on_submit():
        form.populate_obj(current_user.patient)
        db.session.commit()
    return render_template('User/user_sites/update_profile.html',form = form)

@user_bp.route('/user/upload_medical_records',methods=['GET','POST'])
def upload_medical_records_func():
    if request.method == "POST":
        file = request.files['in_file']
        u = upload_medical_records(treat_id = int(request.form['treat_id']),type_doc=str(request.form['type_doc']),date=request.form['date'],File=file.read())
        db.session.add(u)
        try:
            db.session.commit()
            flash("uploaded file successfully!")
        except:
            db.session.rollback()    
            flash("Error! Try Again")
    return render_template('User/user_sites/upload_document.html')

@user_bp.route('/download')
def download():
    u = upload_medical_records.query.first()
    return send_file(BytesIO(u.File),attachment_filename='flask.pdf',as_attachment=True)

@user_bp.route('/user/<int:treat_id>/<int:pres_id>/add_reports/',methods=['GET','POST'])
def add_reports(treat_id,pres_id):
    t = mongo.db.Treatment.find_one({"treat_id":treat_id})
    reports = upload_report.query.filter_by(treat_id=treat_id,pres_id=pres_id).all()
    p = t["prescription"]
    print(p[pres_id-1])
    return render_template('User/user_sites/add_report.html',prescription=p[pres_id-1],added_reports=reports,treat_id=treat_id)


# Assumption has been taken here that prescriptions are stored on the index equal to their pres_id
@user_bp.route('/user/<int:treat_id>/<int:pres_id>/add_reports/<report_name>',methods=['GET','POST'])
def upload_report_file(treat_id,pres_id,report_name):
    if request.method=='POST':
        file = request.files['input_report']
        if file:
            u = upload_report(treat_id = treat_id,pres_id = pres_id,report_name = report_name,file_name = file.filename,report = file.read())
            db.session.add(u)
            try:
                db.session.commit()
                flash("File Uploaded Successfully!")
            except:
                db.session.rollback()
                flash("Error!Try Again")
        else:
            flash("File not selected")
    return redirect(url_for('user.add_reports',treat_id = treat_id,pres_id=pres_id))

@user_bp.route('/user/delete_report/<int:treat_id>/<int:pres_id>/<report_name>')
def remove_report(treat_id,pres_id,report_name):
    u = upload_report.query.filter_by(treat_id=treat_id,pres_id=pres_id,report_name=report_name).first()
    db.session.delete(u)
    try:
        db.session.commit()
        flash("Deleted Successfully")
    except:
        db.session.rollback()
        flash("Try Again")
    return redirect(url_for('user.add_reports',treat_id = treat_id,pres_id=pres_id))        

@user_bp.route('/user/download_report/<treat_id>/<pres_id>/<report_name>')
def download_report(treat_id,pres_id,report_name):
    u = upload_report.query.filter_by(treat_id=treat_id,pres_id=pres_id,report_name=report_name).first()
    return send_file(BytesIO(u.report),attachment_filename=u.file_name,as_attachment=True)

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







    
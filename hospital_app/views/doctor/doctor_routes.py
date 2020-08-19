from flask import Blueprint, render_template, redirect,url_for, request, flash
from hospital_app import mongo
from hospital_app.models import User,Doctor , patient_queue, Medicine, Disease, Symptom, user_role, past_user_role, upload_medical_records
from hospital_app import db
import json
from flask_login import current_user
from hospital_app.forms import update_doctor_form , change_password_form
from hospital_app.models import Doctor
from datetime import date, datetime, timedelta
from collections import defaultdict
from io import BytesIO
import base64
from flask import send_file,Markup

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

doctor_routes_bp = Blueprint('doctor_routes',__name__)

@doctor_routes_bp.route('/doctor')
def home_page():      
    return render_template('Doctor/home.html')

@doctor_routes_bp.route('/current_treatment_list', methods=['GET', 'POST'])
def current_treatment_list():
    doc_treatment = mongo.db.Treatment.find( { 'doctorid' : current_user.username }).sort([("time_stamp", -1)])
    return render_template('Doctor/doctor_sites/current_treatment_list.html',treatment=doc_treatment)

@doctor_routes_bp.route('/doc-closed_treatment_list', methods=['GET', 'POST'])
def closed_treatment_list():
    doc_treatment = mongo.db.Past_Treatments.find( { 'doctorid' : current_user.username }).sort([("treat_closed_on", -1)])
    return render_template('Doctor/doctor_sites/closed_treatment_list.html',treatment=doc_treatment)

@doctor_routes_bp.route('/doc-refer/<treat_id>', methods=['GET', 'POST'])
def refer(treat_id):
    if request.method == 'POST':    
        Referto = request.form['Referto']
        print(Referto)
        mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{ 'Referto':Referto , 'treat_closed_on': datetime.now()}})
        doc_treatment = mongo.db.Treatment.find_one({ "treat_id": int(treat_id) }) 
        mongo.db.Past_Treatments.insert(doc_treatment)
        mongo.db.Treatment.remove({ "treat_id": int(treat_id) })      
    return redirect(url_for("doctor_routes.doc_queue"))

@doctor_routes_bp.route('/doctor/view_profile',methods = ['GET','POST'])
def view_profile():
    doctor = current_user.doctor
    image = base64.b64encode(doctor.File).decode('ascii')
    return render_template('Doctor/doctor_sites/view_profile.html',user = doctor,image = image)

@doctor_routes_bp.route('/doctor/update_profile',methods = ['GET','POST'])
def update_profile():
    if request.method == "POST":
        file = request.files['profile_photo']

        u = current_user.doctor

        if file and file.filename != "":
            u.File = file.read()

        
        u.name = request.form['name']
        u.age = request.form['age']
        u.address = request.form['address']
        u.contact_number = request.form['contact_number']
        u.blood_group = request.form['blood_group']
        u.gender_doctor = request.form['gender_doctor']
        u.qualification = request.form['qualification']
        u.experience = request.form['experience']
        u.specialization = request.form['specialization']
        u.consultant_fee = request.form['consultant_fee']
        u.visiting_hours = request.form['visiting_hours']

        try:
            db.session.commit()
            flash("Updated successfully!")
        except:
            db.session.rollback()
            flash("Try Again!")    
    u = current_user.doctor
    image = base64.b64encode(u.File).decode('ascii')         
    return render_template('Doctor/doctor_sites/update_profile.html',user = current_user.doctor,image = image)

@doctor_routes_bp.route('/doctor/change_password',methods = ['GET','POST'])
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

    return render_template('Doctor/doctor_sites/change_password.html',form = form)


@doctor_routes_bp.route('/doc-queue')
def doc_queue():
    u = patient_queue.query.filter_by(doctor_username = current_user.username).all()       
    return render_template('Doctor/doctor_sites/doctor_queue.html', list = u)

@doctor_routes_bp.route('/doc-visit_patient/<treat_id>')
def visit_patient(treat_id):
    mongo.db.Treatment.update({ "treat_id": int(treat_id) },{"$set":{ 'status': "doctor" }})
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })  
    medicine_list = Medicine.query.all()
    disease_list = Disease.query.all()
    symptom_list = Symptom.query.all()
    return render_template('Doctor/doctor_sites/ongoing_treatment.html', treatment = treatment, medicine_list = medicine_list, symptom_list = symptom_list, disease_list = disease_list)
    
@doctor_routes_bp.route('/doc-prescription/<treat_id>',methods = ['GET','POST'])
def prescription(treat_id):
    print("init")
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) })  
    if request.method == 'POST':    
        multiselect1 = request.form.getlist('multiselect1')
        print(multiselect1)
        multiselect2 = request.form.getlist('multiselect2')
        print(multiselect2)
        multiselect3 = request.form.getlist('multiselect3')
        print(multiselect3)
        print(treat_id)
        print(treatment['total_prescriptions'] )
        mongo.db.Treatment.update(
            { "treat_id": int(treat_id), "prescription.pres_id": treatment['total_prescriptions']},
                {"$push": 
                    {   
                        "prescription.$.medicines": { '$each': multiselect3 }
                    }
                }
        )
        mongo.db.Treatment.update(
        { "treat_id": int(treat_id), "prescription.pres_id": treatment['total_prescriptions']},
            { "$push": 
                {
                    "prescription.$.symptoms" : { '$each': multiselect1 }
                }
            }
        )
        mongo.db.Treatment.update(
        { "treat_id": int(treat_id) },
            { "$push": 
                {
                    "disease" : { '$each': multiselect2 }
                }
            }
        )
        print("pushed")

    return render_template('Doctor/doctor_sites/ongoing_treatment_pres.html', treatment = treatment ,dis = multiselect2, med = multiselect3, sym = multiselect1, pres_id = treatment['total_prescriptions'])
    
@doctor_routes_bp.route('/doc-prescription/<treat_id>/<pres_id>',methods = ['GET','POST'])
def prescription_two(treat_id, pres_id):
    print("init")
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) }) 
    prescriptions = treatment['prescription'] 
    pres = prescriptions[int(pres_id) -1]
    medicines = pres['medicines']
    if request.method == 'POST': 
        for med in medicines:   
            morning_dosage = request.form[med+"_morndos"]
            noon_dosage = request.form[med+"_aftndos"]
            night_dosage = request.form[med+"_nightdos"]
            quantity = request.form[med+"_quantity"]
            Dosage = request.form["Dosage"]
            mongo.db.Treatment.update(
            { "treat_id": int(treat_id), "prescription.pres_id": int(pres_id)},
                {"$push": 
                    {   
                        "prescription.$.dosage": 
                        {
                            "medicine": med,
                            "morning_dosage" : morning_dosage,
                            "noon_dosage" : noon_dosage,  
                            "night_dosage" : night_dosage, 
                            "quantity" : quantity,
                            "Dose" : Dosage
                        }
                    }
                }
            )

        note = request.form["note"]
        next_visit_date = request.form["next_visit_date"]
        reports = request.form.getlist('reports[]')
        print(reports)

        mongo.db.Treatment.update(
        { "treat_id": int(treat_id), "prescription.pres_id": int(pres_id)},
                {"$push": 
                    {   
                        "prescription.$.note": "Note : " + note
                    }
                }
            )
        mongo.db.Treatment.update(
        { "treat_id": int(treat_id), "prescription.pres_id": int(pres_id)},
                {"$push": 
                    {   
                        "prescription.$.note": "Next Visit Date : " + next_visit_date
                    }
                }
            )
        mongo.db.Treatment.update(
        { "treat_id": int(treat_id)},
                {"$push": 
                    {   
                        "reports": { '$each': reports }
                    }
                }
        )
    return render_template('Doctor/doctor_sites/refer.html', treat_id = treat_id)

@doctor_routes_bp.route('/prescription-history/<treat_id>')
def prescription_history(treat_id):
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) }) 
    if treatment == None :
        treatment = mongo.db.Past_Treatments.find_one({'treat_id' : int(treat_id) })
    if treatment == None :
        return "This Treatment does not exist"
    prescriptions = reversed(treatment['prescription'])
    return render_template('Doctor/doctor_sites/prescription_history.html', prescriptions = prescriptions, treatment = treatment)    

# /*********************************************************************************************/

@doctor_routes_bp.route('/treatment-reports/<treat_id>')
def treatment_reports(treat_id):
    treatment = mongo.db.Treatment.find_one({'treat_id' : int(treat_id) }) 
    report = upload_medical_records.query.filter_by(type_doc = 'Report', treat_id = treat_id).all()  
    
    return render_template('Doctor/doctor_sites/treatment_reports.html', report = report, treatment = treatment)      

@doctor_routes_bp.route('/doc-download/<Id>')
def download(Id):
    u = upload_medical_records.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = u.filename, as_attachment = True)

@doctor_routes_bp.route('/doc-view_document/<Id>')
def view_document(Id):
    u = upload_medical_records.query.get(Id)
    return send_file(BytesIO(u.File),attachment_filename = u.filename)

@doctor_routes_bp.route('/doc-patient-documents/<role>',methods=['GET','POST'])
def patient_document(role):

    pres = upload_medical_records.query.filter_by(type_doc = role).all()  
    if role == "Report":
        return render_template('Doctor/doctor_sites/patient_docs_report.html',pres = pres)
    return render_template('Doctor/doctor_sites/patient_docs_pres.html',pres = pres)


# /*********************************************************************************************/


@doctor_routes_bp.route('/doctor/current_assistant')
def current_assistant():
    u = user_role.query.filter_by(role = "assistant",doctor_username = current_user.username ).first()
    if u is not None:
        image = base64.b64encode(u.File).decode('ascii')
        return render_template('Doctor/doctor_sites/current_assistants.html',row = u,username = current_user.username,image = image)
    else:
        flash("Assistant is not assigned")
        return render_template('Doctor/doctor_sites/current_assistants.html',row = u,username = current_user.username)

@doctor_routes_bp.route('/doctor/past_assistants')
def past_assistant():
    u = past_user_role.query.filter_by(role = "assistant", doctor_username = current_user.username).all()
    images = []
    for i in u:
        images.append(base64.b64encode(i.File).decode('ascii'))
    if len(u) == 0:
        flash("No past assistants")
    return render_template('Doctor/doctor_sites/past_assistants.html',users = u,username = current_user.username,images = images)

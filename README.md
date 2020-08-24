--------------------------------------------------------------
Steps to set up the Hospital Management System(HMS):
--------------------------------------------------------------

MongoDB Database set up
-----------------------
 Open the mongo shell and type following queries:

//Here Hospital_Management_Data is the database name 
>use Hospital_Treatment_Data

//Treatment is used to store all the ongoing treatments
>db.Treatment.insert({'treat_id' : 0, 'Description' : "Total number of treatments started" 'total_treatments' : 0})

//Past_Treatments is used to store all the past treatments
>db.Past_Treatments.insert({"time_stamp": new Date() })


Postgres Database set up
------------------------
Open the psql shell and type following queries:
#DROP DATABASE hospital_db;
#CREATE DATABASE hospital_db;

Installation 
------------
-> Install python3 in the system
-> Create virtual environment
-> Install all the dependencies from the given requirements.txt file
If you are using Linux OS:
Run pip install -r requirements.txt (Python 2), or pip3 install -r requirements.txt (Python 3)


HMS set up
----------
-> Configure the system
    1. Open the config.py in instance folder
    2. set all the details asked in config.py
-> Go in the Hospital_Management_System directory
    Initialize the tables of postgres’s ‘hospital_db’ database using these commands :
    $flask db init
    $flask db migrate
    $flask db upgrade
//First, add the admin to the system
    -> open the flask shell using this command
        $flask shell
    -> Add the admin 
        u = User(username='admin',email='admin@gmail.com',role='admin')
        u.set_password('admin')
        db.session.add(u)
        db.session.commit()
-> open the postgres shell and insert the following:

INSERT INTO medicine
(name)
VALUES
('Combiflame'), ('Paracetamol'), ('Crocin'), ('Volini'), ('Move'),('Liver-52');

INSERT INTO symptom 
(name)
VALUES
('Cold'), ('Fever'), ('Rashes'), ('Vomiting'), ('Sweating'),('Nose-Bleeding'),('Nausia');

INSERT INTO disease
(name)
VALUES
('Diabetes'), ('Viral-Fever'), ('Bacterial-Fever'),('Asthenia'), ('Asthma'), ('Astigmatism'),('Astrocytoma');


How to run the system
---------------------
-> Activate the virtual environment which you have created above.
-> Go in the Hospital_Management_System directory.
-> run the command 
$flask run
It runs the localhost server. Open the link in any browser and it will display the login page of the HMS.







Registration Process
--------------------
Register as user:
Users can register into the system by clicking on the “Register as User” button on the login page.  After filling the registration form, an email will be sent on the given email address. On clicking the link within the few minutes in the sent email will register the user and user will be redirected to the login page.

Users can also be registered by the receptionist. So, open the receptionist home page and register the users. The default password for all the users in this case is “password”. This is only for the testing purpose because to get the actual password one needs to fill the legitimate email address and then a random password will be sent to the user on the email. But in the testing it is not possible to enter so many legitimate email addresses that’s why we have provided both the functionality but for now email functionality is commented and password is set as default “password” for all the users. When this system is actually used in real life then we can uncomment that part and easily use that functionality.

Register as doctor:
	Doctor can register by clicking on the “Register as doctor” button on the login page then 
a registration request will be sent to the admin. Then open the admin page and accept the request.

Register as other role users:
Other role users like assistant, receptionist, chief medical officer and compounder can register by clicking on the “Register as other” button on the login page then a registration request will be sent to the admin. Then open the admin page and accept the request.





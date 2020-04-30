For inserting a doctor into the system:
-> write following commands in python shell: 
-> u = User(username = 'pj',email='nfjefne',role='doctor',confirmed=True)
-> u.set_password('whatever')
-> db.session.add(u)
-> db.session.commit()
-> similarily add entry into doctor from python shell or using psql commands.

# to print all users
users = User.query.all()

for user in users:
    print user.name



for running the application:
flask run

for initalising database use(it will be used only once):
flask db init

migrate database using command:
flask db migrate

For upgrade :
flask db upgrade


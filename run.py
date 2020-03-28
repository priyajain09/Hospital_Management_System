from hospital_app import app
from  hospital_app.models import User,Doctor
from hospital_app import db

# The following function in run.py creates a shell context
# that adds the database instance and models to the shell session(can be started using flask shell):
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,'Doctor':Doctor}

if __name__ == "__main__":
    app.run()
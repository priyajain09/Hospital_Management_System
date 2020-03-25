from hospital_app import app
# import hospital_app.models

# The following function in run.py creates a shell context
# that adds the database instance and models to the shell session(can be started using flask shell):
# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Post': Post}

if __name__ == "__main__":
    app.run()
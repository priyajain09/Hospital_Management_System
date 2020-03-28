from flask_mail import Message
from hospital_app import mail,app
from flask import render_template


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[HMS] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('Authentication/email/reset_password.txt',user=user, token=token),
               html_body=render_template('Authentication/email/reset_password.html',user=user, token=token))


def send_registration_request_email(user):
    token = user.get_reset_password_token()
    send_email('[HMS] Confirm Your Email Address',
                    sender=app.config['ADMINS'][0], 
                    recipients=[user.email], 
                    text_body=render_template('Authentication/email/register.txt',user=user, token=token),
                    html_body=render_template('Authentication/email/register.html',user=user, token=token))
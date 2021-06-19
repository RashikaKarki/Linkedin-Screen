from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os 

# Setting up the flask application

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['CELERY_BROKER_URL'] ='redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] ='redis://localhost:6379/1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'founders.sqlite')
app.config['SECURITY_REGISTERABLE'] = True
# Configure application to not send an email upon registration
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY")
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USETLS = False,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	)

tomail = Mail(app)

db = SQLAlchemy(app)
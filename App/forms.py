from wtforms import Form, StringField, SelectField, validators, PasswordField, BooleanField
from flask_wtf import FlaskForm 
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from App.models import User
from App.app import db
from wtforms.validators import ValidationError


class FounderSearchForm(Form):
    choices = [('Fullname', 'Name'),
                ('Added_by', 'Added By'), 
                ('Reached_out', 'Reached Out'),                
               ('Education', 'Education'),
               ('Current Company', 'Current Company'),
               ('Past Company', 'Past Company')
               ]
    select = SelectField("Filter using column:", choices=choices)
    search = StringField('')

class Linkedin(Form):
    email= StringField('Email/Username')
    password =PasswordField('Password')

class AdminForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'),Length(max=50)])






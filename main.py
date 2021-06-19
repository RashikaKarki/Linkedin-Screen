import os
from flask import Flask,render_template, redirect, url_for, request,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from celery import Celery
from App.app import app,db,tomail
from flask_mail import Message
import time
import pandas as pd
import uuid 

from App.db_setup import init_db, db_session, engine
from App.models import Founders, User, MainAdmin
from App.forms import FounderSearchForm, Linkedin, AdminForm, RegisterForm
from App.scraper import before_logging

bootstrap = Bootstrap(app)

# Setting up Celery
celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )

celery.conf.update(
    result_backend = app.config['CELERY_RESULT_BACKEND'],
    broker_url = app.config['CELERY_BROKER_URL']
)

init_db()


# Managing the Login and User Authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

@login_manager.user_loader
def load_user(user_id):
    return MainAdmin.query.get(int(user_id))

class myModalView(ModelView):
    def get_edit_form(self):
        form_class = super(myModalView, self).get_edit_form()
        return form_class

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login'))

    column_list = ['username','email','token']

# Setting up asynchronous linkedin scraping function
@celery.task(name = "celery.linkedin_login")
def linkedin_login(email, password, currentuser):
    updtmsg = before_logging(email, password, currentuser)
    if updtmsg == "Not added":
        pass
    elif updtmsg == "Error":
        try:
            msg = Message("Baidu Scraper Notification!",
            sender="baiduventures@gmail.com",
            recipients=[currentuser.email])
            msg.html = "<p>Hey " + currentuser.user_name + ",</p><br><br>The linkedin authentication you submitted was invalid.<br><br>Best,<br>Baidu Team"
            with app.app_context():         
                tomail.send(msg)
                return 'Mail sent!'
        except:
            return(str("Error"))
    else:
        try:
            msg = Message("Baidu Scraper Notification!",
            sender="baiduventures@gmail.com",
            recipients=["rashikakarki9841@gmail.com"])
            msg.html = updtmsg
            with app.app_context():         
                tomail.send(msg)
                return 'Mail sent!'
        except:
            return(str("Error"))

# Home Page Route
@app.route('/', methods=['GET', 'POST'])
def home():
    form = AdminForm()
    if form.validate_on_submit():
        main_admin = MainAdmin.query.filter_by(username=form.username.data).first()
        if main_admin:
            if main_admin.password == form.password.data:
                login_user(main_admin, remember=form.remember.data)
                return redirect(url_for('signup'))
        return render_template('pages/feedback.html',feedback = "Invalid Username or Password")
    return render_template('auth/login.html', form=form)


# Register Page Route
@app.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the Token exists
        try:
            token = uuid.uuid1().hex
            while True:
                exists = db.session.query(db.session.query(User).filter_by(token=token).exists()).scalar()
                if exists:
                    token = uuid.uuid1().hex
                    continue
                break
            # Creating a new user
            new_user = User(username=form.username.data, email=form.email.data, token=str(token))
            db.session.add(new_user)
            db.session.commit()
            # Sending the email
            msg = Message("Baidu Scraper Notification!",
            sender="baiduventures@gmail.com",
            recipients=[form.email.data])
            unique_link = "http://127.0.0.1:5000/founders/"+str(token)+"/1"
            msg.html = "Hello " + str(form.username.data)+"-<br><br>" + "Click <a href =" + unique_link+ "> here </a> to visit dashboard. <br><br>"+ "If you encounter any issues copy this url: <br><br>"+ unique_link +"<br><br> Best, <br> Baidu Team"
            with app.app_context():         
                tomail.send(msg)
            return render_template('pages/feedback.html',feedback = "Successfully Registered! Please check your email for your unique link.")
        except:
            return render_template('pages/feedback.html',feedback = "Sorry. We encountered an issue while registering your account.")
    return render_template('auth/signup.html', form=form)

# Route to mark user are reached
@app.route('/reached/<token>/<int:page_num>', methods=['POST'])
def reached(token,page_num):
    for key, value in request.form.items():
        if key == "reached":
            founder = Founders.query.filter_by(id=value).first()
    if founder.send_email == 1:
        setattr(founder, 'send_email', 0)
        db.session.commit()
    else:
        setattr(founder, 'send_email', 1)
        db.session.commit()
    return redirect(url_for('founders',  page_num=page_num, token=token))

# Dashboard Route
@app.route('/founders/<token>/<int:page_num>',methods=['GET', 'POST'], defaults={"page_num": 1})
def founders(page_num, token):
    current_user = User.query.filter_by(token = token).first()
    if current_user: 
        search = FounderSearchForm(request.form)
        linkedin = Linkedin(request.form)
        search_string = search.data['search']
        email = linkedin.data['email']
        password = linkedin.data['password']
        founders= Founders.query.order_by(desc(Founders.date)).paginate(per_page=10, page=page_num, error_out=True)
        if request.method == 'POST':
            if email:
                linkedin_login.delay(email,password, current_user.username)
                founders = Founders.query.order_by(desc(Founders.date)).paginate(per_page=10, page=page_num, error_out=True)
                return render_template('pages/index.html', founders=founders, form=search, linkedin = linkedin, page=page_num, error = 0)
        if request.method == 'POST':
            if search_string:
                if search.data['select'] == 'Fullname':
                    founders = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.fullname.contains(search_string)).paginate(per_page=10, page=page_num, error_out=True)
                elif search.data['select'] == 'Added_by':
                    founders = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.added_by.contains(search_string)).paginate(per_page=10, page=page_num, error_out=True)
                elif search.data['select'] == 'Education':
                    founders = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.education.contains(search_string)).paginate(per_page=10, page=page_num, error_out=True)
                elif search.data['select'] == 'Current Company':
                    founders  = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.current_company.contains(search_string)).paginate(per_page=10, page=page_num, error_out=True)
                elif search.data['select'] == 'Past Company':
                    founders  = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.past_company.contains(search_string)).paginate(per_page=10, page=page_num, error_out=True)
                elif search.data['select'] == 'Reached_out':
                    if search_string.title() == "Yes":
                        founders  = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.send_email.contains(1)).paginate(per_page=10, page=page_num, error_out=True)
                    elif search_string.title() == "No":
                        founders  = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.send_email.contains(0)).paginate(per_page=10, page=page_num, error_out=True)
                    else:
                        founders  = Founders.query.order_by(desc(Founders.date)).filter(
                        Founders.send_email.contains(search_string)).paginate(per_page=10, page=page_num, error_out=True)
                else:
                    pass
            else:
                pass
        return render_template('pages/index.html', founders=founders, form=search, linkedin = linkedin, page=page_num, token = token, error = 0)
    else:
        return render_template('pages/feedback.html',feedback = "You are not registered yet")
  
# Route to download the data as csv
@app.route('/download')
def download():
    founders = Founders.query.all()
    rows=[]
    for founder in founders:
        rows.append(
            {
                'date': founder.date,
                'fullname': founder.fullname,
                'title': str(founder.title).strip(),
                'location': founder.location,
                'link': founder.link,
                'email': founder.email,
                'education': founder.education,
                'current_company': founder.current_company,
                'past_company': founder.past_company,
                'added_by': founder.added_by,
                'send_email': founder.send_email,
                
            }
        )
    df = pd.DataFrame(rows)
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=baidu_venture_founders.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

if __name__ == "__main__":
    app.run()


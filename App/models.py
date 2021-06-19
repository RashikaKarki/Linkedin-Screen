from BaiduApp.app import db
from flask_login import UserMixin

class Founders(db.Model):
    __tablename__ = "founders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    fullname = db.Column(db.String(50))
    title = db.Column(db.String(150))
    location = db.Column(db.String(100))
    link = db.Column(db.String(150))
    email= db.Column(db.String(150))
    education = db.Column(db.String(150))
    current_company = db.Column(db.String(50))
    past_company = db.Column(db.String(500))   
    skills = db.Column(db.String(150))
    added_by = db.Column(db.String(150))
    send_email = db.Column(db.Boolean)
    
    def __init__(self, date, fullname,title, location, link, email, education, current_company, past_company, skills, added_by, send_email ):
        self.date= date
        self.fullname = fullname
        self.title = title
        self.location = location
        self.link = link
        self.email= email
        self.education = education
        self.current_company = current_company
        self.past_company = past_company
        self.skills = skills
        self.added_by = added_by
        self.send_email = send_email

    def __repr__(self):
        return f"{self.fullname}"

class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    token = db.Column(db.String(100))

class MainAdmin(db.Model, UserMixin):
    __tablename__ = "Admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, username, password):
        self.username= username
        self.password = password

class Rejected(db.Model):
    __tablename__ = "rejected"
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(150))

    def __init__(self, link):
        self.link= link
    
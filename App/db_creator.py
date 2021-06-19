from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import os

basedir = os.path.abspath(os.path.dirname(__file__))

engine = create_engine('sqlite:///'+os.path.join(basedir,'founders.sqlite'), echo=True)

Base = declarative_base()


class Founders(db.Model):
    
    __tablename__ = "founders"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    link = db.Column(db.String(150))
    education = db.Column(db.String(150))
    experience = db.Column(db.Integer)
    email= db.Column(db.String(150))
    skills = db.Column(db.String(150))
    added_by = db.Column(db.String(150))
    send_email = db.Column(db.Boolean)

    def __init__(self, fullname, link, education, experience, email, skills, added_by, send_email):
        self.fullname = fullname
        self.link = link
        self.education = education
        self.experience = experience
        self.email = email
        self.skills = skills
        self.added_by = added_by
        self.send_email = send_email

    def __repr__(self):
        return f"{self.fullname}"




# create tables
Base.metadata.create_all(engine)
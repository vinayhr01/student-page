from enum import unique
from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 

db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Users(db.Model, UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(30), nullable=False)
    clg= db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email= db.Column(db.String(30), nullable=False, unique=True)
    date_added= db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=True,  default='default_profile_pic.png')

    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts',cascade="all,delete", backref='poster')
    notes = db.relationship('Notes',cascade="all,delete", backref='uploader')
    user_replies = db.relationship('Replies',cascade="all,delete", backref='ureplies')
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, "sha256")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _repr_(self):
        return '<Name %r>' %self.name 


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    replies = db.relationship('Replies',cascade="all,delete", backref='preplies')


class Replies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_replied = db.Column(db.DateTime, default=datetime.utcnow)
    #Foregin Key
    post_for_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    reply_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30),nullable=False)
    sem = db.Column(db.Integer)
    branch = db.Column(db.String(50),nullable=False)
    subject = db.Column(db.String(50),nullable=False)
    college = db.Column(db.String(50),nullable=False)
    module = db.Column(db.String(50),nullable=False)
    content = db.Column(db.Text, nullable=True)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    file = db.Column(db.String(200), nullable=False)
    sem = db.Column(db.Integer,default=0)
    #Foregin Key
    upload_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Subject(db.Model):
    sub_id = db.Column(db.Integer, primary_key=True)
    sem = db.Column(db.Integer)
    branch = db.Column(db.String(50),nullable=False)
    subject = db.Column(db.String(50),nullable=False)
    module = db.Column(db.String(50),nullable=False)
    year = db.Column(db.Text, nullable=False)


class Trig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(30),nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=False)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notify_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id=db.Column(db.Integer, db.ForeignKey('posts.id'))
    username = db.Column(db.String(20), nullable=False, unique=False)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)

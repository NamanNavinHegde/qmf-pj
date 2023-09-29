#!/usr/bin/python3.6

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stack = db.Column(db.String(20), nullable=False)
    version = db.Column(db.String(50), nullable=True)
    date_create = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


class Rack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assettag = db.Column(db.String(20), nullable=False)
    serialnumber = db.Column(db.String(20), nullable= True)
    stack = db.Column(db.String(20), nullable=False)
    date_create = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

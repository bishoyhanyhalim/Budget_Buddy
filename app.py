#!/usr/bin/python3

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetData.db'
db = SQLAlchemy(app)

class BudgetData(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Money_added = db.Column(db.Integer, nullable=False)
    Paid = db.Column(db.Integer, nullable=False)
    Section = db.Column(db.String(200), nullable=False)
    Date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<paid> %r' % self.id

@app.route("/", methods=['POST', 'GET'])
def home_page():
    return render_template("homepage.html", page_title="Home Page")


@app.route("/new_entry", methods=['POST', 'GET'])
def new_entry_paid():
    
    return render_template("new_entry.html", page_title="New Entry")

if __name__ == "__main__":
    app.run(port=4000, debug=True)
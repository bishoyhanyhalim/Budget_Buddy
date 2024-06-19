#!/usr/bin/python3

from flask import Flask, render_template, request, redirect,url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegestrationForm, LoginForm
from wtforms.validators import ValidationError

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'h5vmpbrhoxkv1dgjoc8ebhmhzfxhcbml'
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


@app.route("/register", methods=['GET', 'POST'])
def register():
  form = RegestrationForm()
  if form.validate_on_submit():
    flash(f'Account created for {form.username.data}!', 'success')
    return (redirect(url_for('homepage')))
  return render_template('signup.html',
                         title='register',
                         form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
  form = LoginForm()
  print()
  print(form.email.data)
  print(form.password.data)
  print()
  if form.validate_on_submit():
    print()
    print(form.email.data)
    print(form.password.data)
    print()
    if form.email.data == 'i12@gmail.com' and form.password.data == 'pAssword123':
      flash(f'Account created for {form.email.data}!', 'success')
      return (redirect(url_for('home')))
    else:
      flash('Login Unsuccessful. Please check email and password', 'danger')
      print("Login Unsuccessful. Please check email and password")
  return render_template('login.html',
                         title='register',
                         form=form)

if __name__ == "__main__":
    app.run(port=4000, debug=True)

#!/usr/bin/python3

from flask import Flask, render_template, request, redirect,url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from forms import RegestrationForm, LoginForm
from wtforms.validators import ValidationError
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime
from flask import session
from flask_login import LoginManager, login_user, logout_user
from flask_login import UserMixin
from flask_login import current_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'h5vmpbrhoxkv1dgjoc8ebhmhzfxhcbml'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetData.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
# Set the login_view attribute
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


class BudgetData(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Total_added = db.Column(db.Integer, nullable=False)
    Remainder = db.Column(db.Integer, nullable=False)
    Paid = db.Column(db.Integer, nullable=False)
    Section = db.Column(db.String(200), nullable=False)
    Date_created = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Foreign key to User


    def __repr__(self):
       return f"<BudgetData(Id={self.Id}, Total_added={self.Total_added}, Paid={self.Paid},Remainder={self.Remainder}, Section='{self.Section}', Date_created={self.Date_created}, user_id={self.user_id})>"
    
    def to_dict(self):
        return {
            'Id': self.Id,
            'user_id': self.user_id,
            'Total_added': self.Total_added,
            'Paid': self.Paid,
            'Remainder':self.Remainder,
            'Date_created':self.Date_created,
            'Section': self.Section


            # Add other fields you want to include in the JSON
        }


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
  password = db.Column(db.String(60), nullable=False)
  BudgetData = db.relationship('BudgetData', backref='user', lazy=True)

  
  def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.password}', {self.id})"

@app.route("/", methods=['POST', 'GET'])
def home_page():
    with app.app_context():
      users = User.query.all()
      print()
      print(users)
      user_id = session.get('user_id')
      if user_id:
        loadData()
    return render_template("homepage.html", page_title="Home Page", uZer_id=user_id)


@app.route("/loadcontent", methods=['GET'])
@login_required
def loadData():
  user_id = session.get('user_id')
  budgets = BudgetData.query.filter_by(user_id=user_id).all()
 
  budgets_data = [budget.to_dict() for budget in budgets]
  print("onload data ",budgets_data)
  return jsonify(budgets_data)
      
   

def calculate_total():
  user_id = session.get('user_id')
  budgets = BudgetData.query.filter_by(user_id=user_id).all()
  budgets_data = [budget.to_dict() for budget in budgets]

  total_budget = sum([budget['Total_added'] for budget in budgets_data])
  print("total_bdget sum", total_budget)

  total_spent = sum([budget['Paid'] for budget in budgets_data])
  print("tota spent sum", total_spent)
  res = total_budget - total_spent
  return res

@app.route("/remainder", methods=['POST', 'GET'])
def get_remainder():
  result = calculate_total()
  return jsonify({"remainder":result})

@app.route("/add", methods=['POST', 'GET'])
@login_required
def add():
  if current_user.is_authenticated:

    data = request.get_json()
    print()
    print(data)
    print()
    x = data.get('x')
    y = data.get('y')
    expense = data.get('expense')
    user_id = session.get('user_id')
    print("user_id:", user_id)
    result = calculate_total()
    new_entry = BudgetData(
              Total_added=x,
              Paid=y,
              Remainder=result,
              Section=expense,
              user_id=user_id  # Make sure to pass the correct user_id
          )
        
        # Add the new entry to the session and commit it to the database
    db.session.add(new_entry)
    db.session.commit()
    budget = BudgetData.query.all()
   # Query the database to fetch the newly added budget entry
    newly_added_budget = BudgetData.query.get(new_entry.Id)

    # Convert the newly added budget entry to a dictionary suitable for JSON serialization
    budget_dict = {
          "Id": newly_added_budget.Id,
          "Total_added": newly_added_budget.Total_added,
          "Paid": newly_added_budget.Paid,
          "Section": newly_added_budget.Section,
          "Remainder": newly_added_budget.Remainder,
          "Date_created": newly_added_budget.Date_created.isoformat(),  # Convert datetime to ISO format
            "user_id": newly_added_budget.user_id
      }
    print("newly added budget", budget)
    return jsonify(budget_dict)
  else:
     return jsonify({'message': "login please"})
   
@app.route("/ditems/<int:id>", methods=["DELETE"])
@login_required
def delete_record(id):
    record = BudgetData.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
        result=calculate_total()
        return jsonify({"message": "Item deleted successfully","Remainder": result}), 200
    else:
        return jsonify({"message": "Record not found"}), 404

'''@app.route("/upatingAfterDelete", methods=["POST"])
def update_remainder_data():
    data = request.get_json()
    print()
    print(data)
    print()
    x = data.get('x')
    y = data.get('y')
      # Negate y and create the BudgetData object
    paid_with_negative = y * -1
    expense = "expense_update"
    user_id = session.get('user_id')
    print("user_id:", user_id)
    result = calculate_updated_total(x, y )
    new_entry = BudgetData(
              Total_added=x,
              Paid=paid_with_negative,
              Remainder=result,
              Section=expense,
              user_id=user_id  # Make sure to pass the correct user_id
          )
        
        # Add the new entry to the session and commit it to the database
    db.session.add(new_entry)
    db.session.commit()
    budget = BudgetData.query.all()
    print(budget)
    return jsonify({"message": 'success'})
    '''

@app.route("/upitems/<int:id>", methods=["PUT"])
@login_required
def update_record(id):
    record = BudgetData.query.get(id)
    if record:
        print(record)
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        expense = data.get('expense')
         # Calculate the new remainder
        result = calculate_total()
        # Update the record's attributes
        record.Total_added = x
        record.Paid = y
        record.Remainder = result
        record.Section = expense
        # Commit the changes to the database
        db.session.commit()

        # Return the updated record details this is for api update
        updated_record = {
            "Id": record.Id,
            "Total_added": record.Total_added,
            "Paid": record.Paid,
            "Section": record.Section,
            "Remainder": record.Remainder,
            "Date_updated": record.Date_created.isoformat(),  # Assuming Date_updated is a datetime field
            "user_id": record.user_id
        }
        print("updated",updated_record)
        return jsonify(updated_record), 200
    else:
        return jsonify({"message": "Record not found"}), 404


@app.route("/new_entry", methods=['POST', 'GET'])
def new_entry_paid():
    
    return render_template("new_entry.html", page_title="New Entry")


@app.route("/register", methods=['GET', 'POST'])
def register():
  form = RegestrationForm()
  if form.validate_on_submit():
    username = form.username.data
    email = form.email.data
    password_hash = generate_password_hash(form.password.data)
    new_user = User(
            username=username,
            email=email,
            password=password_hash
        )
        
        # Add the new entry to the session and commit it to the database
    db.session.add(new_user)
    db.session.commit()
    usr = User.query.all()
    print(usr)
    flash(f'Account created for {form.username.data}!', 'success')
    return (redirect(url_for('login')))
  return render_template('signup.html',
                         title='register',
                         form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.email.data)
        print(form.password.data)
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user:
            if check_password_hash(user.password, form.password.data):
                flash(f'Account {form.email.data}!', 'success')
                login_user(user)
                session['user_id'] = current_user.id
                return redirect(url_for('home_page'))  # Ensure 'homepage' is correctly defined
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
                print("Login Unsuccessful. Please check email and password")
        else:
            flash('No account found with that email.', 'danger')
    else:
        print("Form Validation Failed")  # Debugging: Confirm form validation failed
        flash('There was an error processing your login. Please try again.', 'danger')
    
    return render_template('login.html',
                         title='Login',
                         form=form)

@app.route("/logout")
def logout():
   logout_user()
   return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(port=4000, debug=True)
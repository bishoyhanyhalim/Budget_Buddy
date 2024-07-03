#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from forms import RegestrationForm, LoginForm
from wtforms.validators import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'h5vmpbrhoxkv1dgjoc8ebhmhzfxhcbml'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetData.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class BudgetData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Total_added = db.Column(db.Integer, nullable=False)
    Remainder = db.Column(db.Integer, nullable=False)
    Paid = db.Column(db.Integer, nullable=False)
    Section = db.Column(db.String(200), nullable=False)
    Date_created = db.Column(db.DateTime, default=datetime.utcnow)
    Time_created = db.Column(
        db.String, default=datetime.now().strftime('%I:%M %p'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<BudgetData(Id={self.id}, Total_added={self.Total_added}, Paid={self.Paid}, Remainder={self.Remainder}, Section='{self.Section}', Date_created={self.Date_created}, user_id={self.user_id})>"

    def to_dict(self):
        return {
            'Id': self.id,
            'user_id': self.user_id,
            'Total_added': self.Total_added,
            'Paid': self.Paid,
            'Remainder': self.Remainder,
            'Date_created': self.Date_created,
            'Time_created': self.Time_created,
            'Section': self.Section
        }


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    BudgetData = db.relationship('BudgetData', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.password}', {self.id})"


class NoUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Total_added = db.Column(db.Integer, nullable=False)
    Remainder = db.Column(db.Integer, nullable=False)
    Paid = db.Column(db.Integer, nullable=False)
    Section = db.Column(db.String(200), nullable=False)
    Date_created = db.Column(db.DateTime, default=datetime.utcnow)
    Time_created = db.Column(
        db.String, default=datetime.now().strftime('%I:%M %p'))

    def __repr__(self):
        return f"<NoUser(Id={self.id}, Total_added={self.Total_added}, Paid={self.Paid}, Remainder={self.Remainder}, Section='{self.Section}', Date_created={self.Date_created})>"

    def to_dict(self):
        return {
            'Id': self.id,
            'Total_added': self.Total_added,
            'Paid': self.Paid,
            'Remainder': self.Remainder,
            'Date_created': self.Date_created,
            'Time_created': self.Time_created,
            'Section': self.Section
        }


@app.route("/about", methods=['POST', 'GET'])
def about():
    return render_template("landing.html", page_title="About")

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("landing.html", page_title="Home Page")

@app.route("/homepage", methods=['POST', 'GET'])
def home_page():
    user_id = session.get('user_id')
    username = None
    if current_user.is_authenticated:
        username = current_user.username
        return render_template("homepage.html", page_title="Dashboard", user_id=user_id, username=username)
    else:
        return render_template("homepage.html", page_title="Dashboard", user_id=user_id)


@app.route("/loadcontent", methods=['GET'])
def loadData():
    try:
        if current_user.is_authenticated:
            user_id = current_user.id
            budgets = BudgetData.query.filter_by(user_id=user_id).all()
        else:
            budgets = NoUser.query.all()

        budgets_data = [budget.to_dict() for budget in budgets]
        return jsonify(budgets_data)
    except Exception as e:
        print(f"Error loading data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remainder", methods=['POST', 'GET'])
def get_remainder():
    try:
        if current_user.is_authenticated:
            user_id = current_user.id
            budgets = BudgetData.query.filter_by(user_id=user_id).all()
        else:
            budgets = NoUser.query.all()

        total_budget = sum([budget.Total_added for budget in budgets])
        total_spent = sum([budget.Paid for budget in budgets])
        remainder = total_budget - total_spent

        return jsonify({"remainder": remainder})
    except Exception as e:
        print(f"Error calculating remainder: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/add", methods=['POST'])
def add():
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        expense = data.get('expense')
        date_input = data.get('date')
        time_input = data.get('time')


        if date_input:
            date_created = datetime.strptime(date_input, '%Y-%m-%d')
        else:
            date_created = datetime.utcnow()

        if time_input:
            time_created = datetime.strptime(
                time_input, '%H:%M').strftime('%I:%M %p')
        else:
            time_created = datetime.now().strftime('%I:%M %p')

        if current_user.is_authenticated:
            user_id = current_user.id
            new_entry = BudgetData(
                Total_added=x,
                Paid=y,
                # Set remainder for BudgetData (customize as needed)
                Remainder=0,
                Date_created=date_created,
                Time_created=time_created,
                Section=expense,
                user_id=user_id
            )

            db.session.add(new_entry)
            db.session.commit()

            budget = BudgetData.query.all()
        # Query the database to fetch the newly added budget entry
            newly_added_budget = BudgetData.query.get(new_entry.id)

            # Convert the newly added budget entry to a dictionary suitable for JSON serialization
            budget_dict = {
                "Id": newly_added_budget.id,
                "Total_added": newly_added_budget.Total_added,
                "Paid": newly_added_budget.Paid,
                "Section": newly_added_budget.Section,
                "Remainder": newly_added_budget.Remainder,
                "Date_created": newly_added_budget.Date_created,
                "Time_created": newly_added_budget.Time_created,
                "user_id": newly_added_budget.user_id
            }
            print("newly added budget", budget)
            return jsonify(budget_dict)

        else:
            new_entry = NoUser(
                Total_added=x,
                Paid=y,
                Remainder=0,  # Set remainder for NoUser (customize as needed)
                Date_created=date_created,
                Time_created=time_created,
                Section=expense
            )

            db.session.add(new_entry)
            db.session.commit()

            budget = NoUser.query.all()
        # Query the database to fetch the newly added budget entry
            newly_added_budget = NoUser.query.get(new_entry.id)

            # Convert the newly added budget entry to a dictionary suitable for JSON serialization
            budget_dict = {
                "Id": newly_added_budget.id,
                "Total_added": newly_added_budget.Total_added,
                "Paid": newly_added_budget.Paid,
                "Section": newly_added_budget.Section,
                "Remainder": newly_added_budget.Remainder,
                "Date_created": newly_added_budget.Date_created,
                "Time_created": newly_added_budget.Time_created
            }
            print("newly added budget", budget)
            return jsonify(budget_dict)

        # return jsonify({'message': 'Data saved successfully'})
    except Exception as e:
        print(f"Error adding data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/ditems/<int:id>", methods=["DELETE"])
def delete_record(id):
    try:
        if current_user.is_authenticated:
            record = BudgetData.query.get(id)
        else:
            record = NoUser.query.get(id)

        if record:
            db.session.delete(record)
            db.session.commit()
            return jsonify({"message": "Item deleted successfully"}), 200
        else:
            return jsonify({"message": "Record not found"}), 404
    except Exception as e:
        print(f"Error deleting record: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/upitems/<int:id>", methods=["PUT"])
def update_record(id):
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        expense = data.get('expense')
        date_input = data.get('date')
        time_input = data.get('time')

        if date_input:
            date_created = datetime.strptime(date_input, '%Y-%m-%d')
        else:
            date_created = datetime.utcnow()

        if time_input:
            time_created = datetime.strptime(
                time_input, '%H:%M').strftime('%I:%M %p')
        else:
            time_created = datetime.now().strftime('%I:%M %p')

        if current_user.is_authenticated:
            record = BudgetData.query.get(id)
        else:
            record = NoUser.query.get(id)

        if record:
            record.Total_added = x
            record.Paid = y
            record.Section = expense
            record.Date_created = date_created
            record.Time_created = time_created

            db.session.commit()

            return jsonify({'message': 'Record updated successfully'}), 200
        else:
            return jsonify({"message": "Record not found"}), 404
    except Exception as e:
        print(f"Error updating record: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegestrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password_hash = generate_password_hash(form.password.data)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('This username already exists.', 'danger')
            return redirect(url_for('register'))
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('This email already exists.', 'danger')
            return redirect(url_for('register'))
        user = User(username=username, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data  # Use email input
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for('home_page'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')

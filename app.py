#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from forms import RegestrationForm, LoginForm  # Importing forms for user
from wtforms.validators import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
import io  # For handling file streams
import os
from weasyprint import HTML, CSS  # PDF generation


# Initialize Flask application
app = Flask(__name__)
# Secret key for session
app.config['SECRET_KEY'] = 'h5vmpbrhoxkv1dgjoc8ebhmhzfxhcbml'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetData.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set login view for authentication


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class BudgetData(db.Model):
    """ BudgetData model for storing budget entries linked to users """
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
    """User model for storing user information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    BudgetData = db.relationship('BudgetData', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.password}', {self.id})"


@app.route("/about", methods=['POST', 'GET'])
def about():
    """Route for About page"""

    return render_template("landing.html", page_title="About")


@app.route("/", methods=['POST', 'GET'])
def home():
    """Route for Home page (landing page)"""

    return render_template("landing.html", page_title="Home Page")


@app.route("/homepage", methods=['POST', 'GET'])
def home_page():
    """Route for Dashboard page
        # Display dashboard with user-specific data if logged in 
        # Otherwise, display guest data
    """

    user_id = session.get('user_id')
    username = None
    if current_user.is_authenticated:
        username = current_user.username
        return render_template("homepage.html", page_title="Dashboard", user_id=user_id, username=username)
    else:
        return render_template("homepage.html", page_title="Dashboard", user_id=user_id)


@app.route("/loadcontent", methods=['GET'])
def loadData():
    """Route for fetching budget data"""

    try:
        if current_user.is_authenticated:
            user_id = current_user.id
            budgets = BudgetData.query.filter_by(user_id=user_id).all()
            budgets_data = [budget.to_dict() for budget in budgets]
        else:
            guest_budgets = session.get('guest_budgets', [])
            budgets_data = guest_budgets

        return jsonify(budgets_data)

    except Exception as e:
        print(f"Error loading data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remainder", methods=['POST', 'GET'])
def get_remainder():
    """Route for calculating and returning remainder"""

    try:
        if current_user.is_authenticated:
            user_id = current_user.id
            budgets = BudgetData.query.filter_by(user_id=user_id).all()
            total_budget = sum(budget.Total_added for budget in budgets)
            total_spent = sum(budget.Paid for budget in budgets)
        else:
            guest_budgets = session.get('guest_budgets', [])
            total_budget = sum(budget['Total_added']
                               for budget in guest_budgets)
            total_spent = sum(budget['Paid'] for budget in guest_budgets)

        remainder = total_budget - total_spent

        return jsonify({"remainder": remainder})
    except Exception as e:
        print(f"Error calculating remainder: {e}")
        return jsonify({"error": str(e)}), 500


def not_section(Section_Name):
    """Function to handle cases where no section name is provided"""

    if len(Section_Name) < 1:
        return "No Section Added"
    else:
        return (Section_Name)


@app.route("/add", methods=['POST'])
def add():
    """Route for adding a new budget entry"""

    try:
        data = request.get_json()
        new_money_added = data.get('x')
        new_paid = data.get('y')
        expense = data.get('expense')
        date_input = data.get('date')
        time_input = data.get('time')

        if (new_money_added < 0) or (new_paid < 0):
            return jsonify({"error": "Total added and Paid must be greater than 0"}), 400

        if date_input:
            date_created = datetime.strptime(date_input, '%Y-%m-%d')
        else:
            date_created = datetime.utcnow()

        if time_input:
            time_created = datetime.strptime(
                time_input, '%H:%M').strftime('%I:%M %p')
        else:
            time_created = datetime.now().strftime('%I:%M %p')

        # Check if user is authenticated and add budget entry accordingly
        if current_user.is_authenticated:
            user_id = current_user.id
            new_entry = BudgetData(
                Total_added=new_money_added,
                Paid=new_paid,
                Remainder=0,
                Date_created=date_created,
                Time_created=time_created,
                Section=not_section(expense),
                user_id=user_id
            )

            db.session.add(new_entry)
            db.session.commit()

            # Fetch the newly added budget entry using session.get()
            newly_added_budget = db.session.get(BudgetData, new_entry.id)

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
            print("newly added budget", budget_dict)
            return jsonify(budget_dict)

        else:
            guest_budgets = session.get('guest_budgets', [])
            new_entry = {
                "Id": len(guest_budgets) + 1,
                "Total_added": new_money_added,
                "Paid": new_paid,
                "Remainder": 0,
                "Date_created": date_created,
                "Time_created": time_created,
                "Section": not_section(expense)
            }
            guest_budgets.append(new_entry)
            session['guest_budgets'] = guest_budgets
            budget_dict = new_entry

            print("newly added budget", budget_dict)
            return jsonify(budget_dict)

    except Exception as e:
        print(f"Error adding data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/ditems/<int:id>", methods=["DELETE"])
def delete_record(id):
    """Route for deleting a budget record"""
    try:
        if current_user.is_authenticated:
            record = BudgetData.query.get(id)
            if record:
                db.session.delete(record)
                db.session.commit()
                return jsonify({"message": "Item deleted successfully"}), 200
            else:
                return jsonify({"message": "Record not found"}), 404

        else:
            guest_budgets = session.get('guest_budgets', [])
            updated_guest_budgets = [
                budget for budget in guest_budgets if budget["Id"] != id]

            if len(updated_guest_budgets) == len(guest_budgets):
                return jsonify({"message": "Record not found"}), 404

            session['guest_budgets'] = updated_guest_budgets
            return jsonify({"message": "Item deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting record: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/upitems/<int:id>", methods=["PUT"])
def update_record(id):
    """Route for updating a budget record"""

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

        # Check if user is authenticated and update budget record
        if current_user.is_authenticated:
            record = BudgetData.query.get(id)
            if record:
                record.Total_added = x
                record.Paid = y
                record.Section = not_section(expense)
                record.Date_created = date_created
                record.Time_created = time_created

                db.session.commit()
                return jsonify({'message': 'Record updated successfully'}), 200
            else:
                return jsonify({"message": "Record not found"}), 404

        else:
            guest_budgets = session.get('guest_budgets', [])
            for budget in guest_budgets:
                if budget['Id'] == id:
                    budget['Total_added'] = x
                    budget['Paid'] = y
                    budget['Section'] = not_section(expense)
                    budget['Date_created'] = date_created
                    budget['Time_created'] = time_created
                    session['guest_budgets'] = guest_budgets
                    return jsonify({'message': 'Record updated successfully'}), 200

            return jsonify({"message": "Record not found"}), 404

    except Exception as e:
        print(f"Error updating record: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/pdf", methods=['GET', 'POST'])
@app.route("/pdf/<int:user_id>", methods=['GET', 'POST'])
def show_pdf_data(user_id=None):
    """Route for displaying PDF data"""

    if current_user.is_authenticated:
        if user_id and current_user.id == user_id:
            budgets = BudgetData.query.filter_by(user_id=user_id).all()
        else:
            budgets = BudgetData.query.filter_by(user_id=current_user.id).all()

        total_budget_added = sum(
            budget.Total_added for budget in budgets if budget.Total_added is not None)
        total_money_spent = sum(
            budget.Paid for budget in budgets if budget.Paid is not None)

        total_budget_now = total_budget_added - total_money_spent

    else:
        budgets = session.get('guest_budgets', [])

        total_budget_added = sum(
            budget['Total_added'] for budget in budgets if budget.get('Total_added') is not None)
        total_money_spent = sum(
            budget['Paid'] for budget in budgets if budget.get('Paid') is not None)

        total_budget_now = total_budget_added - total_money_spent

    return render_template('pdf_page.html', page_title="pdf",
                           budgets=budgets,
                           total_budget_added=total_budget_added,
                           total_money_spent=total_money_spent,
                           total_budget_now=total_budget_now)


@app.route("/generate_pdf", methods=['GET', 'POST'])
@app.route('/generate_pdf/<int:user_id>', methods=['GET', 'POST'])
def generate_pdf(user_id=None):
    """Route for generating and downloading PDF"""

    username = None

    download_time = datetime.now().strftime('(%I-%M %p) _ (%Y-%m-%d)')

    if current_user.is_authenticated:
        if user_id and current_user.id == user_id:
            budgets = BudgetData.query.filter_by(user_id=user_id).all()
        else:
            budgets = BudgetData.query.filter_by(user_id=current_user.id).all()

        total_budget_added = sum(
            budget.Total_added for budget in budgets if budget.Total_added is not None)
        total_money_spent = sum(
            budget.Paid for budget in budgets if budget.Paid is not None)

        total_budget_now = total_budget_added - total_money_spent

    else:
        budgets = session.get('guest_budgets', [])

        total_budget_added = sum(
            budget['Total_added'] for budget in budgets if budget.get('Total_added') is not None)
        total_money_spent = sum(
            budget['Paid'] for budget in budgets if budget.get('Paid') is not None)

        total_budget_now = total_budget_added - total_money_spent

    if current_user.is_authenticated:
        username = current_user.username

    # Render the HTML template
    html = render_template('pdf_download.html',
                           budgets=budgets,
                           username=username,
                           total_budget_added=total_budget_added,
                           total_money_spent=total_money_spent,
                           total_budget_now=total_budget_now)

    # Construct the path for the CSS file
    css_path = os.path.join(app.root_path, 'static', 'css', 'pdf_page.css')

    # Convert the HTML to PDF with the CSS
    pdf = HTML(string=html).write_pdf(stylesheets=[CSS(css_path)])

    # Create a BytesIO object to send the PDF as a response
    pdf_io = io.BytesIO(pdf)
    pdf_io.seek(0)

    return send_file(pdf_io, download_name=f'Expenses sheet at {download_time}.pdf', as_attachment=True)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """Route for user registration"""

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
    """Route for user login"""

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
    """Route for user logout"""

    logout_user()
    session.pop('user_id', None)
    session.pop('guest_budgets', None)  # Clear guest budgets on logout
    return redirect(url_for('home_page'))


# Run the application if executed directly
if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')

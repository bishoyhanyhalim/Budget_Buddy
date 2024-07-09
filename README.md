# Budget Buddy

Welcome to **Budget Buddy**, your go-to application for managing your finances easily!


## Introduction

Budget Buddy is a Flask application that provides various features for budget management. It includes user registration, login, PDF generation, and CRUD (Create, Read, Update, Delete) operations on budget data. The application leverages SQLAlchemy for database operations, Flask-Login for user session management, and WeasyPrint for PDF generation.


### Authors

- Bishoy Hany Halim: [LinkedIn](https://www.linkedin.com/in/bishoy-hany-halim/)
- Reham Elsyed: [LinkedIn](https://www.linkedin.com/in/reham-shepl-1808811b3/)


## Installation

To set up Budget Buddy on your local machine, follow these steps:

1. Clone the repository to your computer.
2. Open your project terminal and navigate to the project directory.
3. Run the following command to create the database tables:
   ```
   python3
   ```
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
   ```
   Press `Ctrl+D` to exit the Python shell.
   

## Usage

1. Start the application by running:
   ```
   python3 app.py
   ```
2. Open your web browser and visit [http://127.0.0.1:5000](http://127.0.0.1:5000).


## Challenges

1. User Authentication: Implementing secure user registration and login was crucial. We dove into Flask-Login and hashed passwords like our lives depended on it.
2. Database Design: Our database schema must accommodate various budget categories, transactions, and user profiles. SQLAlchemy’s ORM came to the rescue.
3. PDF Reports: Generating beautiful PDF reports from budget data was challenging. We explored different libraries and settled on WeasyPrint for its flexibility.


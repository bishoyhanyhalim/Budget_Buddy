Welcome to Budget Buddy

Manage Your Finances Easily

Created By :
--> Bishoy Hany Halim  <https://www.linkedin.com/in/bishoy-hany-halim/>

--> Reham Elsyed  <https://www.linkedin.com/in/reham-shepl-1808811b3/>



This Flask application defines routes and functions for user registration, login, budget management, PDF generation, and CRUD operations on budget data.

It utilizes SQLAlchemy for database operations, Flask-Login for user session management, and WeasyPrint for PDF generation.

Each route handles specific tasks such as rendering templates, processing form data, and interacting with the database based on user authentication status.



How to use our app ?
You can using app on website By this link: https://probudgetbuddy.pythonanywhere.com/

OR 

Download files on your computer
then to set up database your can follow this steps :

in your project file terminal , write "python3"

then write this commands:


from app import app, db

with app.app_context():
    db.create_all()

then press Ctrl+D


now you setup database

now in your project terminal write:

--->  python3 app.py

then open your Browser and write :

---> http://127.0.0.1:5000
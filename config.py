from app import app, db  # Adjust the import path according to your project structure

with app.app_context():
    db.create_all()
 

# Now, let's add BudgetData instances and associate them with the users

# Commit the transactions to save the BudgetData instances to the database
    db.session.commit()
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database with the Flask app.
    Call this function in your app setup to bind the db instance to your app.
    """
    db.init_app(app)
    

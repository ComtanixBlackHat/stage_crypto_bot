
from flask import Flask , render_template 
from app.config import Config , make_celery
from app.database import db, init_db

# from flask import Blueprint, request, jsonify, render_template 
from app.routes.trading_pair_routes import trading_pair_routes
from app.routes.position_routes import position_routes
# from app.routes.transaction_routes import transaction_routes
from app.routes.auth.user_routes import auth
from app.routes.exchangeRoutes import kraken_routes
from app.routes.botRoutes import botRoutes  
from flask import Flask, send_from_directory
from flask_login import LoginManager , UserMixin
from flask_jwt_extended import JWTManager
from werkzeug.wrappers import Response
from werkzeug.utils import redirect
from app.routes.auth.users import load_user
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database URI
    # Database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://karakin:botdatabase991122@localhost:3306/karakin_db'

    # Initialize the database with the app
    init_db(app)
    jwt = JWTManager(app)
    # app = Flask(__name__, static_folder="static")
    app.config['SECRET_KEY'] = 'verySucoreScretKyeaojhsf9y49813rhajsnf;akjfhs983rha;jehr9q3p8r375rhasjhfvakjhsfvkajh'

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Ensure the correct route
    @login_manager.user_loader
    def load_user_from_id(username):
        return load_user(username)

    app.register_blueprint(auth)

    class Middleware:
        """Custom WSGI middleware for logging and modifying requests."""
        
        def __init__(self, app):
            self.original_app = app  # Store the original Flask app

        def __call__(self, environ, start_response):
            """This method runs before every request."""
            path = environ.get('PATH_INFO', '')
            method = environ.get('REQUEST_METHOD', '')

            # Flask's session needs the app context, but we access it from cookies here
            user_id = environ.get("HTTP_COOKIE", "").split("session=")[-1] if "HTTP_COOKIE" in environ else None
            # Skip authentication for the login page
            if path.startswith("/login"):
                return self.original_app(environ, start_response)
            
            if user_id:
                print(f"[WSGI MIDDLEWARE] User exists: {user_id}")
            else:
                print("[WSGI MIDDLEWARE] No user logged in - Redirecting to login")
                response = redirect("/login")  # Redirect to login page
                return response(environ, start_response)
                

            # Example: Modify headers (Adding a security header)
            def custom_start_response(status, headers, exc_info=None):
                headers.append(("X-Security-Header", "MyCustomValue"))
                return start_response(status, headers, exc_info)

            # Call the original app
            return self.original_app(environ, custom_start_response)

    # Apply middleware correctly
    app.wsgi_app = Middleware(app.wsgi_app)  # Wrap only the original WSGI ap

    # @app.route('/')
    # def home():
    #     return "Welcome to the Flask App!"

    # if __name__ == '__main__':
    #     app.run(debug=True)
    # app.register_blueprint(user_routes, url_prefix='/api/users')
    app.register_blueprint(trading_pair_routes, url_prefix='/api/trading_pairs')
    app.register_blueprint(position_routes, url_prefix='/api/positions')
    app.register_blueprint(kraken_routes, url_prefix='/api')
    app.register_blueprint(botRoutes, url_prefix='/bot')
    # app.register_blueprint(transaction_routes, url_prefix='/api/transactions')

    @app.route('/', methods=['GET'])
    def login_page():
        return render_template('dashboard.html')   
    @app.route('/detail', methods=['GET'])
    def detailpage():
        return render_template('pairDetail.html') 
    
    @app.route('/history', methods=['GET'])
    def historypage():
        return render_template('history.html') 
    # Ensure database connection is successful within app context
    with app.app_context():
        try:
            from sqlalchemy.sql import text  # Import text from SQLAlchemy

            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("Database connection successful.")
            db.create_all()
        except Exception as e:
            print(f"Database connection failed: {e}")

    return app

# ----------------------------------------------------------------------------------------

def bot_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database URI
    # Database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://karakin:botdatabase991122@localhost:3306/karakin_db'
# Configure Celery
    # app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    # app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    # # Initialize Celery
    # celery = make_celery(app)

    # Initialize the database with the app
    init_db(app)

    app.register_blueprint(botRoutes, url_prefix='/bot')



    # Ensure database connection is successful within app context
    with app.app_context():
        try:
            from sqlalchemy.sql import text  # Import text from SQLAlchemy

            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("Database connection successful.")
            db.create_all()
        except Exception as e:
            print(f"Database connection failed: {e}")

    return app



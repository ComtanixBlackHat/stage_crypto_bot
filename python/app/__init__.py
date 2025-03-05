
from flask import Flask , render_template 
from app.config import Config
from app.database import db, init_db

# from flask import Blueprint, request, jsonify, render_template 
from app.routes.trading_pair_routes import trading_pair_routes
from app.routes.position_routes import position_routes
# from app.routes.transaction_routes import transaction_routes
from app.routes.auth.user_routes import user_routes
from app.routes.exchangeRoutes import kraken_routes
from app.routes.botRoutes import botRoutes  
from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
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

    app.register_blueprint(user_routes, url_prefix='/api/users')
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



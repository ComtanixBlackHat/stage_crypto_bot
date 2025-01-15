from flask import Blueprint, request, jsonify, render_template 
from app import db
from app.models import User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bcrypt = Bcrypt()
user_routes = Blueprint('user_routes', __name__)

# Render Registration Page
@user_routes.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# Handle User Registration (POST)
@user_routes.route('/register', methods=['POST'])
def register_user():
    data = request.form  # Use request.form for form data from POST request

    # Check if the required data is provided
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    # Hash the password before saving it
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Create a new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Login User API
@user_routes.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    # Check if the required data is provided
    if not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    # Find the user by username
    user = User.query.filter_by(username=data['username']).first()

    # If user not found or password is incorrect
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    # Create an access token (JWT)
    access_token = create_access_token(identity=user.id)

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200

# Render Login Page
@user_routes.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

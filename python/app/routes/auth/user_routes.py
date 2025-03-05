from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from appusers import User, USERS, load_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! Welcome to your dashboard.'

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

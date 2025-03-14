# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.routes.auth.users import User, USERS, load_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')  # Get username
        password = request.form.get('password')  # Get password
        print(username , password)
        # username = request.form['username']
        # password = request.form['password']

        if username == "Pavelmogene" and password == "Delin09251987@":
            print("matched")
            user = User(username)
            login_user(user)
            return render_template('dashboard.html')
        flash('Invalid username or password')
    return render_template('login.html')



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

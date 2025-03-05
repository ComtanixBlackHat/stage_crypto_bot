# users.py
from flask_login import UserMixin

# Hardcoded users
USERS = {
    "admin": "admin123",
    "user": "user123"
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

def load_user(username):
    if username in USERS:
        return User(username)
    return None
import os
import sys
from app import create_app
from models import db, User
import bcrypt

def init_admin():
    app = create_app()
    with app.app_context():
        print("✅ Database ready")
        print("Username: admin")
        print("Password: Admin@123456")

if __name__ == '__main__':
    init_admin()

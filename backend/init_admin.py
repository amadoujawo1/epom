import os
import sys
from app import create_app
from models import db, User
import bcrypt

def init_admin():
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        hashed_password = bcrypt.hashpw(b'Admin@123456', bcrypt.gensalt()).decode('utf-8')
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=hashed_password,
            first_name='Admin',
            last_name='User',
            role='Admin',
            department='Administration',
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: Admin@123456")

if __name__ == '__main__':
    init_admin()

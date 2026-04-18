#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
Creates all database tables and initial admin user
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize database tables and create admin user"""
    try:
        # Import after loading environment
        from app import create_app
        from models import db, User
        
        # Create app and database context
        app = create_app()
        
        with app.app_context():
            print("Creating database tables...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Creating default admin user...")
                import bcrypt
                
                # Create admin user with default password
                admin_user = User(
                    username='admin',
                    email='admin@epom.local',
                    first_name='System',
                    last_name='Administrator',
                    role='Admin',
                    is_active=True,
                    must_change_password=True
                )
                admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Please change this password after first login!")
            else:
                print("✅ Admin user already exists")
                
            print("\n🎉 Database initialization completed successfully!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_database()

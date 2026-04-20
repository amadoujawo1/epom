#!/usr/bin/env python3
"""
Complete Database Fix for e-POM
Fixes SQLite database schema issues and creates fresh database
"""

import os
import sys
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def fix_database():
    """Complete database fix"""
    print("=== E-POM Database Fix ===")
    
    # Database files to remove
    db_files = [
        'epom_dev.db',
        'backend/instance/epom_dev.db',
        'instance/epom_dev.db'
    ]
    
    # Remove all database files
    print("1. Removing old database files...")
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"   Removed: {db_file}")
            except Exception as e:
                print(f"   Could not remove {db_file}: {e}")
        else:
            print(f"   Not found: {db_file}")
    
    # Remove instance directories
    instance_dirs = ['backend/instance', 'instance']
    for dir_path in instance_dirs:
        if os.path.exists(dir_path):
            try:
                os.rmdir(dir_path)
                print(f"   Removed directory: {dir_path}")
            except Exception as e:
                print(f"   Could not remove directory {dir_path}: {e}")
    
    # Create fresh database
    print("\n2. Creating fresh database...")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///epom_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Import models to ensure they're registered
    try:
        from models import User, Event, Document, Action, Project, Notification, Resource, AttendanceRecord, DocumentAudit
        print("   Models imported successfully")
    except ImportError as e:
        print(f"   Error importing models: {e}")
        return False
    
    # Create all tables
    print("   Creating database tables...")
    with app.app_context():
        try:
            db.create_all()
            print("   Database tables created successfully!")
            
            # Create admin user
            print("   Creating admin user...")
            admin_user = User(
                username='admin',
                email='admin@epom.local',
                first_name='System',
                last_name='Administrator',
                role='Admin',
                is_active=True,
                must_change_password=True
            )
            
            # Import bcrypt for password hashing
            import bcrypt
            admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            db.session.add(admin_user)
            db.session.commit()
            print("   Admin user created successfully!")
            
            # Verify admin user
            verify_user = User.query.filter_by(username='admin').first()
            if verify_user:
                print(f"   Admin user verified: {verify_user.username}")
                print(f"   Login credentials: admin/admin123")
            else:
                print("   Admin user verification failed!")
                return False
            
            print("\n3. Database fix completed successfully!")
            print("   You can now start the app with: python app.py")
            print("   Login with: username='admin', password='admin123'")
            return True
            
        except Exception as e:
            print(f"   Error creating database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_database()
    if success:
        print("\n=== SUCCESS: Database fixed! ===")
        sys.exit(0)
    else:
        print("\n=== ERROR: Database fix failed ===")
        sys.exit(1)

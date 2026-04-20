#!/usr/bin/env python3
"""
Simple Database Reset for e-POM
"""

import os
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def reset_database():
    print("=== Simple Database Reset ===")
    
    # Remove all database files
    db_files = ['epom_dev.db', 'backend/instance/epom_dev.db', 'instance/epom_dev.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"Removed: {db_file}")
            except Exception as e:
                print(f"Could not remove {db_file}: {e}")
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///epom_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Import models
    from models import User, Event, Document, Action, Project, Notification, Resource, AttendanceRecord, DocumentAudit
    
    # Create tables
    with app.app_context():
        try:
            # Drop all tables first
            db.drop_all()
            print("Dropped all tables")
            
            # Create all tables
            db.create_all()
            print("Created all tables")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables created: {tables}")
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@epom.local',
                first_name='System',
                last_name='Administrator',
                role='Admin',
                is_active=True,
                must_change_password=True
            )
            
            import bcrypt
            admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
            
            # Verify admin user
            verify_user = User.query.filter_by(username='admin').first()
            if verify_user:
                print(f"Admin user verified: {verify_user.username}")
                print("Database reset completed successfully!")
                print("Login credentials: admin/admin123")
                return True
            else:
                print("Admin user verification failed!")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    reset_database()

#!/usr/bin/env python3
"""
Database Reset Script for e-POM
Fixes SQLite database schema issues by recreating database with correct schema
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User, Event, Document, Action, Project, Notification, Resource, AttendanceRecord, DocumentAudit

def reset_database():
    """Reset database with correct schema"""
    print("🔄 Resetting e-POM database...")
    
    # Remove old database file if it exists
    db_file = 'epom_dev.db'
    if os.path.exists(db_file):
        print(f"🗑️ Removing old database: {db_file}")
        os.remove(db_file)
        print("✅ Old database removed")
    
    # Create Flask app and database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///epom_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Import models to ensure they're registered
    from models import User, Event, Document, Action, Project, Notification, Resource, AttendanceRecord, DocumentAudit
    
    # Drop all tables and recreate with correct schema
    print("📝 Dropping existing tables...")
    with app.app_context():
        db.drop_all()
        print("✅ All tables dropped!")
        
        print("📝 Creating database tables with correct schema...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create admin user
        print("👤 Creating admin user...")
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
        print("✅ Admin user created successfully!")
        
        # Verify admin user
        verify_user = User.query.filter_by(username='admin').first()
        if verify_user:
            print(f"✅ Admin user verified: {verify_user.username}")
            print(f"🔑 Login credentials: admin/admin123")
        else:
            print("❌ Admin user verification failed!")
    
    print("🎉 Database reset complete!")
    print("🌐 You can now start the app with: python app.py")
    print("🔐 Login with: username='admin', password='admin123'")

if __name__ == '__main__':
    reset_database()

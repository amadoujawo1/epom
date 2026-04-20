#!/usr/bin/env python3
"""
Create test users for the e-POM system
This will populate the database with sample personnel for testing
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User
from app import create_app

def create_test_users():
    """Create test users for the system"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating test users...")
        
        # Check if users already exist
        existing_users = User.query.all()
        if len(existing_users) > 1:
            print(f"✅ {len(existing_users)} users already exist in database")
            for user in existing_users:
                print(f"   - {user.username} ({user.role})")
            return
        
        # Test users with different roles
        test_users = [
            {
                "username": "jminister",
                "email": "minister@epom.gov",
                "first_name": "John",
                "last_name": "Minister",
                "role": "Minister",
                "password": "test123",
                "department": "Executive Office"
            },
            {
                "username": "schief",
                "email": "chief@epom.gov", 
                "first_name": "Sarah",
                "last_name": "Chief",
                "role": "Chief of staff",
                "password": "test123",
                "department": "Executive Office"
            },
            {
                "username": "aadvisor",
                "email": "advisor@epom.gov",
                "first_name": "Ahmed",
                "last_name": "Advisor", 
                "role": "Advisor",
                "password": "test123",
                "department": "Strategic Planning"
            },
            {
                "username": "pprotocol",
                "email": "protocol@epom.gov",
                "first_name": "Patricia",
                "last_name": "Protocol",
                "role": "Protocol",
                "password": "test123", 
                "department": "Diplomatic Services"
            },
            {
                "username": "aassistant",
                "email": "assistant@epom.gov",
                "first_name": "Alex",
                "last_name": "Assistant",
                "role": "Assistant",
                "password": "test123",
                "department": "Administrative Support"
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            # Check if user already exists
            existing = User.query.filter_by(username=user_data["username"]).first()
            if existing:
                print(f"⚠️  User {user_data['username']} already exists")
                continue
                
            # Create new user
            import bcrypt
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                department=user_data["department"],
                is_active=True,
                must_change_password=False
            )
            new_user.password_hash = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            db.session.add(new_user)
            created_count += 1
            print(f"✅ Created user: {user_data['username']} ({user_data['role']})")
        
        try:
            db.session.commit()
            print(f"🎉 Successfully created {created_count} test users!")
            
            # Verify users were created
            all_users = User.query.all()
            print(f"📊 Total users in database: {len(all_users)}")
            for user in all_users:
                print(f"   - {user.username} ({user.role}) - {user.first_name} {user.last_name}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating users: {e}")

if __name__ == "__main__":
    create_test_users()

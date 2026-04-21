#!/usr/bin/env python3
"""
Update user roles to match the new organizational structure:
- Admin
- Minister
- Chief of staff
- Advisor
- Protocol
- Assistant
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import sqlite3
import bcrypt
from flask_sqlalchemy import SQLAlchemy

# Initialize database directly
db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')

# Create a simple User class for the update
class User:
    def __init__(self, id, username, first_name, last_name, email, role, is_active=True):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role
        self.is_active = is_active

def update_user_roles():
    """Update existing user roles to match new organizational structure"""
    
    # Role mapping from old to new
    role_mapping = {
        'Staff': 'Assistant',
        'Leader': 'Advisor',
        'Admin': 'Admin',  # Keep Admin as is
        'Minister': 'Minister',
        'Chief of staff': 'Chief of staff',
        'Advisor': 'Advisor',
        'Protocol': 'Protocol',
        'Assistant': 'Assistant'
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all users
        cursor.execute("SELECT id, username, first_name, last_name, email, role, is_active FROM users")
        users_data = cursor.fetchall()
        
        users = []
        for row in users_data:
            user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            users.append(user)
        
        print(f"Found {len(users)} users in database")
        
        updated_count = 0
        for user in users:
            old_role = user.role
            new_role = role_mapping.get(old_role, 'Assistant')  # Default to Assistant
            
            if old_role != new_role:
                print(f"Updating user '{user.username}' from '{old_role}' to '{new_role}'")
                cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user.id))
                updated_count += 1
            else:
                print(f"User '{user.username}' already has correct role: '{new_role}'")
        
        if updated_count > 0:
            conn.commit()
            print(f"\nSuccessfully updated {updated_count} users")
        else:
            print("\nNo users needed updating")
        
        # Display current role distribution
        print("\nCurrent role distribution:")
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        role_data = cursor.fetchall()
        
        for role, count in role_data:
            print(f"  {role}: {count} users")
            
    finally:
        conn.close()

def create_sample_users():
    """Create sample users with the new roles if they don't exist"""
    
    sample_users = [
        {
            'username': 'minister',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'minister@epom.local',
            'role': 'Minister',
            'password': 'Minister123'
        },
        {
            'username': 'chief_of_staff',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'chief@epom.local',
            'role': 'Chief of staff',
            'password': 'Chief123'
        },
        {
            'username': 'advisor',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'email': 'advisor@epom.local',
            'role': 'Advisor',
            'password': 'Advisor123'
        },
        {
            'username': 'protocol',
            'first_name': 'David',
            'last_name': 'Wilson',
            'email': 'protocol@epom.local',
            'role': 'Protocol',
            'password': 'Protocol123'
        },
        {
            'username': 'assistant',
            'first_name': 'Emily',
            'last_name': 'Davis',
            'email': 'assistant@epom.local',
            'role': 'Assistant',
            'password': 'Assistant123'
        }
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        created_count = 0
        
        for user_data in sample_users:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (user_data['username'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                print(f"User '{user_data['username']}' already exists")
                continue
            
            print(f"Creating user '{user_data['username']}' with role '{user_data['role']}'")
            
            hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (username, first_name, last_name, email, password_hash, role, is_active, must_change_password, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                user_data['username'],
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                hashed_password,
                user_data['role'],
                True,
                True
            ))
            
            created_count += 1
        
        if created_count > 0:
            conn.commit()
            print(f"\nSuccessfully created {created_count} sample users")
        else:
            print("\nNo new sample users created")
            
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== USER ROLES UPDATE ===")
    print("Updating user roles to new organizational structure...")
    
    try:
        update_user_roles()
        print("\n" + "="*50)
        print("Creating sample users with new roles...")
        create_sample_users()
        print("\n" + "="*50)
        print("User roles update completed successfully!")
        
        print("\nNew role structure:")
        print("- Admin")
        print("- Minister")
        print("- Chief of staff")
        print("- Advisor")
        print("- Protocol")
        print("- Assistant")
        
    except Exception as e:
        print(f"Error updating user roles: {e}")
        sys.exit(1)

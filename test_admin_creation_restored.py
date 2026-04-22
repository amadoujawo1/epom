#!/usr/bin/env python3
"""
Test the restored admin user creation functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5007"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_as_admin():
    """Login as admin and get token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token'), data.get('user')
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Login error: {e}")
        return None, None

def test_create_user():
    """Test creating a new user with admin token"""
    print("=== TESTING ADMIN USER CREATION ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Login as admin
    print("1. Admin login...")
    token, admin_user = login_as_admin()
    if not token:
        print("   Admin login failed!")
        return False
    
    print(f"   Admin login successful! User: {admin_user}")
    
    # Test creating a new user
    print("\n2. Creating new user...")
    test_user_data = {
        "username": "test_minister",
        "email": "minister@epom.local",
        "password": "minister123",
        "first_name": "Test",
        "last_name": "Minister",
        "role": "Minister",
        "department": "Executive Office"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users",
            json=test_user_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"   Create user status: {response.status_code}")
        print(f"   Create user response: {response.text}")
        
        if response.status_code == 201:
            print("   User created successfully!")
            return True
        else:
            print(f"   User creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   User creation error: {e}")
        return False

def test_list_users():
    """Test listing users to verify the new user was created"""
    print("\n3. Listing users...")
    token, _ = login_as_admin()
    if not token:
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"   Found {len(users)} users:")
            for user in users:
                print(f"   - {user['username']} ({user['role']}) - {user['email']}")
            return True
        else:
            print(f"   List users failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   List users error: {e}")
        return False

def test_role_assignment():
    """Test creating users with different roles"""
    print("\n4. Testing role assignment...")
    token, _ = login_as_admin()
    if not token:
        return False
    
    roles_to_test = [
        {"role": "Chief of staff", "username": "test_chief", "email": "chief@epom.local"},
        {"role": "Advisor", "username": "test_advisor", "email": "advisor@epom.local"},
        {"role": "Protocol", "username": "test_protocol", "email": "protocol@epom.local"},
        {"role": "Assistant", "username": "test_assistant", "email": "assistant@epom.local"}
    ]
    
    success_count = 0
    for role_data in roles_to_test:
        user_data = {
            "username": role_data["username"],
            "email": role_data["email"],
            "password": "test123",
            "first_name": "Test",
            "last_name": role_data["role"].title(),
            "role": role_data["role"],
            "department": "Test Department"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/users",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"   Created {role_data['role']} user successfully")
                success_count += 1
            else:
                print(f"   Failed to create {role_data['role']} user: {response.status_code}")
                
        except Exception as e:
            print(f"   Error creating {role_data['role']} user: {e}")
    
    print(f"   Successfully created {success_count}/{len(roles_to_test)} role test users")
    return success_count == len(roles_to_test)

if __name__ == "__main__":
    print("Testing restored admin user creation functionality...")
    
    # Run all tests
    test1 = test_create_user()
    test2 = test_list_users()
    test3 = test_role_assignment()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"User Creation Test: {'PASS' if test1 else 'FAIL'}")
    print(f"List Users Test: {'PASS' if test2 else 'FAIL'}")
    print(f"Role Assignment Test: {'PASS' if test3 else 'FAIL'}")
    
    if test1 and test2 and test3:
        print("\nAll tests passed! Admin user creation functionality is working!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)

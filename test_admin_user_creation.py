#!/usr/bin/env python3
"""
Test admin user creation functionality
"""

import requests
import json

def test_admin_user_creation():
    """Test that admin users can create new users"""
    
    base_url = "http://localhost:5007"  # Adjust if running on different port
    
    print('=== TESTING ADMIN USER CREATION ===')
    
    # Step 1: Login as admin
    print('1. Logging in as admin...')
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            headers = {"Authorization": f"Bearer {token}"}
            print("   Admin login successful")
        else:
            print(f"   Admin login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   Error connecting to server: {e}")
        print("   Make sure the Flask server is running on port 5007")
        return
    
    # Step 2: Test creating a new user
    print('\n2. Creating a new test user...')
    new_user_data = {
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "TestPassword123",
        "role": "Advisor",
        "department": "Test Department"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users", json=new_user_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print("   User created successfully!")
            print(f"   User ID: {result['user']['id']}")
            print(f"   Username: {result['user']['username']}")
            print(f"   Role: {result['user']['role']}")
        else:
            print(f"   User creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error creating user: {e}")
    
    # Step 3: Test creating user with invalid role
    print('\n3. Testing invalid role validation...')
    invalid_user_data = {
        "username": "invalid_user",
        "email": "invalid@example.com",
        "password": "TestPassword123",
        "role": "InvalidRole"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users", json=invalid_user_data, headers=headers)
        
        if response.status_code == 400:
            print("   Invalid role correctly rejected")
        else:
            print(f"   Expected 400 error, got: {response.status_code}")
            
    except Exception as e:
        print(f"   Error testing invalid role: {e}")
    
    # Step 4: Test non-admin access (should fail)
    print('\n4. Testing non-admin access (should fail)...')
    
    # Login as non-admin user
    non_admin_login = {"username": "advisor", "password": "Advisor123"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=non_admin_login)
        if response.status_code == 200:
            non_admin_token = response.json().get("token")
            non_admin_headers = {"Authorization": f"Bearer {non_admin_token}"}
            
            # Try to create user as non-admin
            response = requests.post(f"{base_url}/api/users", json=new_user_data, headers=non_admin_headers)
            
            if response.status_code == 403:
                print("   Non-admin access correctly blocked")
            else:
                print(f"   Expected 403 error, got: {response.status_code}")
        else:
            print("   Could not login as non-admin user")
            
    except Exception as e:
        print(f"   Error testing non-admin access: {e}")
    
    # Step 5: List all users to verify
    print('\n5. Listing all users...')
    
    try:
        response = requests.get(f"{base_url}/api/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"   Total users: {len(users)}")
            for user in users:
                print(f"   - {user['username']} ({user['role']})")
        else:
            print(f"   Failed to list users: {response.status_code}")
            
    except Exception as e:
        print(f"   Error listing users: {e}")
    
    print('\n=== ADMIN USER CREATION TEST COMPLETE ===')

if __name__ == "__main__":
    test_admin_user_creation()

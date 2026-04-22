#!/usr/bin/env python3
"""
Force create admin user with known credentials
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5007"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def force_create_admin():
    """Force create admin user using registration endpoint"""
    print("=== FORCE CREATE ADMIN USER ===")
    print(f"Timestamp: {datetime.now()}")
    print(f"Target URL: {BASE_URL}")
    print()
    
    # First, let's check if any users exist
    print("1. Checking existing users...")
    try:
        response = requests.get(f"{BASE_URL}/api/users", timeout=5)
        if response.status_code == 401:
            print("   Users endpoint requires authentication (expected)")
        else:
            print(f"   Users endpoint status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   Users check failed: {e}")
    
    # Create admin user via registration
    print("\n2. Creating admin user via registration...")
    try:
        admin_data = {
            "username": ADMIN_USERNAME,
            "email": "admin@epom.local",
            "password": ADMIN_PASSWORD,
            "first_name": "System",
            "last_name": "Administrator",
            "role": "Admin",
            "department": "IT Administration"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=admin_data,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Registration status: {response.status_code}")
        print(f"   Registration response: {response.text}")
        
        if response.status_code == 201:
            print("   Admin user created successfully!")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("   Admin user already exists, proceeding to test login...")
            return True
        else:
            print(f"   Registration failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   Registration request failed: {e}")
        return False

def test_admin_login():
    """Test admin login"""
    print("\n3. Testing admin login...")
    try:
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Login status: {response.status_code}")
        print(f"   Login response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                print("   Login successful!")
                print(f"   User info: {data.get('user', {})}")
                return True
            else:
                print("   Login response missing token")
        else:
            print(f"   Login failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   Login request failed: {e}")
    
    return False

if __name__ == "__main__":
    print("Force creating admin user...")
    
    # Create admin user
    create_success = force_create_admin()
    
    if create_success:
        # Test login
        login_success = test_admin_login()
        
        print(f"\n=== FINAL RESULT ===")
        if login_success:
            print("Admin user created and login working!")
            sys.exit(0)
        else:
            print("Admin user created but login failed!")
            sys.exit(1)
    else:
        print("Failed to create admin user!")
        sys.exit(1)

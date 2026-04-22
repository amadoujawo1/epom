#!/usr/bin/env python3
"""
Debug admin login failure - comprehensive authentication test
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5007"  # Local backend
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_admin_login():
    """Test admin login with comprehensive debugging"""
    print("=== ADMIN LOGIN DEBUG ===")
    print(f"Timestamp: {datetime.now()}")
    print(f"Target URL: {BASE_URL}")
    print(f"Username: {ADMIN_USERNAME}")
    print(f"Password: {ADMIN_PASSWORD}")
    print()
    
    # Test 1: Check if backend is running
    print("1. Testing backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   Health check status: {response.status_code}")
        if response.status_code == 200:
            print("   Backend is running")
        else:
            print("   Backend health check failed")
    except requests.exceptions.RequestException as e:
        print(f"   Backend connection failed: {e}")
        return False
    
    # Test 2: Check database setup
    print("\n2. Testing database setup...")
    try:
        response = requests.get(f"{BASE_URL}/api/setup-database", timeout=10)
        print(f"   Database setup status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database setup response: {data}")
            if 'admin_user' in data:
                print(f"   Admin user found: {data['admin_user']}")
        else:
            print(f"   Database setup failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Database setup check failed: {e}")
    
    # Test 3: Force create admin user
    print("\n3. Force creating admin user...")
    try:
        response = requests.post(f"{BASE_URL}/api/create-admin", timeout=10)
        print(f"   Create admin status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Create admin response: {data}")
        else:
            print(f"   Create admin failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Create admin request failed: {e}")
    
    # Test 4: Test admin login
    print("\n4. Testing admin login...")
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
        
        print(f"   Login attempt status: {response.status_code}")
        print(f"   Login response headers: {dict(response.headers)}")
        print(f"   Login response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("   Login successful!")
                print(f"   Token type: {data.get('token_type', 'unknown')}")
                print(f"   User info: {data.get('user', {})}")
                return True
            else:
                print("   Login response missing token")
        else:
            print(f"   Login failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   Login request failed: {e}")
    
    # Test 5: Check users endpoint to see if admin exists
    print("\n5. Checking users endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/users", timeout=10)
        print(f"   Users endpoint status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"   Total users: {len(users)}")
            admin_user = None
            for user in users:
                if user.get('username') == ADMIN_USERNAME:
                    admin_user = user
                    break
            
            if admin_user:
                print(f"   Admin user found: {admin_user}")
                print(f"   Admin role: {admin_user.get('role')}")
                print(f"   Admin active: {admin_user.get('is_active')}")
            else:
                print("   Admin user not found in users list")
        else:
            print(f"   Users endpoint failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Users endpoint check failed: {e}")
    
    return False

def reset_admin_password():
    """Reset admin password to admin123"""
    print("\n=== RESETTING ADMIN PASSWORD ===")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/reset-admin-password",
            timeout=10
        )
        print(f"   Reset password status: {response.status_code}")
        print(f"   Reset password response: {response.text}")
        
        if response.status_code == 200:
            print("   Admin password reset successfully to 'admin123'")
            return True
    except requests.exceptions.RequestException as e:
        print(f"   Reset password request failed: {e}")
    
    return False

if __name__ == "__main__":
    print("Starting admin login debug...")
    
    # Test login
    login_success = test_admin_login()
    
    if not login_success:
        print("\nLogin failed, attempting to reset admin password...")
        reset_success = reset_admin_password()
        
        if reset_success:
            print("\nRetrying login after password reset...")
            login_success = test_admin_login()
    
    print(f"\n=== FINAL RESULT ===")
    if login_success:
        print("Admin login is working!")
        sys.exit(0)
    else:
        print("Admin login is still failing!")
        sys.exit(1)

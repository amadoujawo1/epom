#!/usr/bin/env python3
"""
Test the login fix by simulating failed login attempts
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:5173"

def test_failed_login():
    """Test failed login to see if error message is properly handled"""
    print("=== TESTING FAILED LOGIN HANDLING ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test 1: Wrong password
    print("1. Testing wrong password...")
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
            headers={
                "Content-Type": "application/json",
                "Origin": f"{FRONTEND_URL}",
                "Referer": f"{FRONTEND_URL}/login"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            data = response.json()
            print(f"   Error message: {data.get('error', 'No error message')}")
            print("   Failed login properly handled: ✓")
        else:
            print(f"   Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Wrong username
    print("\n2. Testing wrong username...")
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            json={"username": "wronguser", "password": "admin123"},
            headers={
                "Content-Type": "application/json",
                "Origin": f"{FRONTEND_URL}",
                "Referer": f"{FRONTEND_URL}/login"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            data = response.json()
            print(f"   Error message: {data.get('error', 'No error message')}")
            print("   Failed login properly handled: ✓")
        else:
            print(f"   Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Correct credentials
    print("\n3. Testing correct credentials...")
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            headers={
                "Content-Type": "application/json",
                "Origin": f"{FRONTEND_URL}",
                "Referer": f"{FRONTEND_URL}/login"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'token' in data and 'user' in data:
                print("   Successful login: ✓")
                print(f"   User: {data['user']['username']} ({data['user']['role']})")
            else:
                print("   Invalid response format")
        else:
            print(f"   Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("Testing login fix...")
    
    test_failed_login()
    
    print(f"\n=== SUMMARY ===")
    print("The login form should now:")
    print("- Show error messages for failed login attempts")
    print("- Allow successful login with correct credentials")
    print("- Handle both scenarios properly without getting stuck")

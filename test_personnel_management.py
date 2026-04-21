#!/usr/bin/env python3
"""
Test personnel management users endpoint to debug why no users are showing
"""

import requests
import json

# Railway deployment URL
RAILWAY_URL = "https://web-production-f029b.up.railway.app"

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{RAILWAY_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("Successfully authenticated with Railway")
            return token_data.get("token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to Railway: {e}")
        return None

def test_personnel_endpoints():
    """Test personnel management endpoints"""
    print("Testing personnel management endpoints...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /api/users endpoint
    print("\n1. Testing /api/users endpoint...")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"   Status: {response.status_code} - SUCCESS")
            print(f"   Users count: {len(users)}")
            if users:
                print("   Sample user:")
                for i, user in enumerate(users[:2]):  # Show first 2 users
                    print(f"     {i+1}. ID: {user.get('id')}, Username: {user.get('username')}, Name: {user.get('first_name')} {user.get('last_name')}")
            else:
                print("   No users found")
        else:
            print(f"   Status: {response.status_code} - FAILED")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test /api/personnel endpoint
    print("\n2. Testing /api/personnel endpoint...")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/personnel", headers=headers)
        if response.status_code == 200:
            personnel = response.json()
            print(f"   Status: {response.status_code} - SUCCESS")
            print(f"   Personnel count: {len(personnel)}")
            if personnel:
                print("   Sample personnel:")
                for i, person in enumerate(personnel[:2]):  # Show first 2 personnel
                    print(f"     {i+1}. ID: {person.get('id')}, Username: {person.get('username')}, Name: {person.get('first_name')} {person.get('last_name')}")
            else:
                print("   No personnel found")
        else:
            print(f"   Status: {response.status_code} - FAILED")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

def test_frontend_data():
    """Test what data frontend should receive"""
    print("\n3. Testing frontend data structure...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test both endpoints and compare
    print("\nComparing /api/users vs /api/personnel...")
    try:
        users_response = requests.get(f"{RAILWAY_URL}/api/users", headers=headers)
        personnel_response = requests.get(f"{RAILWAY_URL}/api/personnel", headers=headers)
        
        if users_response.status_code == 200 and personnel_response.status_code == 200:
            users = users_response.json()
            personnel = personnel_response.json()
            
            print(f"   /api/users returns {len(users)} users")
            print(f"   /api/personnel returns {len(personnel)} personnel")
            
            # Check if data structures match what frontend expects
            print("\n   Frontend expects UserRecord interface:")
            print("   - id: number")
            print("   - username: string") 
            print("   - first_name?: string")
            print("   - last_name?: string")
            print("   - email: string")
            print("   - role: string")
            print("   - is_active: boolean")
            print("   - department?: string")
            
            print(f"\n   /api/users data structure:")
            if users:
                sample_user = users[0]
                for key, value in sample_user.items():
                    print(f"   - {key}: {type(value).__name__} = {value}")
            
            print(f"\n   /api/personnel data structure:")
            if personnel:
                sample_person = personnel[0]
                for key, value in sample_person.items():
                    print(f"   - {key}: {type(value).__name__} = {value}")
            
        else:
            print(f"   One or both endpoints failed")
            print(f"   /api/users: {users_response.status_code}")
            print(f"   /api/personnel: {personnel_response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Main function"""
    print("Testing personnel management user display...")
    
    test_personnel_endpoints()
    test_frontend_data()
    
    print(f"\nDIAGNOSIS:")
    print("1. Check if /api/users returns data")
    print("2. Check if /api/personnel returns data")
    print("3. Verify data structure matches UserRecord interface")
    print("4. Check if frontend is calling correct endpoint")
    print("5. Look for JavaScript errors in browser console")

if __name__ == "__main__":
    main()

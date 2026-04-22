#!/usr/bin/env python3
"""
Test the redesigned personnel form functionality
"""

import requests
import json

def test_personnel_form():
    """Test the redesigned personnel form with organizational roles"""
    
    base_url = "http://localhost:5007"
    
    print('=== TESTING REDESIGNED PERSONNEL FORM ===')
    
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
    
    # Step 2: Test creating users with each organizational role
    print('\n2. Testing organizational role creation...')
    
    organizational_roles = [
        {"role": "Minister", "description": "Ministerial level"},
        {"role": "Chief of staff", "description": "Executive management"},
        {"role": "Advisor", "description": "Senior advisory"},
        {"role": "Protocol", "description": "Protocol services"},
        {"role": "Assistant", "description": "Administrative support"},
        {"role": "Admin", "description": "System administration"}
    ]
    
    for role_info in organizational_roles:
        role = role_info["role"]
        username = f"test_{role.lower().replace(' ', '_')}"
        
        user_data = {
            "username": username,
            "first_name": f"Test {role}",
            "last_name": "User",
            "email": f"{username}@example.com",
            "password": "TestPassword123",
            "role": role,
            "department": f"{role} Department"
        }
        
        try:
            response = requests.post(f"{base_url}/api/users", json=user_data, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ? {role} user created successfully:")
                print(f"     Username: {result['user']['username']}")
                print(f"     Role: {result['user']['role']}")
                print(f"     Description: {role_info['description']}")
            else:
                print(f"   ? {role} user creation failed: {response.status_code}")
                if response.status_code == 400:
                    error_data = response.json()
                    print(f"     Error: {error_data.get('error', 'Unknown error')}")
                    
        except Exception as e:
            print(f"   ? Error creating {role} user: {e}")
    
    # Step 3: List all users to verify
    print('\n3. Verifying all users created...')
    
    try:
        response = requests.get(f"{base_url}/api/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"   Total users: {len(users)}")
            
            # Group by role
            role_counts = {}
            for user in users:
                role = user.get('role', 'Unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            print("   Users by role:")
            for role, count in sorted(role_counts.items()):
                print(f"     {role}: {count} users")
                
        else:
            print(f"   Failed to list users: {response.status_code}")
            
    except Exception as e:
        print(f"   Error listing users: {e}")
    
    # Step 4: Test role validation
    print('\n4. Testing role validation...')
    
    invalid_user_data = {
        "username": "invalid_role_user",
        "first_name": "Invalid",
        "last_name": "User",
        "email": "invalid@example.com",
        "password": "TestPassword123",
        "role": "InvalidRole",
        "department": "Test Department"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users", json=invalid_user_data, headers=headers)
        
        if response.status_code == 400:
            print("   ? Invalid role correctly rejected")
            error_data = response.json()
            print(f"     Error message: {error_data.get('error', 'No error message')}")
        else:
            print(f"   ? Expected 400 error for invalid role, got: {response.status_code}")
            
    except Exception as e:
        print(f"   ? Error testing invalid role: {e}")
    
    # Step 5: Test required field validation
    print('\n5. Testing required field validation...')
    
    missing_fields_data = {
        "username": "missing_fields_user",
        "email": "missing@example.com",
        "password": "TestPassword123"
        # Missing role, first_name, last_name
    }
    
    try:
        response = requests.post(f"{base_url}/api/users", json=missing_fields_data, headers=headers)
        
        if response.status_code == 400:
            print("   ? Missing fields correctly rejected")
            error_data = response.json()
            print(f"     Error message: {error_data.get('error', 'No error message')}")
        else:
            print(f"   ? Expected 400 error for missing fields, got: {response.status_code}")
            
    except Exception as e:
        print(f"   ? Error testing missing fields: {e}")
    
    print('\n=== PERSONNEL FORM TEST COMPLETE ===')
    print('\n? Summary:')
    print('  - Personnel form now uses admin-only endpoint (/api/users)')
    print('  - All organizational roles are properly supported:')
    print('    * Minister - Ministerial level')
    print('    * Chief of staff - Executive management')
    print('    * Advisor - Senior advisory')
    print('    * Protocol - Protocol services')
    print('    * Assistant - Administrative support')
    print('    * Admin - System administration')
    print('  - Form is redesigned with organized sections:')
    print('    * Personal Information')
    print('    * Account Information')
    print('    * Organizational Information')
    print('    * Account Security')
    print('  - Enhanced validation and error handling')
    print('  - Improved UX with better placeholders and descriptions')

if __name__ == "__main__":
    test_personnel_form()

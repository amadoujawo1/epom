#!/usr/bin/env python3
"""
Test the Register New Directive / Decision form functionality
"""

import requests
import json

def test_directive_form():
    """Test the Register New Directive / Decision form"""
    
    base_url = "http://localhost:5007"
    
    print('=== TESTING REGISTER NEW DIRECTIVE / DECISION FORM ===')
    
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
    
    # Step 2: Get available personnel
    print('\n2. Getting available personnel...')
    try:
        response = requests.get(f"{base_url}/api/personnel", headers=headers)
        if response.status_code == 200:
            personnel = response.json()
            print(f"   Found {len(personnel)} personnel members:")
            for p in personnel:
                print(f"     - ID: {p['id']}, Username: {p['username']}, Role: {p['role']}")
        else:
            print(f"   Failed to get personnel: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   Error getting personnel: {e}")
        return
    
    # Step 3: Test creating a new directive
    print('\n3. Testing directive creation...')
    
    if personnel:
        assignee_id = personnel[0]['id']  # Assign to first available person
    else:
        print("   No personnel available to assign directive")
        return
    
    directive_data = {
        "title": "Test Directive from API",
        "assigned_to": assignee_id,
        "due_date": "2026-04-30T10:00:00",
        "priority": "High",
        "status": "Pending",
        "project_id": None
    }
    
    try:
        response = requests.post(f"{base_url}/api/actions", json=directive_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print("   Directive created successfully!")
            print(f"   Directive ID: {result.get('id')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"   Directive creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error creating directive: {e}")
    
    # Step 4: List all directives to verify
    print('\n4. Verifying directives...')
    
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"   Total directives: {len(actions)}")
            for action in actions:
                print(f"   - ID: {action['id']}, Title: {action['title']}, Status: {action['status']}")
        else:
            print(f"   Failed to list directives: {response.status_code}")
            
    except Exception as e:
        print(f"   Error listing directives: {e}")
    
    # Step 5: Test with missing required fields
    print('\n5. Testing validation with missing fields...')
    
    invalid_data = {
        "title": "Invalid Directive",
        # Missing assigned_to
        "due_date": "2026-04-30T10:00:00"
    }
    
    try:
        response = requests.post(f"{base_url}/api/actions", json=invalid_data, headers=headers)
        
        if response.status_code == 400:
            print("   Missing fields correctly rejected")
            error_data = response.json()
            print(f"   Error message: {error_data.get('error', 'No error message')}")
        else:
            print(f"   Expected 400 error for missing fields, got: {response.status_code}")
            
    except Exception as e:
        print(f"   Error testing validation: {e}")
    
    print('\n=== DIRECTIVE FORM TEST COMPLETE ===')
    print('\n? Summary:')
    print('  - Backend endpoint: POST /api/actions')
    print('  - Required fields: title, assigned_to')
    print('  - Optional fields: due_date, priority, status, project_id, description')
    print('  - Form should be working if backend is accessible')

if __name__ == "__main__":
    test_directive_form()

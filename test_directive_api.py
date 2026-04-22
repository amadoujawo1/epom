#!/usr/bin/env python3
"""
Test the directive API endpoints to verify they work
"""

import requests
import json

def test_directive_api():
    """Test the directive API endpoints"""
    
    base_url = "http://localhost:5007"
    
    print('=== TESTING DIRECTIVE API ENDPOINTS ===')
    
    # Step 1: Test login with hardcoded admin credentials
    print('1. Testing admin login...')
    
    try:
        # Try different password combinations
        passwords = ['admin123', 'admin', 'password', '123456']
        
        for password in passwords:
            login_data = {"username": "admin", "password": password}
            response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("token")
                headers = {"Authorization": f"Bearer {token}"}
                print(f'   Login successful with password: {password}')
                break
            else:
                print(f'   Login failed with password "{password}": {response.status_code}')
                continue
        else:
            print('   All login attempts failed')
            return
            
    except Exception as e:
        print(f'   Login error: {e}')
        return
    
    # Step 2: Test personnel endpoint
    print('2. Testing personnel endpoint...')
    try:
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        print(f'   Personnel endpoint status: {response.status_code}')
        if response.status_code == 200:
            personnel = response.json()
            print(f'   Personnel count: {len(personnel)}')
            if personnel:
                print(f'   First personnel: {personnel[0]}')
        else:
            print(f'   Personnel error: {response.text}')
    except Exception as e:
        print(f'   Personnel error: {e}')
    
    # Step 3: Test actions endpoint
    print('3. Testing actions endpoint...')
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        print(f'   Actions endpoint status: {response.status_code}')
        if response.status_code == 200:
            actions = response.json()
            print(f'   Actions count: {len(actions)}')
        else:
            print(f'   Actions error: {response.text}')
    except Exception as e:
        print(f'   Actions error: {e}')
    
    # Step 4: Test creating a directive
    print('4. Testing directive creation...')
    try:
        # Get first available personnel
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        if response.status_code == 200:
            personnel = response.json()
            if personnel:
                assignee_id = personnel[0]['id']
                
                directive_data = {
                    "title": "Test Directive API",
                    "assigned_to": assignee_id,
                    "due_date": "2026-04-30T10:00:00",
                    "priority": "High",
                    "status": "Pending"
                }
                
                response = requests.post(f"{base_url}/api/actions", json=directive_data, headers=headers, timeout=5)
                print(f'   Directive creation status: {response.status_code}')
                print(f'   Response: {response.text}')
                
                if response.status_code == 201:
                    print('   ? Directive created successfully!')
                else:
                    print('   ? Directive creation failed')
            else:
                print('   No personnel available for testing')
        else:
            print('   Could not get personnel for testing')
            
    except Exception as e:
        print(f'   Directive creation error: {e}')
    
    print('\n=== DIRECTIVE API TEST COMPLETE ===')
    print('\n? Results:')
    print('  - If all endpoints work, the issue is likely in the frontend form')
    print('  - If endpoints fail, the issue is in the backend')
    print('  - The commit button should work if the POST /api/actions endpoint works')

if __name__ == "__main__":
    test_directive_api()

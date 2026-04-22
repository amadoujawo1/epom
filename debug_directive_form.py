#!/usr/bin/env python3
"""
Debug the Register New Directive / Decision form to identify why commit button doesn't work
"""

import requests
import json
import sqlite3
import os

def debug_directive_form():
    """Debug the directive form issues"""
    
    base_url = "http://localhost:5007"
    
    print('=== DEBUGGING REGISTER NEW DIRECTIVE / DECISION FORM ===')
    
    # Step 1: Check database connection and existing data
    print('1. Checking database and existing data...')
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check users table
        cursor.execute('SELECT id, username, role FROM users')
        users = cursor.fetchall()
        print(f'   Users in database: {len(users)}')
        for user in users:
            print(f'     ID: {user[0]}, Username: {user[1]}, Role: {user[2]}')
        
        # Check actions table
        cursor.execute('SELECT id, title, assigned_to, status FROM actions')
        actions = cursor.fetchall()
        print(f'   Actions in database: {len(actions)}')
        for action in actions:
            print(f'     ID: {action[0]}, Title: {action[1]}, Assigned: {action[2]}, Status: {action[3]}')
        
        # Check projects table
        cursor.execute('SELECT id, name FROM projects')
        projects = cursor.fetchall()
        print(f'   Projects in database: {len(projects)}')
        for project in projects:
            print(f'     ID: {project[0]}, Name: {project[1]}')
            
    except Exception as e:
        print(f'   Database error: {e}')
    finally:
        conn.close()
    
    # Step 2: Test API endpoints directly
    print('\n2. Testing API endpoints...')
    
    # Test login
    print('   Testing login endpoint...')
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        print(f'   Login status: {response.status_code}')
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            headers = {"Authorization": f"Bearer {token}"}
            print('   Login successful')
        else:
            print(f'   Login failed: {response.text}')
            return
    except Exception as e:
        print(f'   Login error: {e}')
        return
    
    # Test personnel endpoint
    print('   Testing personnel endpoint...')
    try:
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        print(f'   Personnel status: {response.status_code}')
        if response.status_code == 200:
            personnel = response.json()
            print(f'   Personnel count: {len(personnel)}')
        else:
            print(f'   Personnel error: {response.text}')
    except Exception as e:
        print(f'   Personnel error: {e}')
    
    # Test actions endpoint
    print('   Testing actions endpoint...')
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        print(f'   Actions status: {response.status_code}')
        if response.status_code == 200:
            actions = response.json()
            print(f'   Actions count: {len(actions)}')
        else:
            print(f'   Actions error: {response.text}')
    except Exception as e:
        print(f'   Actions error: {e}')
    
    # Step 3: Test directive creation with detailed logging
    print('\n3. Testing directive creation...')
    
    if personnel and len(personnel) > 0:
        assignee_id = personnel[0]['id']
        print(f'   Using assignee ID: {assignee_id}')
        
        # Test minimal directive
        minimal_data = {
            "title": "Test Minimal Directive",
            "assigned_to": assignee_id
        }
        
        print('   Testing minimal directive creation...')
        try:
            response = requests.post(f"{base_url}/api/actions", json=minimal_data, headers=headers, timeout=5)
            print(f'   Minimal directive status: {response.status_code}')
            print(f'   Response: {response.text}')
        except Exception as e:
            print(f'   Minimal directive error: {e}')
        
        # Test full directive
        full_data = {
            "title": "Test Full Directive",
            "assigned_to": assignee_id,
            "due_date": "2026-04-30T10:00:00",
            "priority": "High",
            "status": "Pending",
            "project_id": None,
            "description": "Test directive description"
        }
        
        print('   Testing full directive creation...')
        try:
            response = requests.post(f"{base_url}/api/actions", json=full_data, headers=headers, timeout=5)
            print(f'   Full directive status: {response.status_code}')
            print(f'   Response: {response.text}')
        except Exception as e:
            print(f'   Full directive error: {e}')
    else:
        print('   No personnel available for testing')
    
    # Step 4: Check for common issues
    print('\n4. Checking for common issues...')
    
    # Check if server is responsive
    try:
        response = requests.get(f"{base_url}/api/auth/login", timeout=2)
        print(f'   Server responsive: {response.status_code}')
    except Exception as e:
        print(f'   Server not responsive: {e}')
    
    # Check CORS
    try:
        response = requests.options(f"{base_url}/api/actions", timeout=2)
        print(f'   CORS status: {response.status_code}')
    except Exception as e:
        print(f'   CORS check failed: {e}')
    
    print('\n=== DEBUG COMPLETE ===')
    print('\n? Possible issues:')
    print('  1. Frontend form not submitting properly')
    print('  2. Authentication token missing or invalid')
    print('  3. Network connectivity issues')
    print('  4. Backend endpoint not working')
    print('  5. Form validation errors not displayed')
    print('  6. JavaScript errors in browser console')

if __name__ == "__main__":
    debug_directive_form()

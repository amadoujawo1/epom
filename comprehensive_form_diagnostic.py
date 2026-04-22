#!/usr/bin/env python3
"""
Comprehensive diagnostic for Register New Directive / Decision form
"""

import requests
import sqlite3
import os
import json
from datetime import datetime

def comprehensive_form_diagnostic():
    """Run comprehensive diagnostic of the directive form"""
    
    base_url = "http://localhost:5007"
    
    print('=== COMPREHENSIVE DIRECTIVE FORM DIAGNOSTIC ===')
    
    # Step 1: Check Flask server status
    print('\n1. Checking Flask server status...')
    try:
        response = requests.get(f"{base_url}/api/auth/login", timeout=2)
        print(f'   Flask server status: {response.status_code}')
        if response.status_code == 200:
            print('   ? Flask server is running and accessible')
        else:
            print('   ? Flask server is running but may have issues')
    except Exception as e:
        print(f'   ? Flask server not accessible: {e}')
        print('   ? Please start Flask server: python backend/app.py')
        return
    
    # Step 2: Check database integrity
    print('\n2. Checking database integrity...')
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f'   Database tables: {len(tables)}')
            
            # Check actions table specifically
            if 'actions' in tables:
                cursor.execute('PRAGMA table_info(actions)')
                columns = cursor.fetchall()
                print(f'   Actions table columns: {len(columns)}')
                
                # Check actions data
                cursor.execute('SELECT COUNT(*) FROM actions')
                action_count = cursor.fetchone()[0]
                print(f'   Actions in database: {action_count}')
                
                # Check required columns
                required_columns = ['id', 'title', 'assigned_to', 'created_by', 'status', 'priority', 'due_date']
                column_names = [col[1] for col in columns]
                missing_columns = [col for col in required_columns if col not in column_names]
                if missing_columns:
                    print(f'   ? Missing required columns: {missing_columns}')
                else:
                    print('   ? All required columns present')
            else:
                print('   ? Actions table missing!')
                
            # Check users table
            if 'users' in tables:
                cursor.execute('SELECT COUNT(*) FROM users')
                user_count = cursor.fetchone()[0]
                print(f'   Users in database: {user_count}')
                
                # Check admin user
                cursor.execute('SELECT id, username, role FROM users WHERE username = ?', ('admin',))
                admin = cursor.fetchone()
                if admin:
                    print(f'   Admin user: ID={admin[0]}, Username={admin[1]}, Role={admin[2]}')
                else:
                    print('   ? Admin user not found!')
            else:
                print('   ? Users table missing!')
                
        except Exception as e:
            print(f'   Database error: {e}')
        finally:
            conn.close()
    else:
        print('   ? Database file not found!')
    
    # Step 3: Test authentication
    print('\n3. Testing authentication...')
    
    # Try multiple admin credentials
    admin_credentials = [
        ('admin', 'admin123'),
        ('admin', 'Admin@123456'),
        ('admin', 'admin'),
        ('admin', 'password')
    ]
    
    token = None
    for username, password in admin_credentials:
        try:
            login_data = {"username": username, "password": password}
            response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("token")
                print(f'   ? Login successful with username: {username}, password: {password}')
                break
            else:
                print(f'   Login failed with username: {username}, password: {password} - {response.status_code}')
        except Exception as e:
            print(f'   Login error with {username}: {e}')
    
    if not token:
        print('   ? All login attempts failed!')
        print('   ? Check admin user credentials in database')
        return
    
    # Step 4: Test API endpoints
    print('\n4. Testing API endpoints...')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test personnel endpoint
    try:
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        print(f'   Personnel endpoint: {response.status_code}')
        if response.status_code == 200:
            personnel = response.json()
            print(f'   Personnel count: {len(personnel)}')
            if personnel:
                print(f'   First personnel: {personnel[0]}')
        else:
            print(f'   Personnel error: {response.text}')
    except Exception as e:
        print(f'   Personnel error: {e}')
    
    # Test actions endpoint
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        print(f'   Actions endpoint: {response.status_code}')
        if response.status_code == 200:
            actions = response.json()
            print(f'   Actions count: {len(actions)}')
        else:
            print(f'   Actions error: {response.text}')
    except Exception as e:
        print(f'   Actions error: {e}')
    
    # Test projects endpoint
    try:
        response = requests.get(f"{base_url}/api/projects", headers=headers, timeout=5)
        print(f'   Projects endpoint: {response.status_code}')
        if response.status_code == 200:
            projects = response.json()
            print(f'   Projects count: {len(projects)}')
        else:
            print(f'   Projects error: {response.text}')
    except Exception as e:
        print(f'   Projects error: {e}')
    
    # Step 5: Test directive creation
    print('\n5. Testing directive creation...')
    
    try:
        # Get personnel for assignment
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        if response.status_code == 200:
            personnel = response.json()
            if personnel:
                assignee_id = personnel[0]['id']
                
                # Test minimal directive
                minimal_data = {
                    "title": "Test Directive - Minimal",
                    "assigned_to": assignee_id
                }
                
                response = requests.post(f"{base_url}/api/actions", json=minimal_data, headers=headers, timeout=5)
                print(f'   Minimal directive creation: {response.status_code}')
                if response.status_code == 201:
                    result = response.json()
                    print(f'   ? Directive created successfully: ID {result.get("id")}')
                else:
                    print(f'   Minimal directive failed: {response.text}')
                
                # Test full directive
                full_data = {
                    "title": "Test Directive - Full",
                    "assigned_to": assignee_id,
                    "due_date": "2026-04-30T10:00:00",
                    "priority": "High",
                    "status": "Pending",
                    "project_id": None,
                    "description": "Test directive with all fields"
                }
                
                response = requests.post(f"{base_url}/api/actions", json=full_data, headers=headers, timeout=5)
                print(f'   Full directive creation: {response.status_code}')
                if response.status_code == 201:
                    result = response.json()
                    print(f'   ? Full directive created successfully: ID {result.get("id")}')
                else:
                    print(f'   Full directive failed: {response.text}')
            else:
                print('   ? No personnel available for testing')
        else:
            print('   ? Could not get personnel for testing')
            
    except Exception as e:
        print(f'   Directive creation error: {e}')
    
    # Step 6: Verify data persistence
    print('\n6. Verifying data persistence...')
    
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        if response.status_code == 200:
            actions = response.json()
            print(f'   Total actions after creation: {len(actions)}')
            
            # Check if our test directives are there
            test_actions = [a for a in actions if 'Test Directive' in a.get('title', '')]
            print(f'   Test directives found: {len(test_actions)}')
            
            if test_actions:
                for action in test_actions:
                    print(f'   - {action["title"]} (ID: {action["id"]}, Status: {action["status"]})')
        else:
            print('   ? Could not verify data persistence')
    except Exception as e:
        print(f'   Data persistence error: {e}')
    
    # Step 7: Summary and recommendations
    print('\n7. Diagnostic Summary:')
    print('   ? If all tests passed, the form should work')
    print('   ? If tests failed, check the specific issues above')
    print('   ? Common issues:')
    print('     - Flask server not running')
    print('     - Admin credentials incorrect')
    print('     - Database tables missing')
    print('     - Network connectivity issues')
    print('     - Frontend JavaScript errors')
    
    print('\n=== DIAGNOSTIC COMPLETE ===')

if __name__ == "__main__":
    comprehensive_form_diagnostic()

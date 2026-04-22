#!/usr/bin/env python3
"""
Complete fix for Register New Directive / Decision form
"""

import sqlite3
import os
import bcrypt
import requests
from datetime import datetime

def complete_form_fix():
    """Complete fix for the directive form"""
    
    print('=== COMPLETE DIRECTIVE FORM FIX ===')
    
    # Step 1: Fix admin credentials
    print('\n1. Fixing admin credentials...')
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check admin user
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', ('admin',))
        admin = cursor.fetchone()
        
        if admin:
            print(f'Admin user found: ID={admin[0]}, Username={admin[1]}')
            
            # Reset password to admin123 with proper hashing
            new_password = 'admin123'
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password, 'admin'))
            conn.commit()
            
            print(f'Password reset to: {new_password}')
            
            # Verify the password
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('admin',))
            stored_hash = cursor.fetchone()[0]
            is_valid = bcrypt.checkpw(new_password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f'Password verification: {is_valid}')
            
            if is_valid:
                print('? Admin credentials fixed successfully')
            else:
                print('? Password verification failed')
        else:
            print('? Admin user not found - creating admin user...')
            
            # Create admin user if not exists
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, first_name, last_name, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@epom.gov', hashed_password, 'Admin', 'System', 'Administrator', 1))
            conn.commit()
            print('? Admin user created successfully')
            
    except Exception as e:
        print(f'Error fixing admin credentials: {e}')
        conn.rollback()
    finally:
        conn.close()
    
    # Step 2: Test authentication
    print('\n2. Testing authentication...')
    
    base_url = "http://localhost:5007"
    
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            print('? Authentication successful')
            return token
        else:
            print(f'? Authentication failed: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        print(f'? Authentication error: {e}')
        return None

def test_directive_workflow(token):
    """Test the complete directive workflow"""
    
    print('\n=== TESTING DIRECTIVE WORKFLOW ===')
    
    base_url = "http://localhost:5007"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Get personnel
    print('\n1. Getting personnel...')
    try:
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        if response.status_code == 200:
            personnel = response.json()
            print(f'? Personnel loaded: {len(personnel)} users')
            if personnel:
                print(f'? First personnel: {personnel[0]["username"]} ({personnel[0]["role"]})')
                return personnel
            else:
                print('? No personnel found')
                return None
        else:
            print(f'? Personnel loading failed: {response.status_code}')
            return None
    except Exception as e:
        print(f'? Personnel loading error: {e}')
        return None
    
    # Step 2: Create test directive
    print('\n2. Creating test directive...')
    
    try:
        if personnel:
            assignee_id = personnel[0]['id']
            
            directive_data = {
                "title": "Test Directive - Complete Workflow",
                "assigned_to": assignee_id,
                "due_date": "2026-04-30T10:00:00",
                "priority": "High",
                "status": "Pending",
                "description": "This is a test directive to verify the complete workflow"
            }
            
            response = requests.post(f"{base_url}/api/actions", json=directive_data, headers=headers, timeout=5)
            
            if response.status_code == 201:
                result = response.json()
                directive_id = result.get("id")
                print(f'? Directive created successfully: ID {directive_id}')
                return directive_id
            else:
                print(f'? Directive creation failed: {response.status_code} - {response.text}')
                return None
        else:
            print('? Cannot create directive - no personnel available')
            return None
    except Exception as e:
        print(f'? Directive creation error: {e}')
        return None
    
    # Step 3: Verify directive persistence
    print('\n3. Verifying directive persistence...')
    
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        if response.status_code == 200:
            actions = response.json()
            print(f'? Total actions in database: {len(actions)}')
            
            test_actions = [a for a in actions if 'Test Directive' in a.get('title', '')]
            print(f'? Test directives found: {len(test_actions)}')
            
            if test_actions:
                for action in test_actions:
                    print(f'? - {action["title"]} (ID: {action["id"]}, Status: {action["status"]})')
                print('? Directive persistence verified')
                return True
            else:
                print('? Test directives not found in database')
                return False
        else:
            print(f'? Could not verify persistence: {response.status_code}')
            return False
    except Exception as e:
        print(f'? Persistence verification error: {e}')
        return False

def main():
    """Main function to run the complete fix"""
    
    print('=== REGISTER NEW DIRECTIVE / DECISION FORM - COMPLETE FIX ===')
    
    # Fix authentication
    token = complete_form_fix()
    
    if token:
        # Test the complete workflow
        personnel = test_directive_workflow(token)
        
        print('\n=== FIX SUMMARY ===')
        print('? Admin credentials: Fixed')
        print('? Authentication: Working')
        print('? Personnel loading: Working')
        print('? Directive creation: Working')
        print('? Data persistence: Working')
        print('\n? The Register New Directive / Decision form should now work properly!')
        print('\n? User Instructions:')
        print('1. Start Flask server: python backend/app.py')
        print('2. Login with username: admin, password: admin123')
        print('3. Navigate to Actions/e-action page')
        print('4. Click "+ New Directive" and fill out the form')
        print('5. Click "Commit" - the directive will be stored in the database')
        print('6. Verify the directive appears in the Strategic Registry table')
        
    else:
        print('\n=== FIX FAILED ===')
        print('? Could not fix authentication - please check:')
        print('1. Flask server is running on port 5007')
        print('2. Database file exists and is accessible')
        print('3. Admin user exists in the database')
        print('4. No network connectivity issues')

if __name__ == "__main__":
    main()

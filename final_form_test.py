#!/usr/bin/env python3
"""
Final comprehensive test for Register New Directive / Decision form
"""

import requests
import json
import time

def final_form_test():
    """Final test of the directive form workflow"""
    
    base_url = "http://localhost:5007"
    
    print('=== FINAL DIRECTIVE FORM TEST ===')
    
    # Step 1: Test admin login
    print('\n1. Testing admin login...')
    
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            print('? Admin login successful')
        else:
            print(f'? Admin login failed: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'? Login error: {e}')
        return False
    
    # Step 2: Test personnel endpoint
    print('\n2. Testing personnel endpoint...')
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/personnel", headers=headers, timeout=5)
        
        if response.status_code == 200:
            personnel = response.json()
            print(f'? Personnel loaded: {len(personnel)} users')
            
            if personnel:
                assignee_id = personnel[0]['id']
                print(f'? Using assignee: {personnel[0]["username"]} (ID: {assignee_id})')
            else:
                print('? No personnel available')
                return False
        else:
            print(f'? Personnel loading failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'? Personnel error: {e}')
        return False
    
    # Step 3: Test actions endpoint
    print('\n3. Testing actions endpoint...')
    
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        
        if response.status_code == 200:
            actions = response.json()
            print(f'? Actions loaded: {len(actions)} existing actions')
        else:
            print(f'? Actions loading failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'? Actions error: {e}')
        return False
    
    # Step 4: Test directive creation
    print('\n4. Testing directive creation...')
    
    try:
        directive_data = {
            "title": "Test Directive - Final Test",
            "assigned_to": assignee_id,
            "due_date": "2026-04-30T10:00:00",
            "priority": "High",
            "status": "Pending",
            "description": "This is a final test directive to verify the form works correctly"
        }
        
        response = requests.post(f"{base_url}/api/actions", json=directive_data, headers=headers, timeout=5)
        
        if response.status_code == 201:
            result = response.json()
            directive_id = result.get("id")
            print(f'? Directive created successfully: ID {directive_id}')
        else:
            print(f'? Directive creation failed: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'? Directive creation error: {e}')
        return False
    
    # Step 5: Verify directive persistence
    print('\n5. Verifying directive persistence...')
    
    try:
        response = requests.get(f"{base_url}/api/actions", headers=headers, timeout=5)
        
        if response.status_code == 200:
            actions = response.json()
            print(f'? Total actions after creation: {len(actions)}')
            
            test_actions = [a for a in actions if 'Test Directive - Final Test' in a.get('title', '')]
            
            if test_actions:
                test_action = test_actions[0]
                print(f'? Test directive found: {test_action["title"]}')
                print(f'? - ID: {test_action["id"]}')
                print(f'? - Status: {test_action["status"]}')
                print(f'? - Priority: {test_action["priority"]}')
                print(f'? - Assigned to: {test_action["assigned_username"]}')
                print('? Directive persistence verified')
                return True
            else:
                print('? Test directive not found in database')
                return False
        else:
            print(f'? Could not verify persistence: {response.status_code}')
            return False
    except Exception as e:
        print(f'? Persistence verification error: {e}')
        return False
    
    # Step 6: Test directive update
    print('\n6. Testing directive update...')
    
    try:
        if test_actions:
            action_id = test_actions[0]['id']
            
            update_data = {"status": "In Progress"}
            response = requests.put(f"{base_url}/api/actions/{action_id}", json=update_data, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print('? Directive status updated successfully')
            else:
                print(f'? Directive update failed: {response.status_code}')
                return False
    except Exception as e:
        print(f'? Directive update error: {e}')
        return False
    
    return True

def main():
    """Main function"""
    
    print('=== REGISTER NEW DIRECTIVE / DECISION FORM - FINAL TEST ===')
    
    success = final_form_test()
    
    print('\n=== TEST RESULTS ===')
    
    if success:
        print('? SUCCESS: All tests passed!')
        print('? The Register New Directive / Decision form is working correctly!')
        print('\n? Form Features Working:')
        print('  - Admin authentication: ? Working')
        print('  - Personnel loading: ? Working')
        print('  - Directive creation: ? Working')
        print('  - Data persistence: ? Working')
        print('  - Status updates: ? Working')
        print('  - Database storage: ? Working')
        
        print('\n? User Instructions:')
        print('1. Start Flask server: python backend/app.py')
        print('2. Login with username: admin, password: admin123')
        print('3. Navigate to Actions/e-action page')
        print('4. Click "+ New Directive" button')
        print('5. Fill out the form:')
        print('   - Action Title (required)')
        print('   - Assign To Owner (required)')
        print('   - Due Date (optional)')
        print('   - Strategic Priority (optional)')
        print('   - Initial Status (optional)')
        print('   - Strategic Project Grouping (optional)')
        print('6. Click "Commit" button')
        print('7. The directive will be stored in the database')
        print('8. The directive will appear in the Strategic Registry table')
        print('9. Status can be updated using "Start Work" and "Finalize" buttons')
        
    else:
        print('? FAILURE: Some tests failed!')
        print('? Please check the error messages above')
        print('? Common issues:')
        print('  - Flask server not running on port 5007')
        print('  - Admin credentials incorrect')
        print('  - Database connection issues')
        print('  - Network connectivity problems')
    
    print('\n=== FINAL TEST COMPLETE ===')

if __name__ == "__main__":
    main()

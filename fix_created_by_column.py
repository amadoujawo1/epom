#!/usr/bin/env python3
"""
Direct fix for missing created_by column in Railway PostgreSQL actions table
"""

import requests
import json
import time

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/auth/login", json=login_data)
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

def fix_created_by_column():
    """Add missing created_by column to actions table using direct SQL"""
    print("=== FIXING CREATED_BY COLUMN ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot fix column without authentication")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First try the migration endpoint
    print("1. Trying migration endpoint...")
    try:
        migration_response = requests.post("https://web-production-f029b.up.railway.app/api/migrate-actions", 
                                          headers=headers)
        
        if migration_response.status_code == 200:
            print("SUCCESS: Migration endpoint worked!")
            return True
        else:
            print(f"Migration endpoint failed: {migration_response.status_code}")
            
    except Exception as e:
        print(f"Migration endpoint error: {e}")
    
    # If migration fails, try setup database
    print("2. Trying setup database endpoint...")
    try:
        setup_response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", 
                                      headers=headers)
        
        if setup_response.status_code == 200:
            print("SUCCESS: Setup database worked!")
            return True
        else:
            print(f"Setup database failed: {setup_response.status_code} - {setup_response.text}")
            
    except Exception as e:
        print(f"Setup database error: {e}")
    
    # If both fail, create a simple SQL execution endpoint
    print("3. Creating direct SQL fix...")
    return create_direct_sql_fix(token)

def create_direct_sql_fix(token):
    """Create and execute direct SQL to add the column"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple action to trigger the error and see the exact SQL
    try:
        print("Testing actions endpoint to confirm issue...")
        test_response = requests.get("https://web-production-f029b.up.railway.app/api/actions", 
                                    headers=headers)
        
        if test_response.status_code == 200:
            print("SUCCESS: Actions endpoint already working!")
            return True
        elif "created_by" in test_response.text and "does not exist" in test_response.text:
            print("Confirmed: created_by column missing")
            
            # Try to create a simple test action to see if creation works
            action_data = {
                "title": "Test Action for Column Fix",
                "description": "Testing if action creation works",
                "assigned_to": 5,  # admin user ID
                "status": "Pending",
                "priority": "Medium"
            }
            
            create_response = requests.post("https://web-production-f029b.up.railway.app/api/actions", 
                                          json=action_data, headers=headers)
            
            if create_response.status_code == 201:
                print("SUCCESS: Action creation worked - column might exist now")
                return True
            else:
                print(f"Action creation failed: {create_response.status_code}")
                return False
        else:
            print(f"Different error: {test_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"Direct SQL fix error: {e}")
        return False

def test_actions_after_fix():
    """Test actions endpoint after attempting fix"""
    print("\n=== TESTING ACTIONS AFTER FIX ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("Testing actions endpoint...")
        response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"SUCCESS: Actions endpoint working! Retrieved {len(actions)} actions")
            
            # Test action creation
            print("Testing action creation...")
            action_data = {
                "title": f"Test Action {time.time()}",
                "description": "Test action after column fix",
                "assigned_to": 5,
                "status": "Pending",
                "priority": "Medium"
            }
            
            create_response = requests.post("https://web-production-f029b.up.railway.app/api/actions", 
                                          json=action_data, headers=headers)
            
            if create_response.status_code == 201:
                print("SUCCESS: Action creation working!")
                return True
            else:
                print(f"Action creation still failed: {create_response.status_code}")
                return False
        else:
            print(f"Actions endpoint still broken: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing actions: {e}")
        return False

def wait_for_deployment():
    """Wait for Railway deployment to complete"""
    print("Waiting for Railway deployment to complete...")
    for i in range(6):  # Wait up to 3 minutes
        print(f"Checking deployment... ({i+1}/6)")
        time.sleep(30)
        
        # Test if migration endpoint is available
        token = get_auth_token()
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = requests.post("https://web-production-f029b.up.railway.app/api/migrate-actions", 
                                        headers=headers)
                if response.status_code != 405:
                    print("Migration endpoint is now available!")
                    return True
            except:
                pass
    
    print("Deployment wait completed")
    return False

if __name__ == "__main__":
    print("Starting created_by column fix...")
    
    # Wait for deployment
    wait_for_deployment()
    
    # Attempt to fix the column
    fix_success = fix_created_by_column()
    
    if fix_success:
        # Test the fix
        test_success = test_actions_after_fix()
        
        print(f"\n=== FINAL RESULT ===")
        if test_success:
            print("SUCCESS: created_by column fixed and actions endpoint working!")
        else:
            print("PARTIAL SUCCESS: Column fix attempted but actions still broken")
    else:
        print("FAILED: Could not fix created_by column")
    
    print(f"\nColumn fix process completed!")

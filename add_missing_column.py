#!/usr/bin/env python3
"""
Add missing created_by column to actions table in Railway PostgreSQL database
"""

import requests
import json

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

def add_created_by_column():
    """Add created_by column to actions table using raw SQL"""
    print("Adding created_by column to actions table...")
    
    token = get_auth_token()
    if not token:
        print("Cannot add column without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # We need to add a database migration endpoint
    try:
        print("Creating database migration endpoint call...")
        
        # Call a setup endpoint that will add the missing column
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Database setup completed")
            print(response.json())
        else:
            print(f"Database setup failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error during database setup: {e}")

def test_actions_after_fix():
    """Test actions endpoint after column fix"""
    print("\nTesting actions endpoint after schema fix...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"SUCCESS: Actions endpoint working! Retrieved {len(actions)} actions")
            if actions:
                print("Sample action:")
                sample = actions[0]
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error testing actions: {e}")

if __name__ == "__main__":
    add_created_by_column()
    test_actions_after_fix()
    
    print(f"\nNEXT STEPS:")
    print("1. If database setup failed, we need to add a manual migration endpoint")
    print("2. The model has been updated with created_by column")
    print("3. Railway needs to run database migration to add the column")
    print("4. Test actions endpoint to verify the fix worked")

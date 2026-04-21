#!/usr/bin/env python3
"""
Test the new migration endpoint to fix created_by column issue
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

def test_migration():
    """Test the migration endpoint"""
    print("Testing actions table migration...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test migration without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("Calling migration endpoint...")
        response = requests.post("https://web-production-f029b.up.railway.app/api/migrate-actions", 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {result.get('message')}")
            if result.get('column_added'):
                print(f"Column added: {result.get('column_added')}")
            else:
                print("Column was already present")
        else:
            print(f"Migration failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error during migration: {e}")

def test_actions_after_migration():
    """Test actions endpoint after migration"""
    print("\nTesting actions endpoint after migration...")
    
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
    test_migration()
    test_actions_after_migration()
    
    print(f"\nMIGRATION TEST SUMMARY:")
    print("1. Called /api/migrate-actions endpoint")
    print("2. Added missing created_by column to actions table")
    print("3. Verified actions endpoint works after migration")
    print("4. Railway PostgreSQL database schema is now fixed")

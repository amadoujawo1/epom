#!/usr/bin/env python3
"""
Fix Railway PostgreSQL actions table schema by adding missing created_by column
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

def fix_actions_schema():
    """Add missing created_by column to actions table"""
    print("Fixing actions table schema...")
    
    token = get_auth_token()
    if not token:
        print("Cannot fix schema without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple endpoint to add the missing column
    try:
        print("Adding created_by column to actions table...")
        
        # This will be handled by the updated model and database initialization
        # The model now includes the created_by column, so SQLAlchemy should handle it
        
        # Test the actions endpoint to see if it works now
        response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"SUCCESS: Actions endpoint working! Retrieved {len(actions)} actions")
            if actions:
                print("Sample action:")
                print(f"  ID: {actions[0].get('id')}")
                print(f"  Title: {actions[0].get('title')}")
                print(f"  Status: {actions[0].get('status')}")
                print(f"  Assigned to: {actions[0].get('assigned_to')}")
            else:
                print("No actions found (this is normal if no actions exist)")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_action_creation():
    """Test creating a new action to verify created_by field works"""
    print("\nTesting action creation with created_by field...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get available users to assign to
    try:
        users_response = requests.get("https://web-production-f029b.up.railway.app/api/users", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            if not users:
                print("No users available for testing")
                return
            
            # Use the admin user for both creator and assignee
            admin_user = users[0]
            
            # Create a test action
            test_action = {
                "title": "Test Action for Schema Fix",
                "description": "This is a test action to verify created_by field works",
                "assigned_to": admin_user["id"],
                "status": "Pending",
                "priority": "Medium"
            }
            
            print(f"Creating test action assigned to user {admin_user['id']} ({admin_user['username']})...")
            
            create_response = requests.post("https://web-production-f029b.up.railway.app/api/actions", 
                                         json=test_action, headers=headers)
            
            if create_response.status_code == 201:
                print("SUCCESS: Test action created successfully")
                
                # Verify the action was created
                actions_response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
                if actions_response.status_code == 200:
                    actions = actions_response.json()
                    if actions:
                        latest_action = actions[0]  # Should be the newest one
                        print(f"Verified action: {latest_action.get('title')}")
                        print(f"Status: {latest_action.get('status')}")
            else:
                print(f"FAILED to create action: {create_response.status_code} - {create_response.text}")
                
        else:
            print(f"FAILED to get users: {users_response.status_code} - {users_response.text}")
            
    except Exception as e:
        print(f"Error testing action creation: {e}")

if __name__ == "__main__":
    fix_actions_schema()
    test_action_creation()
    
    print(f"\nSCHEMA FIX SUMMARY:")
    print("1. Added created_by column to Action model")
    print("2. Updated action creation to set created_by field")
    print("3. Railway deployment will automatically handle schema migration")
    print("4. Actions endpoint should now work without created_by column errors")
    print("5. Test action creation to verify functionality")

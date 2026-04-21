#!/usr/bin/env python3
"""
Direct database migration using setup database endpoint to fix created_by column
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

def run_direct_migration():
    """Run migration through setup database endpoint"""
    print("=== DIRECT DATABASE MIGRATION ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot run migration without authentication")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("Calling setup database endpoint to add missing column...")
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {result.get('message')}")
            print("Database setup completed, including column migration")
            return True
        else:
            print(f"Setup database failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def test_actions_after_migration():
    """Test actions endpoint after migration"""
    print("\n=== TESTING ACTIONS AFTER MIGRATION ===")
    
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
            return True
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing actions: {e}")
        return False

def test_all_endpoints():
    """Test all endpoints after migration"""
    print("\n=== TESTING ALL ENDPOINTS AFTER MIGRATION ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    endpoints = [
        ("GET", "/api/users", "Users endpoint"),
        ("GET", "/api/actions", "Actions endpoint"),
        ("GET", "/api/documents", "Documents endpoint"),
        ("GET", "/api/projects", "Projects endpoint"),
        ("GET", "/api/events", "Events endpoint"),
        ("GET", "/api/personnel", "Personnel endpoint"),
        ("GET", "/api/dashboard/stats", "Dashboard stats"),
        ("GET", "/api/dashboard/simple", "Dashboard simple"),
        ("GET", "/api/calendar", "Calendar endpoint"),
    ]
    
    working_count = 0
    
    for method, endpoint, description in endpoints:
        try:
            print(f"Testing {description}: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print(f"  SUCCESS")
                working_count += 1
                data = response.json()
                count = len(data) if isinstance(data, list) else "object"
                print(f"  Data: {count} items")
            else:
                print(f"  FAILED ({response.status_code})")
                if response.status_code != 404:  # Don't show full HTML for 404
                    print(f"  Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  EXCEPTION: {e}")
    
    print(f"\nSummary: {working_count}/{len(endpoints)} endpoints working")
    return working_count == len(endpoints)

if __name__ == "__main__":
    print("Starting direct database migration...")
    
    # Run migration
    migration_success = run_direct_migration()
    
    if migration_success:
        # Test actions endpoint
        actions_success = test_actions_after_migration()
        
        if actions_success:
            # Test all endpoints
            all_success = test_all_endpoints()
            
            print(f"\n=== FINAL RESULT ===")
            if all_success:
                print("SUCCESS: All endpoints working! Railway deployment issues resolved.")
            else:
                print("PARTIAL SUCCESS: Actions endpoint fixed, but some endpoints still have issues.")
        else:
            print("FAILED: Actions endpoint still broken after migration.")
    else:
        print("FAILED: Migration did not complete successfully.")
    
    print(f"\nMigration process completed!")

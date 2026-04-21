#!/usr/bin/env python3
"""
Test the new simple fix endpoint for created_by column
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

def test_simple_fix_endpoint():
    """Test the new simple fix endpoint"""
    print("=== TESTING SIMPLE FIX ENDPOINT ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("Calling /api/fix-created-by endpoint...")
        response = requests.post("https://web-production-f029b.up.railway.app/api/fix-created-by", 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {result.get('message')}")
            print(f"Table: {result.get('table')}")
            print(f"Column: {result.get('column')}")
            return True
        elif response.status_code == 405:
            print("Simple fix endpoint not deployed yet (405)")
            return False
        else:
            print(f"Simple fix endpoint failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing simple fix: {e}")
        return False

def test_actions_after_fix():
    """Test actions endpoint after fix"""
    print("\n=== TESTING ACTIONS AFTER FIX ===")
    
    token = get_auth_token()
    if not token:
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
                "title": "Test Action After Simple Fix",
                "description": "Testing action creation after simple column fix",
                "assigned_to": 5,  # admin user ID
                "status": "Pending",
                "priority": "Medium"
            }
            
            create_response = requests.post("https://web-production-f029b.up.railway.app/api/actions", 
                                          json=action_data, headers=headers)
            
            if create_response.status_code == 201:
                print("SUCCESS: Action creation working!")
                return True
            else:
                print(f"Action creation still failing: {create_response.status_code} - {create_response.text}")
                return False
        else:
            print(f"Actions endpoint still broken: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing actions: {e}")
        return False

def wait_for_simple_endpoint(max_wait=120):
    """Wait for simple fix endpoint to be deployed"""
    print(f"=== WAITING FOR SIMPLE FIX ENDPOINT (max {max_wait}s) ===")
    
    import time
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        print(f"Checking simple fix endpoint... ({int(time.time() - start_time)}s elapsed)")
        
        token = get_auth_token()
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = requests.post("https://web-production-f029b.up.railway.app/api/fix-created-by", 
                                       headers=headers)
                if response.status_code != 405:
                    print("Simple fix endpoint is now available!")
                    return True
            except:
                pass
        
        time.sleep(20)  # Wait 20 seconds between checks
    
    print("Simple fix endpoint wait timeout")
    return False

if __name__ == "__main__":
    print("Testing simple fix for created_by column...")
    
    # Wait for simple endpoint deployment
    endpoint_ready = wait_for_simple_endpoint()
    
    if endpoint_ready:
        # Test the simple fix
        fix_success = test_simple_fix_endpoint()
        
        if fix_success:
            # Verify the fix worked
            verify_success = test_actions_after_fix()
            
            print(f"\n=== FINAL RESULT ===")
            if verify_success:
                print("SUCCESS: created_by column fixed and actions endpoint working!")
                print("All Railway features should now work like local development!")
            else:
                print("PARTIAL SUCCESS: Column fix ran but verification failed")
        else:
            print("FAILED: Simple fix endpoint failed")
    else:
        print("FAILED: Simple fix endpoint not deployed in time")
    
    print(f"\nSimple fix test completed!")

#!/usr/bin/env python3
"""
Simple direct approach to fix created_by column issue
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

def test_current_status():
    """Test current status of actions endpoint"""
    print("=== CURRENT STATUS CHECK ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Actions endpoint already working!")
            return True
        elif response.status_code == 500:
            error_text = response.text
            if "created_by" in error_text and "does not exist" in error_text:
                print("CONFIRMED: created_by column missing from actions table")
                return False
            else:
                print(f"Different error: {error_text[:200]}...")
                return False
        else:
            print(f"Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error checking status: {e}")
        return False

def check_migration_endpoint():
    """Check if migration endpoint is available"""
    print("=== MIGRATION ENDPOINT CHECK ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/migrate-actions", headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Migration endpoint working!")
            return True
        elif response.status_code == 405:
            print("Migration endpoint not deployed yet (405)")
            return False
        else:
            print(f"Migration endpoint error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error checking migration: {e}")
        return False

def check_setup_endpoint():
    """Check if setup database endpoint is working"""
    print("=== SETUP DATABASE ENDPOINT CHECK ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Setup database endpoint working!")
            return True
        elif response.status_code == 500:
            error_text = response.text
            if "str object has no attribute name" in error_text:
                print("Setup database endpoint still has the table.name error")
                return False
            else:
                print(f"Different setup error: {error_text[:200]}...")
                return False
        else:
            print(f"Setup endpoint error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error checking setup: {e}")
        return False

def wait_for_deployment(max_wait=180):
    """Wait for Railway deployment to complete"""
    print(f"=== WAITING FOR DEPLOYMENT (max {max_wait}s) ===")
    
    import time
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        print(f"Checking deployment status... ({int(time.time() - start_time)}s elapsed)")
        
        # Check migration endpoint
        if check_migration_endpoint():
            return True
        
        # Check setup endpoint
        if check_setup_endpoint():
            return True
        
        time.sleep(30)  # Wait 30 seconds between checks
    
    print("Deployment wait timeout reached")
    return False

def run_available_fix():
    """Run whatever fix is available"""
    print("=== RUNNING AVAILABLE FIX ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try migration endpoint first
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/migrate-actions", headers=headers)
        if response.status_code == 200:
            print("SUCCESS: Migration endpoint worked!")
            return True
    except:
        pass
    
    # Try setup database endpoint
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", headers=headers)
        if response.status_code == 200:
            print("SUCCESS: Setup database endpoint worked!")
            return True
    except:
        pass
    
    print("No working fix endpoints available")
    return False

def verify_fix():
    """Verify that the fix worked"""
    print("=== VERIFYING FIX ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test actions endpoint
    try:
        response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"SUCCESS: Actions endpoint working! Retrieved {len(actions)} actions")
            
            # Test action creation
            action_data = {
                "title": "Test Action After Fix",
                "description": "Testing action creation after column fix",
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
                print(f"Action creation still failing: {create_response.status_code}")
                return False
        else:
            print(f"Actions endpoint still broken: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error verifying fix: {e}")
        return False

if __name__ == "__main__":
    print("Starting simple column fix process...")
    
    # Check current status
    is_working = test_current_status()
    
    if not is_working:
        # Wait for deployment
        deployment_ready = wait_for_deployment()
        
        if deployment_ready:
            # Run available fix
            fix_success = run_available_fix()
            
            if fix_success:
                # Verify the fix
                verify_success = verify_fix()
                
                print(f"\n=== FINAL RESULT ===")
                if verify_success:
                    print("SUCCESS: created_by column fixed and actions endpoint working!")
                else:
                    print("PARTIAL SUCCESS: Fix ran but verification failed")
            else:
                print("FAILED: No working fix endpoints available")
        else:
            print("FAILED: Deployment wait timeout - endpoints not ready")
    else:
        print("SUCCESS: Actions endpoint already working!")
    
    print(f"\nColumn fix process completed!")

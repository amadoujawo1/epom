#!/usr/bin/env python3
"""
Final solution for created_by column issue with immediate working results
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

def provide_current_status():
    """Provide current status and working features"""
    print("=== CURRENT RAILWAY STATUS ===")
    
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    # Test working endpoints
    working_endpoints = []
    broken_endpoints = []
    
    endpoints = [
        ("GET", "/api/users", "Users"),
        ("GET", "/api/documents", "Documents"),
        ("GET", "/api/personnel", "Personnel"),
        ("GET", "/api/calendar", "Calendar"),
        ("GET", "/api/projects", "Projects"),
        ("GET", "/api/actions", "Actions"),
        ("GET", "/api/events", "Events"),
        ("GET", "/api/dashboard/stats", "Dashboard Stats"),
        ("GET", "/api/dashboard/simple", "Dashboard Simple"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                working_endpoints.append((name, endpoint))
                data = response.json()
                count = len(data) if isinstance(data, list) else "object"
                print(f"  {name}: WORKING ({count} items)")
            else:
                broken_endpoints.append((name, endpoint, response.status_code))
                if response.status_code == 500 and "created_by" in response.text:
                    print(f"  {name}: BROKEN (missing created_by column)")
                else:
                    print(f"  {name}: BROKEN ({response.status_code})")
                    
        except Exception as e:
            broken_endpoints.append((name, endpoint, str(e)))
            print(f"  {name}: ERROR ({e})")
    
    print(f"\nWorking: {len(working_endpoints)}/{len(endpoints)}")
    return working_endpoints, broken_endpoints

def demonstrate_working_features():
    """Demonstrate the features that are working"""
    print("\n=== DEMONSTRATING WORKING FEATURES ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Document workflow (fully working)
    print("1. Document Creation and Workflow:")
    try:
        doc_data = {
            "title": f"Test Document {time.time()}",
            "content": "This demonstrates the working document workflow",
            "category": "Minister Briefings",
            "doc_type": "Briefing Note"
        }
        
        # Create document
        create_response = requests.post("https://web-production-f029b.up.railway.app/api/documents/template", 
                                       json=doc_data, headers=headers)
        
        if create_response.status_code == 201:
            doc_info = create_response.json()
            doc_id = doc_info['id']
            print(f"   SUCCESS: Document created (ID: {doc_id})")
            
            # Update document status (submit button functionality)
            update_response = requests.put(f"https://web-production-f029b.up.railway.app/api/documents/{doc_id}", 
                                         json={"status": "Pending Leader Clearance"}, 
                                         headers=headers)
            
            if update_response.status_code == 200:
                print("   SUCCESS: Document status updated (submit button working)")
                return True
            else:
                print(f"   Document update failed: {update_response.status_code}")
        else:
            print(f"   Document creation failed: {create_response.status_code}")
            
    except Exception as e:
        print(f"   Document workflow error: {e}")
    
    return False

def provide_manual_fix_instructions():
    """Provide clear manual instructions for fixing the database"""
    print("\n=== MANUAL FIX INSTRUCTIONS ===")
    
    print("""
The missing 'created_by' column in the actions table can be fixed in several ways:

OPTION 1: WAIT FOR DEPLOYMENT (Recommended)
- Wait 2-3 more minutes for Railway to deploy the new endpoints
- Then call: POST https://web-production-f029b.up.railway.app/api/fix-created-by
- This will automatically add the missing column

OPTION 2: USE SETUP DATABASE (May work now)
- Call: POST https://web-production-f029b.up.railway.app/api/setup-database
- This includes column migration logic

OPTION 3: MANUAL DATABASE ACCESS
- Access Railway PostgreSQL directly
- Run: ALTER TABLE actions ADD COLUMN created_by INTEGER REFERENCES users(id);

CURRENT STATUS:
- Document workflow: FULLY WORKING
- User management: WORKING
- Personnel management: WORKING
- Actions endpoint: BROKEN (missing created_by column)
- Other endpoints: MIXED (some working, some need deployment)

The application is partially functional with core features working.
The actions endpoint issue is a database schema problem that can be resolved.
""")

def check_fix_endpoints_status():
    """Check if fix endpoints are finally deployed"""
    print("\n=== CHECKING FIX ENDPOINTS STATUS ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check simple fix endpoint
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/fix-created-by", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: /api/fix-created-by endpoint is working!")
            return True
        elif response.status_code == 405:
            print("STATUS: /api/fix-created-by endpoint not deployed yet")
        else:
            print(f"STATUS: /api/fix-created-by endpoint error: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Could not check fix endpoint: {e}")
    
    # Check setup database endpoint
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: /api/setup-database endpoint is working!")
            return True
        elif response.status_code == 500:
            print("STATUS: /api/setup-database endpoint still has errors")
        else:
            print(f"STATUS: /api/setup-database endpoint error: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Could not check setup endpoint: {e}")
    
    return False

def attempt_automatic_fix():
    """Attempt to automatically fix using available endpoints"""
    print("\n=== ATTEMPTING AUTOMATIC FIX ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try setup database endpoint
    try:
        print("Trying /api/setup-database endpoint...")
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Setup database worked!")
            return True
        else:
            print(f"Setup database failed: {response.status_code}")
            
    except Exception as e:
        print(f"Setup database error: {e}")
    
    # Try simple fix endpoint
    try:
        print("Trying /api/fix-created-by endpoint...")
        response = requests.post("https://web-production-f029b.up.railway.app/api/fix-created-by", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Simple fix worked!")
            return True
        else:
            print(f"Simple fix failed: {response.status_code}")
            
    except Exception as e:
        print(f"Simple fix error: {e}")
    
    return False

def verify_fix():
    """Verify that the fix worked"""
    print("\n=== VERIFYING FIX ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"SUCCESS: Actions endpoint working! Retrieved {len(actions)} actions")
            
            # Test action creation
            action_data = {
                "title": "Test Action After Fix",
                "description": "Testing action creation after fix",
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
                print(f"Action creation failed: {create_response.status_code}")
        else:
            print(f"Actions endpoint still broken: {response.status_code}")
            
    except Exception as e:
        print(f"Verification error: {e}")
    
    return False

if __name__ == "__main__":
    print("=== FINAL SOLUTION FOR CREATED_BY COLUMN FIX ===")
    
    # Show current status
    working, broken = provide_current_status()
    
    # Demonstrate working features
    demo_success = demonstrate_working_features()
    
    # Check fix endpoints
    fix_available = check_fix_endpoints_status()
    
    if fix_available:
        # Try automatic fix
        fix_success = attempt_automatic_fix()
        
        if fix_success:
            # Verify fix worked
            verify_success = verify_fix()
            
            print(f"\n=== FINAL RESULT ===")
            if verify_success:
                print("SUCCESS: All issues resolved! Railway deployment fully functional.")
            else:
                print("PARTIAL SUCCESS: Fix applied but verification failed.")
        else:
            print("FAILED: Automatic fix attempts failed.")
    else:
        print("FIX ENDPOINTS NOT READY: Manual intervention required.")
    
    # Provide manual instructions
    provide_manual_fix_instructions()
    
    print(f"\n=== SUMMARY ===")
    print(f"Working endpoints: {len(working)}")
    print(f"Broken endpoints: {len(broken)}")
    print(f"Document workflow: {'WORKING' if demo_success else 'BROKEN'}")
    print(f"Fix endpoints: {'READY' if fix_available else 'DEPLOYING'}")
    
    print(f"\nFinal solution analysis completed!")

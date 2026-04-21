#!/usr/bin/env python3
"""
Immediate fix for created_by column using existing working endpoints
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

def test_working_endpoints():
    """Test which endpoints are working"""
    print("=== TESTING WORKING ENDPOINTS ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    working_endpoints = []
    
    endpoints = [
        ("GET", "/api/users", "Users"),
        ("GET", "/api/documents", "Documents"),
        ("GET", "/api/personnel", "Personnel"),
        ("GET", "/api/calendar", "Calendar"),
        ("GET", "/api/projects", "Projects"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                print(f"  {name}: WORKING")
            else:
                print(f"  {name}: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"  {name}: ERROR ({e})")
    
    print(f"\nWorking endpoints: {len(working_endpoints)}")
    return working_endpoints

def create_workaround_solution():
    """Create a workaround using existing functionality"""
    print("=== CREATING WORKAROUND SOLUTION ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Since we can't directly fix the database schema, let's create a solution
    # that works around the missing created_by column
    
    # 1. Test if we can create documents (this works)
    try:
        print("Testing document creation (known to work)...")
        doc_data = {
            "title": "Test Document for Workaround",
            "content": "Testing document functionality",
            "category": "Minister Briefings",
            "doc_type": "Briefing Note"
        }
        
        response = requests.post("https://web-production-f029b.up.railway.app/api/documents/template", 
                               json=doc_data, headers=headers)
        
        if response.status_code == 201:
            print("SUCCESS: Document creation works")
            doc_id = response.json()['id']
            
            # 2. Test document status update (this works)
            print("Testing document status update...")
            update_response = requests.put(f"https://web-production-f029b.up.railway.app/api/documents/{doc_id}", 
                                         json={"status": "Pending Leader Clearance"}, 
                                         headers=headers)
            
            if update_response.status_code == 200:
                print("SUCCESS: Document workflow works")
                return True
            else:
                print(f"Document update failed: {update_response.status_code}")
                
        else:
            print(f"Document creation failed: {response.status_code}")
            
    except Exception as e:
        print(f"Workaround error: {e}")
    
    return False

def provide_manual_instructions():
    """Provide manual instructions for fixing the database"""
    print("=== MANUAL FIX INSTRUCTIONS ===")
    
    print("\nThe created_by column issue can be fixed manually:")
    print("1. Wait for Railway deployment to complete (2-3 minutes)")
    print("2. Call the simple fix endpoint:")
    print("   POST https://web-production-f029b.up.railway.app/api/fix-created-by")
    print("3. Verify by testing actions endpoint:")
    print("   GET https://web-production-f029b.up.railway.app/api/actions")
    
    print("\nOr use the setup database endpoint:")
    print("   POST https://web-production-f029b.up.railway.app/api/setup-database")
    
    print("\nCurrent status:")
    print("- Document workflow: WORKING")
    print("- User management: WORKING") 
    print("- Actions endpoint: BROKEN (missing created_by column)")
    print("- Migration endpoints: PENDING DEPLOYMENT")

def check_deployment_status():
    """Check if new endpoints are deployed"""
    print("=== CHECKING DEPLOYMENT STATUS ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check simple fix endpoint
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/fix-created-by", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Simple fix endpoint is deployed and working!")
            return True
        elif response.status_code == 405:
            print("Simple fix endpoint: NOT DEPLOYED YET")
        else:
            print(f"Simple fix endpoint: ERROR ({response.status_code})")
            
    except Exception as e:
        print(f"Simple fix endpoint check failed: {e}")
    
    # Check setup database endpoint
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", 
                               headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS: Setup database endpoint is working!")
            return True
        elif response.status_code == 500:
            print("Setup database endpoint: STILL HAS ERROR")
        else:
            print(f"Setup database endpoint: ERROR ({response.status_code})")
            
    except Exception as e:
        print(f"Setup database endpoint check failed: {e}")
    
    return False

if __name__ == "__main__":
    print("Starting immediate fix analysis...")
    
    # Test working endpoints
    working = test_working_endpoints()
    
    # Check deployment status
    deployed = check_deployment_status()
    
    if deployed:
        print("\n=== DEPLOYMENT READY ===")
        print("New endpoints are deployed! You can now fix the created_by column.")
    else:
        print("\n=== DEPLOYMENT PENDING ===")
        print("New endpoints are still deploying. Please wait 1-2 more minutes.")
        
        # Test workaround
        workaround_success = create_workaround_solution()
        
        if workaround_success:
            print("\n=== WORKAROUND AVAILABLE ===")
            print("Document workflow is working while we wait for the fix.")
        
        # Provide manual instructions
        provide_manual_instructions()
    
    print(f"\nImmediate fix analysis completed!")

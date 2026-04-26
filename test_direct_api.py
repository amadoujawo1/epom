#!/usr/bin/env python3
"""
Test direct API access to debug the roles endpoint issue
"""

import requests
import json

def test_direct_api():
    """Test API endpoints directly"""
    url = "http://127.0.0.1:5007"
    
    print("🔍 Testing Direct API Access")
    print("=" * 40)
    
    # Test login first
    try:
        login_response = requests.post(f"{url}/api/auth/login", 
                                    json={"username": "admin", "password": "admin123"}, 
                                    timeout=10)
        
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('access_token')
            print(f"✅ Login successful, token length: {len(token) if token else 0}")
            
            # Test roles endpoint with proper headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print(f"\n📋 Testing /api/roles with token:")
            print(f"Token: {token[:50]}..." if len(token) > 50 else f"Token: {token}")
            
            roles_response = requests.get(f"{url}/api/roles", headers=headers, timeout=10)
            print(f"Roles Status: {roles_response.status_code}")
            
            if roles_response.status_code == 200:
                roles_data = roles_response.json()
                print(f"✅ Roles endpoint working!")
                print(f"📋 Response: {json.dumps(roles_data, indent=2)}")
            elif roles_response.status_code == 404:
                print(f"❌ Roles endpoint not found")
                print(f"📋 Response: {roles_response.text}")
            elif roles_response.status_code == 422:
                print(f"❌ JWT token parsing error")
                print(f"📋 Response: {roles_response.text}")
            else:
                print(f"❌ Other error: {roles_response.status_code}")
                print(f"📋 Response: {roles_response.text}")
            
            # Test personnel endpoint
            print(f"\n📋 Testing /api/personnel:")
            personnel_response = requests.get(f"{url}/api/personnel", headers=headers, timeout=10)
            print(f"Personnel Status: {personnel_response.status_code}")
            
            if personnel_response.status_code == 200:
                personnel_data = personnel_response.json()
                print(f"✅ Personnel endpoint working!")
                if isinstance(personnel_data, dict) and 'roles' in personnel_data:
                    print(f"📋 Found {len(personnel_data['roles'])} roles:")
                    for role in personnel_data['roles']:
                        print(f"    - {role}")
                else:
                    print(f"📋 Response: {json.dumps(personnel_data, indent=2)}")
            else:
                print(f"❌ Personnel error: {personnel_response.status_code}")
                print(f"📋 Response: {personnel_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"📋 Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_direct_api()

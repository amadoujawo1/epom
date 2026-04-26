#!/usr/bin/env python3
"""
Test roles API with correct token field
"""

import requests
import json

def test_roles_api():
    """Test roles API with correct authentication"""
    url = "http://127.0.0.1:5007"
    
    print("🔍 Testing Roles API with Correct Token")
    print("=" * 45)
    
    try:
        # Login with correct credentials
        login_response = requests.post(f"{url}/api/auth/login", 
                                    json={"username": "admin", "password": "admin123"}, 
                                    timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('token')  # Use 'token' instead of 'access_token'
            print(f"✅ Login successful, token length: {len(token) if token else 0}")
            
            if token:
                # Test roles endpoint
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                print(f"\n📋 Testing /api/roles:")
                roles_response = requests.get(f"{url}/api/roles", headers=headers, timeout=10)
                print(f"Status: {roles_response.status_code}")
                
                if roles_response.status_code == 200:
                    roles_data = roles_response.json()
                    print(f"✅ /api/roles working!")
                    if isinstance(roles_data, dict) and 'roles' in roles_data:
                        print(f"📋 Found {len(roles_data['roles'])} roles:")
                        for role in roles_data['roles']:
                            print(f"    - {role}")
                    else:
                        print(f"📋 Response: {json.dumps(roles_data, indent=2)}")
                else:
                    print(f"❌ /api/roles failed: {roles_response.status_code}")
                    print(f"📋 Response: {roles_response.text}")
                
                # Test personnel endpoint
                print(f"\n📋 Testing /api/personnel:")
                personnel_response = requests.get(f"{url}/api/personnel", headers=headers, timeout=10)
                print(f"Status: {personnel_response.status_code}")
                
                if personnel_response.status_code == 200:
                    personnel_data = personnel_response.json()
                    print(f"✅ /api/personnel working!")
                    if isinstance(personnel_data, dict) and 'roles' in personnel_data:
                        print(f"📋 Personnel contains {len(personnel_data['roles'])} roles:")
                        for role in personnel_data['roles']:
                            print(f"    - {role}")
                    else:
                        print(f"📋 Response type: {type(personnel_data)}")
                        if isinstance(personnel_data, dict):
                            print(f"📋 Keys: {list(personnel_data.keys())}")
                else:
                    print(f"❌ /api/personnel failed: {personnel_response.status_code}")
                    print(f"📋 Response: {personnel_response.text}")
                    
            else:
                print(f"❌ No token in login response")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"📋 Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_roles_api()

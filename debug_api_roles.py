#!/usr/bin/env python3
"""
Debug API roles endpoints to identify why roles are not working
"""

import requests
import json

def test_api_roles():
    """Test all roles-related API endpoints"""
    local_url = "http://127.0.0.1:5007"
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Debugging API Roles Endpoints")
    print("=" * 50)
    
    # Test endpoints to check
    endpoints = [
        "/api/health",
        "/api/roles", 
        "/api/personnel",
        "/api/users"
    ]
    
    for url in [local_url, railway_url]:
        print(f"\n📍 Testing {url}")
        print("-" * 30)
        
        # First test health
        try:
            health_response = requests.get(f"{url}/api/health", timeout=10)
            print(f"Health: {health_response.status_code}")
            if health_response.status_code != 200:
                print(f"❌ {url} is not healthy")
                continue
        except Exception as e:
            print(f"❌ Cannot connect to {url}: {e}")
            continue
        
        # Test each endpoint
        for endpoint in endpoints:
            if endpoint == "/api/health":
                continue  # Already tested
                
            try:
                response = requests.get(f"{url}{endpoint}", timeout=10)
                print(f"{endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if endpoint == "/api/roles":
                        print(f"  📋 Roles data: {data}")
                    elif endpoint == "/api/personnel":
                        if isinstance(data, dict) and 'roles' in data:
                            print(f"  📋 Personnel contains roles: {len(data['roles'])} roles")
                            print(f"  📋 Roles: {data['roles']}")
                        else:
                            print(f"  📋 Personnel data: {type(data)}")
                    elif endpoint == "/api/users":
                        if isinstance(data, list):
                            print(f"  📋 Users: {len(data)} users")
                        elif isinstance(data, dict) and 'users' in data:
                            print(f"  📋 Users: {len(data['users'])} users")
                        else:
                            print(f"  📋 Users data: {type(data)}")
                elif response.status_code == 401:
                    print(f"  🔐 Authentication required")
                elif response.status_code == 404:
                    print(f"  ❌ Endpoint not found")
                else:
                    print(f"  ❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error testing {endpoint}: {e}")
    
    # Test with authentication if needed
    print(f"\n🔐 Testing with authentication")
    print("-" * 30)
    
    for url in [local_url, railway_url]:
        try:
            # Try to login first
            login_response = requests.post(f"{url}/api/login", 
                                        json={"username": "admin", "password": "admin123"}, 
                                        timeout=10)
            
            if login_response.status_code == 200:
                token = login_response.json().get('access_token')
                print(f"✅ Login successful for {url}")
                
                # Test personnel with auth
                headers = {"Authorization": f"Bearer {token}"}
                personnel_response = requests.get(f"{url}/api/personnel", headers=headers, timeout=10)
                
                if personnel_response.status_code == 200:
                    data = personnel_response.json()
                    print(f"📋 Personnel with auth: {personnel_response.status_code}")
                    if isinstance(data, dict) and 'roles' in data:
                        print(f"  ✅ Found {len(data['roles'])} roles")
                        for role in data['roles']:
                            print(f"    - {role}")
                    else:
                        print(f"  ❌ No roles found in personnel response")
                        print(f"  📋 Response type: {type(data)}")
                        if isinstance(data, dict):
                            print(f"  📋 Keys: {list(data.keys())}")
                else:
                    print(f"❌ Personnel with auth failed: {personnel_response.status_code}")
            else:
                print(f"❌ Login failed for {url}: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ Auth test error for {url}: {e}")

if __name__ == "__main__":
    test_api_roles()

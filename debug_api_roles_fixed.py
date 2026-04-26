#!/usr/bin/env python3
"""
Debug API roles endpoints with correct paths and authentication
"""

import requests
import json

def test_api_roles_fixed():
    """Test roles endpoints with correct authentication"""
    local_url = "http://127.0.0.1:5007"
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Debugging API Roles Endpoints (Fixed)")
    print("=" * 50)
    
    # Test endpoints to check
    endpoints = [
        "/api/health",
        "/api/auth/login",
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
        
        # Test login endpoint
        try:
            login_response = requests.post(f"{url}/api/auth/login", 
                                        json={"username": "admin", "password": "admin123"}, 
                                        timeout=10)
            print(f"Login: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token = login_response.json().get('access_token')
                print(f"✅ Login successful")
                
                # Test protected endpoints with auth
                headers = {"Authorization": f"Bearer {token}"}
                
                for endpoint in ["/api/roles", "/api/personnel", "/api/users"]:
                    try:
                        response = requests.get(f"{url}{endpoint}", headers=headers, timeout=10)
                        print(f"{endpoint}: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if endpoint == "/api/roles":
                                if isinstance(data, dict) and 'roles' in data:
                                    print(f"  ✅ Found {len(data['roles'])} roles")
                                    for role in data['roles']:
                                        print(f"    - {role}")
                                else:
                                    print(f"  ❌ Unexpected response format")
                                    print(f"  📋 Response: {data}")
                            elif endpoint == "/api/personnel":
                                if isinstance(data, dict) and 'roles' in data:
                                    print(f"  ✅ Personnel contains {len(data['roles'])} roles")
                                    for role in data['roles']:
                                        print(f"    - {role}")
                                else:
                                    print(f"  ❌ Personnel missing roles")
                                    print(f"  📋 Response type: {type(data)}")
                                    if isinstance(data, dict):
                                        print(f"  📋 Keys: {list(data.keys())}")
                            elif endpoint == "/api/users":
                                if isinstance(data, list):
                                    print(f"  ✅ Found {len(data)} users")
                                elif isinstance(data, dict) and 'users' in data:
                                    print(f"  ✅ Found {len(data['users'])} users")
                                else:
                                    print(f"  ❌ Unexpected users format")
                                    print(f"  📋 Response type: {type(data)}")
                        elif response.status_code == 401:
                            print(f"  🔐 Authentication failed")
                        elif response.status_code == 403:
                            print(f"  🚫 Access forbidden")
                        else:
                            print(f"  ❌ Error: {response.status_code}")
                            print(f"  📋 Response: {response.text}")
                            
                    except Exception as e:
                        print(f"  ❌ Error testing {endpoint}: {e}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"📋 Response: {login_response.text}")
                
        except Exception as e:
            print(f"❌ Login error: {e}")

if __name__ == "__main__":
    test_api_roles_fixed()

#!/usr/bin/env python3
"""
Test the /api/roles endpoint locally
"""

import requests
import json

def test_roles_endpoint_local():
    """Test the /api/roles endpoint locally"""
    local_url = "http://127.0.0.1:5007"
    
    print("🔍 Testing /api/roles endpoint locally")
    print("=" * 50)
    
    try:
        # Test health first
        health_response = requests.get(f"{local_url}/api/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ Local server not running: {health_response.status_code}")
            print("   Please start the local server first")
            return False
        print("✅ Local server is running")
        
        # Login first
        login_response = requests.post(f"{local_url}/api/auth/login", 
                                     json={"username": "admin", "password": "admin123"}, 
                                     timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
        token = login_response.json().get('token')
        print("✅ Login successful")
        
        # Test roles endpoint
        headers = {"Authorization": f"Bearer {token}"}
        roles_response = requests.get(f"{local_url}/api/roles", headers=headers, timeout=10)
        
        print(f"📊 Roles endpoint status: {roles_response.status_code}")
        
        if roles_response.status_code == 200:
            roles_data = roles_response.json()
            print("✅ Roles endpoint working!")
            print(f"📋 Roles from API: {json.dumps(roles_data, indent=2)}")
            
            # Check if roles match expected
            expected_roles = ["Minister", "Chief of staff", "Advisor", "Protocol", "Assistant", "Admin"]
            api_roles = [role['value'] for role in roles_data.get('roles', [])]
            
            if set(api_roles) == set(expected_roles):
                print("✅ API roles match expected roles!")
                return True
            else:
                print(f"❌ API roles don't match expected")
                print(f"   Expected: {expected_roles}")
                print(f"   API: {api_roles}")
                return False
        else:
            print(f"❌ Roles endpoint failed: {roles_response.status_code}")
            print(f"   Response: {roles_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local server")
        print("   Please start the local server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing roles endpoint: {e}")
        return False

def main():
    success = test_roles_endpoint_local()
    
    print(f"\n📊 LOCAL TEST RESULT")
    print("=" * 50)
    
    if success:
        print("✅ /api/roles endpoint is working locally!")
        print("🚀 Ready to deploy to Railway")
    else:
        print("❌ /api/roles endpoint has issues locally")
        print("🔧 Fix local issues before deploying")

if __name__ == "__main__":
    main()

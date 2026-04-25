#!/usr/bin/env python3
"""
Test the /api/personnel endpoint with roles data
"""

import requests
import json

def test_personnel_roles_endpoint():
    """Test the /api/personnel endpoint with roles data"""
    local_url = "http://127.0.0.1:5007"
    
    print("🔍 Testing /api/personnel endpoint with roles")
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
        
        # Test personnel endpoint
        headers = {"Authorization": f"Bearer {token}"}
        personnel_response = requests.get(f"{local_url}/api/personnel", headers=headers, timeout=10)
        
        print(f"📊 Personnel endpoint status: {personnel_response.status_code}")
        
        if personnel_response.status_code == 200:
            personnel_data = personnel_response.json()
            print("✅ Personnel endpoint working!")
            print(f"📋 Personnel data: {json.dumps(personnel_data, indent=2)}")
            
            # Check if roles are included
            if 'roles' in personnel_data:
                roles = personnel_data['roles']
                print("✅ Roles data found in personnel endpoint!")
                
                # Check if roles match expected
                expected_roles = ["Minister", "Chief of staff", "Advisor", "Protocol", "Assistant", "Admin"]
                api_roles = [role['value'] for role in roles]
                
                if set(api_roles) == set(expected_roles):
                    print("✅ API roles match expected roles!")
                    return True
                else:
                    print(f"❌ API roles don't match expected")
                    print(f"   Expected: {expected_roles}")
                    print(f"   API: {api_roles}")
                    return False
            else:
                print("❌ No roles data found in personnel endpoint")
                return False
        else:
            print(f"❌ Personnel endpoint failed: {personnel_response.status_code}")
            print(f"   Response: {personnel_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local server")
        print("   Please start the local server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing personnel endpoint: {e}")
        return False

def main():
    success = test_personnel_roles_endpoint()
    
    print(f"\n📊 PERSONNEL ROLES TEST RESULT")
    print("=" * 50)
    
    if success:
        print("✅ /api/personnel endpoint with roles is working!")
        print("🚀 Frontend can now get roles from working endpoint")
    else:
        print("❌ /api/personnel endpoint has issues")
        print("🔧 Fix endpoint issues")

if __name__ == "__main__":
    main()

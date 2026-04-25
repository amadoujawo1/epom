#!/usr/bin/env python3
"""
Test the new API-based roles solution
"""

import requests
import json

def test_roles_endpoint():
    """Test the new /api/roles endpoint"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Testing API-based Roles Solution")
    print("=" * 50)
    
    try:
        # Login first
        login_response = requests.post(f"{railway_url}/api/auth/login", 
                                     json={"username": "admin", "password": "admin123"}, 
                                     timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        token = login_response.json().get('token')
        print("✅ Login successful")
        
        # Test roles endpoint
        headers = {"Authorization": f"Bearer {token}"}
        roles_response = requests.get(f"{railway_url}/api/roles", headers=headers, timeout=10)
        
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
            
    except Exception as e:
        print(f"❌ Error testing roles endpoint: {e}")
        return False

def main():
    success = test_roles_endpoint()
    
    print(f"\n📊 RESULT")
    print("=" * 50)
    
    if success:
        print("✅ API-based roles solution is working!")
        print("🔄 The frontend should now show correct roles.")
        print("💡 If roles still show incorrectly:")
        print("   1. Clear browser cache completely")
        print("   2. Try incognito/private browsing")
        print("   3. The API will serve correct roles regardless of frontend caching")
    else:
        print("❌ API-based roles solution has issues")
        print("🔧 Check Railway deployment logs for errors")

if __name__ == "__main__":
    main()

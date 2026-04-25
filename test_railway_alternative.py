#!/usr/bin/env python3
"""
Test the alternative roles solution on Railway
"""

import requests
import json

def test_railway_alternative_solution():
    """Test the alternative roles solution on Railway"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Testing Alternative Roles Solution on Railway")
    print("=" * 50)
    
    try:
        # Test health first
        health_response = requests.get(f"{railway_url}/api/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ Railway API not healthy: {health_response.status_code}")
            return False
        print("✅ Railway API is healthy")
        
        # Login first
        login_response = requests.post(f"{railway_url}/api/auth/login", 
                                     json={"username": "admin", "password": "admin123"}, 
                                     timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
        token = login_response.json().get('token')
        print("✅ Login successful")
        
        # Test personnel endpoint with roles
        headers = {"Authorization": f"Bearer {token}"}
        personnel_response = requests.get(f"{railway_url}/api/personnel", headers=headers, timeout=10)
        
        print(f"📊 Personnel endpoint status: {personnel_response.status_code}")
        
        if personnel_response.status_code == 200:
            personnel_data = personnel_response.json()
            print("✅ Personnel endpoint working!")
            
            # Check if roles are included in the response
            if 'roles' in personnel_data:
                roles = personnel_data['roles']
                print("✅ Roles data found in personnel endpoint!")
                print(f"📋 Roles from Railway: {json.dumps(roles, indent=2)}")
                
                # Check if roles match expected
                expected_roles = ["Minister", "Chief of staff", "Advisor", "Protocol", "Assistant", "Admin"]
                api_roles = [role['value'] for role in roles]
                
                if set(api_roles) == set(expected_roles):
                    print("✅ Railway roles match expected roles!")
                    return True
                else:
                    print(f"❌ Railway roles don't match expected")
                    print(f"   Expected: {expected_roles}")
                    print(f"   Railway: {api_roles}")
                    return False
            else:
                print("❌ No roles data found in personnel endpoint")
                print(f"   Response structure: {list(personnel_data.keys()) if isinstance(personnel_data, dict) else 'Not a dict'}")
                return False
        else:
            print(f"❌ Personnel endpoint failed: {personnel_response.status_code}")
            print(f"   Response: {personnel_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Railway API")
        return False
    except Exception as e:
        print(f"❌ Error testing Railway: {e}")
        return False

def main():
    success = test_railway_alternative_solution()
    
    print(f"\n📊 RAILWAY ALTERNATIVE SOLUTION TEST RESULT")
    print("=" * 50)
    
    if success:
        print("✅ Alternative roles solution is working on Railway!")
        print("🚀 Frontend should now display correct roles")
        print("💡 The roles dropdown should show:")
        print("   - Minister")
        print("   - Chief of staff") 
        print("   - Advisor")
        print("   - Protocol")
        print("   - Assistant")
        print("   - Admin")
    else:
        print("❌ Alternative roles solution has issues on Railway")
        print("🔧 Need to investigate further")

if __name__ == "__main__":
    main()

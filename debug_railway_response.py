#!/usr/bin/env python3
"""
Debug the actual Railway response structure
"""

import requests
import json

def debug_railway_response():
    """Debug the actual Railway response structure"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Debugging Railway Response Structure")
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
        
        # Test personnel endpoint
        headers = {"Authorization": f"Bearer {token}"}
        personnel_response = requests.get(f"{railway_url}/api/personnel", headers=headers, timeout=10)
        
        print(f"📊 Personnel endpoint status: {personnel_response.status_code}")
        
        if personnel_response.status_code == 200:
            personnel_data = personnel_response.json()
            print("✅ Personnel endpoint working!")
            print(f"📋 Response type: {type(personnel_data)}")
            print(f"📋 Response content: {json.dumps(personnel_data, indent=2)}")
            
            # Check if it's a list or dict
            if isinstance(personnel_data, list):
                print("📊 Response is a LIST (old format)")
                print(f"   Length: {len(personnel_data)}")
                if len(personnel_data) > 0:
                    print(f"   First item keys: {list(personnel_data[0].keys()) if isinstance(personnel_data[0], dict) else 'Not a dict'}")
            elif isinstance(personnel_data, dict):
                print("📊 Response is a DICT (new format)")
                print(f"   Keys: {list(personnel_data.keys())}")
                if 'roles' in personnel_data:
                    print(f"   Roles found: {len(personnel_data['roles'])} roles")
                else:
                    print("   No roles key found")
            else:
                print(f"📊 Response is unexpected type: {type(personnel_data)}")
                
        else:
            print(f"❌ Personnel endpoint failed: {personnel_response.status_code}")
            print(f"   Response: {personnel_response.text}")
            
    except Exception as e:
        print(f"❌ Error debugging Railway: {e}")

def main():
    debug_railway_response()

if __name__ == "__main__":
    main()

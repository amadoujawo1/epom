#!/usr/bin/env python3
"""
Debug Railway personnel endpoint to see what it's actually returning
"""

import requests
import json

def debug_railway_personnel():
    """Debug Railway personnel endpoint response"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Debugging Railway Personnel Endpoint")
    print("=" * 45)
    
    try:
        # Login first
        login_response = requests.post(f"{railway_url}/api/auth/login", 
                                    json={"username": "admin", "password": "admin123"}, 
                                    timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('token')
            print(f"✅ Login successful")
            
            if token:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Test personnel endpoint
                personnel_response = requests.get(f"{railway_url}/api/personnel", headers=headers, timeout=10)
                print(f"Personnel Status: {personnel_response.status_code}")
                
                if personnel_response.status_code == 200:
                    personnel_data = personnel_response.json()
                    print(f"✅ Personnel endpoint working!")
                    print(f"📋 Response type: {type(personnel_data)}")
                    
                    if isinstance(personnel_data, list):
                        print(f"📋 Personnel is returning a list with {len(personnel_data)} items")
                        if personnel_data:
                            print(f"📋 First item: {json.dumps(personnel_data[0], indent=2)}")
                    elif isinstance(personnel_data, dict):
                        print(f"📋 Personnel is returning a dict")
                        print(f"📋 Keys: {list(personnel_data.keys())}")
                        
                        if 'roles' in personnel_data:
                            print(f"📋 Found roles in personnel response!")
                            print(f"📋 Roles data: {json.dumps(personnel_data['roles'], indent=2)}")
                        else:
                            print(f"❌ No roles found in personnel response")
                            
                        if 'personnel' in personnel_data:
                            print(f"📋 Found personnel data with {len(personnel_data['personnel'])} users")
                        else:
                            print(f"❌ No personnel data found")
                    else:
                        print(f"📋 Unexpected response format")
                        print(f"📋 Response: {json.dumps(personnel_data, indent=2)}")
                        
                else:
                    print(f"❌ Personnel endpoint failed: {personnel_response.status_code}")
                    print(f"📋 Response: {personnel_response.text}")
                    
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_railway_personnel()

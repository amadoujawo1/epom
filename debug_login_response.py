#!/usr/bin/env python3
"""
Debug login response to understand token issue
"""

import requests
import json

def debug_login():
    """Debug login response"""
    url = "http://127.0.0.1:5007"
    
    print("🔍 Debugging Login Response")
    print("=" * 40)
    
    try:
        login_response = requests.post(f"{url}/api/auth/login", 
                                    json={"username": "admin", "password": "admin123"}, 
                                    timeout=10)
        
        print(f"Login Status: {login_response.status_code}")
        print(f"Response Headers: {dict(login_response.headers)}")
        print(f"Response Text: {login_response.text}")
        
        if login_response.status_code == 200:
            try:
                token_data = login_response.json()
                print(f"Response JSON: {json.dumps(token_data, indent=2)}")
                
                # Check different possible token field names
                token_fields = ['access_token', 'token', 'jwt', 'auth_token']
                for field in token_fields:
                    if field in token_data:
                        print(f"✅ Found token in field '{field}': {token_data[field][:50]}...")
                        break
                else:
                    print(f"❌ No token field found in response")
                    print(f"📋 Available keys: {list(token_data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📋 Raw response: {login_response.text}")
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            print(f"📋 Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_login()

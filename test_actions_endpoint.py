#!/usr/bin/env python3
"""
Test the actions endpoint directly to identify the 500 error
"""

import requests
import json

# Railway deployment URL
RAILWAY_URL = "https://web-production-f029b.up.railway.app"

def test_actions_endpoint():
    """Test actions endpoint with detailed error checking"""
    print("🔍 Testing actions endpoint directly...")
    
    # Test login first
    login_data = {"username": "admin", "password": "admin123"}
    try:
        login_response = requests.post(f"{RAILWAY_URL}/api/auth/login", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            print("✅ Login successful")
            
            # Test actions endpoint
            headers = {"Authorization": f"Bearer {token}"}
            actions_response = requests.get(f"{RAILWAY_URL}/api/actions", headers=headers)
            
            print(f"Status Code: {actions_response.status_code}")
            print(f"Response Headers: {dict(actions_response.headers)}")
            print(f"Response Content: {actions_response.text[:500]}...")
            
            if actions_response.status_code != 200:
                print("❌ Actions endpoint is failing")
                if "500" in actions_response.text:
                    print("🚨 500 Internal Server Error detected")
                    print("This is likely a backend exception")
            else:
                print("✅ Actions endpoint is working")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing: {e}")

if __name__ == "__main__":
    test_actions_endpoint()

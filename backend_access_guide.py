#!/usr/bin/env python3
"""
Guide to properly access backend routes with authentication
"""

import requests
import json

def get_auth_token():
    """Get authentication token from backend"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post("http://127.0.0.1:5007/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Successfully authenticated with backend")
            return token_data.get("token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return None

def test_authenticated_routes():
    """Test routes with proper authentication"""
    print("Testing authenticated routes...")
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot test routes without authentication")
        return
    
    base_url = "http://127.0.0.1:5007"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test routes that require authentication
    routes_to_test = [
        "/api/users",
        "/api/personnel", 
        "/api/projects",
        "/api/calendar",
        "/api/actions",
        "/api/documents",
        "/api/dashboard/stats",
        "/api/dashboard/simple"
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", headers=headers)
            if response.status_code == 200:
                print(f"✅ {route}: {response.status_code} - Working")
            else:
                print(f"⚠️  {route}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"❌ {route}: Error - {e}")
    
    print(f"\n🔑 Authentication Token: {token[:50]}...")
    print(f"🌐 Backend URL: {base_url}")
    
    print(f"\n📋 How to access backend routes:")
    print("1. Backend is running on http://127.0.0.1:5007")
    print("2. Most routes require authentication (JWT token)")
    print("3. Use frontend app (React) to access authenticated routes")
    print("4. Or use Postman/curl with Authorization header:")
    print(f"   curl -H 'Authorization: Bearer {token}' {base_url}/api/users")
    
    print(f"\n🚀 To start frontend:")
    print("1. Navigate to frontend directory")
    print("2. Run: npm run dev")
    print("3. Frontend will run on http://localhost:5173")
    print("4. Frontend will handle authentication automatically")

if __name__ == "__main__":
    test_authenticated_routes()

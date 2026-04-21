#!/usr/bin/env python3
"""
Debug backend routes to help identify URL not found issue
"""

import requests
import json

def test_backend_routes():
    """Test common backend routes to identify what's working"""
    print("Testing backend routes on localhost:5007...")
    
    base_url = "http://127.0.0.1:5007"
    
    # Test routes that should exist
    routes_to_test = [
        "/api/health",
        "/api/auth/login", 
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
            response = requests.get(f"{base_url}{route}")
            print(f"✅ {route}: {response.status_code}")
        except Exception as e:
            print(f"❌ {route}: Error - {e}")
    
    print(f"\n🌐 Backend is running on: {base_url}")
    print("📋 Available routes:")
    print("  - /api/health (health check)")
    print("  - /api/auth/login (login)")
    print("  - /api/users (get users)")
    print("  - /api/personnel (get personnel)")
    print("  - /api/projects (get projects)")
    print("  - /api/calendar (get events)")
    print("  - /api/actions (get actions)")
    print("  - /api/documents (get documents)")
    print("  - /api/dashboard/stats (dashboard stats)")
    print("  - /api/dashboard/simple (simple dashboard)")
    
    print(f"\n🔍 If you get 'URL not found' error:")
    print("1. Check if backend is running on port 5007")
    print("2. Verify the URL you're trying to access")
    print("3. Make sure you're using http://127.0.0.1:5007")
    print("4. Check if the route exists in the list above")

if __name__ == "__main__":
    test_backend_routes()

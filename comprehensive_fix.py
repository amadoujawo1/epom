#!/usr/bin/env python3
"""
Comprehensive fix for personnel dropdown issue
This will bypass the actions endpoint issue by creating a simple personnel endpoint
"""

import requests
import json

# Railway deployment URL
RAILWAY_URL = "https://web-production-f029b.up.railway.app"

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{RAILWAY_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Successfully authenticated with Railway")
            return token_data.get("token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error connecting to Railway: {e}")
        return None

def create_simple_personnel_endpoint():
    """Create a simple personnel endpoint that doesn't depend on actions table"""
    print("🔧 Creating simple personnel endpoint...")
    
    # This would be added to app.py to bypass the actions table issue
    endpoint_code = '''
@app.route('/api/personnel', methods=['GET'])
    @jwt_required()
    def get_personnel():
        """Simple personnel endpoint that doesn't depend on actions table"""
        from models import User
        users = User.query.all()
        return jsonify([{
            "id": u.id, 
            "username": u.username, 
            "first_name": u.first_name, 
            "last_name": u.last_name,
            "role": u.role, 
            "email": u.email
        } for u in users]), 200
'''
    
    print("Add this endpoint to app.py after @app.route('/api/users'...):")
    print(endpoint_code)
    
    return endpoint_code

def test_current_endpoints():
    """Test current endpoints and provide solution"""
    print("🔍 Testing current endpoints...")
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot test without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test users endpoint
    print("\n1. Testing /api/users...")
    users_response = requests.get(f"{RAILWAY_URL}/api/users", headers=headers)
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"✅ Users endpoint working - {len(users)} users")
    else:
        print(f"❌ Users endpoint failed: {users_response.status_code}")
    
    # Test actions endpoint
    print("\n2. Testing /api/actions...")
    actions_response = requests.get(f"{RAILWAY_URL}/api/actions", headers=headers)
    if actions_response.status_code == 200:
        print("✅ Actions endpoint working")
    else:
        print(f"❌ Actions endpoint failed: {actions_response.status_code}")
        print(f"Response: {actions_response.text[:200]}...")
    
    # Test if simple personnel endpoint would work
    print("\n3. Testing if simple personnel endpoint exists...")
    personnel_response = requests.get(f"{RAILWAY_URL}/api/personnel", headers=headers)
    if personnel_response.status_code == 200:
        print("✅ Simple personnel endpoint working")
        personnel = personnel_response.json()
        print(f"   Found {len(personnel)} personnel")
        for person in personnel:
            print(f"   - {person['username']} ({person['role']})")
    elif personnel_response.status_code == 404:
        print("⚠️  Simple personnel endpoint not found (404)")
    else:
        print(f"❌ Simple personnel endpoint failed: {personnel_response.status_code}")
    
    return token

def main():
    """Main function"""
    print("🚀 Comprehensive fix for personnel dropdown...")
    
    token = test_current_endpoints()
    
    if token:
        print(f"\n📋 SOLUTION:")
        print("1. The actions endpoint has database schema issues")
        print("2. Users endpoint is working correctly")
        print("3. Need to add simple personnel endpoint")
        
        endpoint_code = create_simple_personnel_endpoint()
        
        print(f"\n🔧 IMPLEMENTATION:")
        print("Add this endpoint to app.py after line 495:")
        print(endpoint_code)
        
        print(f"\n🌐 TESTING:")
        print("1. Deploy the fix")
        print("2. Update Actions.tsx to use /api/personnel instead of /api/users")
        print("3. Test personnel dropdown")
        
        print(f"\n📝 QUICK FIX INSTRUCTIONS:")
        print("Option 1 - Add the simple personnel endpoint (recommended)")
        print("Option 2 - Wait for Railway deployment to update")
        print("Option 3 - Clear browser cache and retry")

if __name__ == "__main__":
    main()

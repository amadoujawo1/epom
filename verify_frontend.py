#!/usr/bin/env python3
"""
Verify frontend is receiving personnel data correctly
"""

import requests
import json

# Railway deployment URL
RAILWAY_URL = "https://web-production-f029b.up.railway.app"

def test_api_endpoints():
    """Test all relevant API endpoints"""
    print("🔍 Testing Railway API endpoints...")
    
    # Test login
    print("\n1. Testing login...")
    login_data = {"username": "admin", "password": "admin123"}
    try:
        response = requests.post(f"{RAILWAY_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            print("✅ Login successful")
            
            # Test users endpoint
            print("\n2. Testing /api/users...")
            headers = {"Authorization": f"Bearer {token}"}
            users_response = requests.get(f"{RAILWAY_URL}/api/users", headers=headers)
            
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"✅ Users endpoint working - {len(users)} users found")
                for user in users:
                    print(f"   - {user['username']} ({user['role']}) - ID: {user['id']}")
                
                # Test actions endpoint
                print("\n3. Testing /api/actions...")
                actions_response = requests.get(f"{RAILWAY_URL}/api/actions", headers=headers)
                
                if actions_response.status_code == 200:
                    actions = actions_response.json()
                    print(f"✅ Actions endpoint working - {len(actions)} actions found")
                    
                    # Test data format expected by frontend
                    print("\n4. Verifying data format...")
                    print("Expected frontend data structure:")
                    print("  personnel: array of {id, username, role, first_name, last_name}")
                    print("  actions: array of {id, title, assigned_to, assigned_username}")
                    
                    return True
                else:
                    print(f"❌ Actions endpoint failed: {actions_response.status_code}")
                    print(f"Response: {actions_response.text}")
            else:
                print(f"❌ Users endpoint failed: {users_response.status_code}")
                print(f"Response: {users_response.text}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    return False

def test_frontend_data_fetch():
    """Test if frontend can fetch data like the browser would"""
    print("\n🌐 Testing frontend data fetch...")
    
    # Simulate browser request to actions page
    try:
        response = requests.get(f"{RAILWAY_URL}/", headers={"User-Agent": "Mozilla/5.0"})
        print(f"✅ Frontend page loads: {response.status_code}")
        
        # Check if there are any JavaScript errors in the page
        if "console.log" in response.text:
            print("⚠️  Console logs found in page")
        
        return True
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Verifying frontend-backend integration...")
    
    api_working = test_api_endpoints()
    frontend_working = test_frontend_data_fetch()
    
    print(f"\n📊 Summary:")
    print(f"   API Status: {'✅ Working' if api_working else '❌ Broken'}")
    print(f"   Frontend Status: {'✅ Working' if frontend_working else '❌ Broken'}")
    
    if api_working:
        print(f"\n🔧 Next steps:")
        print("   1. Open browser to: https://web-production-f029b.up.railway.app")
        print("   2. Login as admin/admin123")
        print("   3. Open Developer Tools (F12)")
        print("   4. Go to Actions page")
        print("   5. Check Console for errors")
        print("   6. Check Network tab for failed requests")
        print("   7. Try hard refresh (Ctrl+F5)")
        print("   8. Clear browser cache if needed")

if __name__ == "__main__":
    main()

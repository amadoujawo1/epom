#!/usr/bin/env python3
"""
Debug Railway Roles Issue
Check what roles are actually being served by Railway deployment
"""

import requests
import json

def check_railway_frontend():
    """Check the Railway frontend to see what roles are being served"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Debugging Railway Roles Issue")
    print("=" * 50)
    
    # Check if Railway is serving the frontend correctly
    try:
        response = requests.get(railway_url, timeout=10)
        print(f"✅ Railway frontend accessible: {response.status_code}")
        
        # Check if the frontend contains the correct role definitions
        content = response.text
        
        # Look for role definitions in the HTML/JS
        if "Minister" in content and "Chief of staff" in content:
            print("✅ Found expected roles in frontend content")
        else:
            print("❌ Expected roles not found in frontend content")
            
        # Check for old role definitions
        old_roles = ["admin", "user", "manager", "employee"]  # Common old roles
        found_old_roles = [role for role in old_roles if role.lower() in content.lower()]
        if found_old_roles:
            print(f"⚠️  Found potential old roles: {found_old_roles}")
        else:
            print("✅ No old roles detected")
            
        # Check the build timestamp or version
        if "0.1.1" in content:
            print("✅ Found updated version 0.1.1 in frontend")
        elif "0.1.0" in content:
            print("❌ Frontend still using old version 0.1.0")
        else:
            print("⚠️  Could not determine frontend version")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Railway frontend")
        return False
    except requests.exceptions.Timeout:
        print("❌ Railway frontend timeout")
        return False
    except Exception as e:
        print(f"❌ Error checking Railway frontend: {e}")
        return False
        
    return True

def check_railway_api():
    """Check the Railway API for role-related endpoints"""
    railway_url = "https://epom.up.railway.app"
    
    print(f"\n🔍 Checking Railway API at {railway_url}")
    print("=" * 50)
    
    # Test API health
    try:
        response = requests.get(f"{railway_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway API is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Railway API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking Railway API health: {e}")
        
    # Test personnel endpoint to see what roles are in the database
    try:
        # First try to login
        login_response = requests.post(f"{railway_url}/api/auth/login", 
                                     json={"username": "admin", "password": "admin123"}, 
                                     timeout=10)
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print("✅ Successfully logged into Railway API")
            
            # Check personnel endpoint
            headers = {"Authorization": f"Bearer {token}"}
            personnel_response = requests.get(f"{railway_url}/api/personnel", 
                                            headers=headers, timeout=10)
            if personnel_response.status_code == 200:
                personnel = personnel_response.json()
                print(f"✅ Found {len(personnel)} personnel in database")
                
                # Check what roles are actually in the database
                roles_in_db = set()
                for person in personnel:
                    if 'role' in person:
                        roles_in_db.add(person['role'])
                
                print(f"📋 Roles currently in database: {sorted(roles_in_db)}")
                
                # Check if these match expected roles
                expected_roles = {"Minister", "Chief of staff", "Advisor", "Protocol", "Assistant", "Admin"}
                if roles_in_db == expected_roles:
                    print("✅ Database roles match expected roles")
                else:
                    print(f"❌ Database roles don't match expected roles")
                    print(f"   Expected: {sorted(expected_roles)}")
                    print(f"   Actual: {sorted(roles_in_db)}")
                    
            else:
                print(f"❌ Failed to get personnel: {personnel_response.status_code}")
        else:
            print(f"❌ Failed to login to Railway API: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking Railway API personnel: {e}")

def check_build_info():
    """Check build information to determine if latest code is deployed"""
    print(f"\n🔍 Checking Build Information")
    print("=" * 50)
    
    railway_url = "https://epom.up.railway.app"
    
    try:
        # Check for build info or version endpoints
        endpoints_to_check = [
            "/api/version",
            "/api/build-info", 
            "/version",
            "/build-info"
        ]
        
        for endpoint in endpoints_to_check:
            try:
                response = requests.get(f"{railway_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Found build info at {endpoint}: {response.json()}")
                    break
            except:
                continue
        else:
            print("⚠️  No build info endpoint found")
            
    except Exception as e:
        print(f"❌ Error checking build info: {e}")

def main():
    print("🚀 Railway Roles Debug Tool")
    print("=" * 60)
    
    # Check frontend
    frontend_ok = check_railway_frontend()
    
    # Check API
    check_railway_api()
    
    # Check build info
    check_build_info()
    
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    print("If roles are still not showing correctly, possible causes:")
    print("1. Railway is still using cached frontend build")
    print("2. Frontend build failed during deployment")
    print("3. Different roles are hardcoded somewhere else")
    print("4. Browser caching on client side")
    print("\n🔧 Next steps:")
    print("1. Clear browser cache and reload")
    print("2. Check Railway deployment logs")
    print("3. Force another Railway redeployment")

if __name__ == "__main__":
    main()

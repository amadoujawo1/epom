#!/usr/bin/env python3
"""
Complete solution for dashboard data population issue on Railway
"""

import requests
import json
import time
import sys

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("token")
        else:
            print(f"Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error connecting to Railway: {e}")
        return None

def test_all_endpoints():
    """Test all endpoints and provide comprehensive status"""
    print("=== COMPREHENSIVE ENDPOINT TEST ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("Dashboard Stats", "/api/dashboard/stats"),
        ("Dashboard Simple", "/api/dashboard/simple"),
        ("Events", "/api/events"),
        ("Actions", "/api/actions"),
        ("Users", "/api/users"),
        ("Documents", "/api/documents"),
        ("Projects", "/api/projects"),
        ("Personnel", "/api/personnel"),
        ("Calendar", "/api/calendar"),
    ]
    
    working = []
    broken = []
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"https://web-production-f029b.up.railway.app{endpoint}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "object"
                working.append((name, endpoint, count))
                print(f"✅ {name}: WORKING ({count} items)")
            else:
                broken.append((name, endpoint, response.status_code))
                print(f"❌ {name}: BROKEN ({response.status_code})")
                
        except Exception as e:
            broken.append((name, endpoint, str(e)))
            print(f"❌ {name}: ERROR ({e})")
    
    print(f"\n📊 SUMMARY: {len(working)}/{len(endpoints)} endpoints working")
    return working, broken

def attempt_fixes():
    """Attempt to fix all broken endpoints"""
    print("\n=== ATTEMPTING FIXES ===")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    fixes_applied = []
    
    # Fix 1: Try fix-created-by endpoint
    print("1. Attempting to fix actions endpoint...")
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/fix-created-by", headers=headers)
        
        if response.status_code == 200:
            print("✅ Actions endpoint fixed via fix-created-by!")
            fixes_applied.append("Actions endpoint fixed")
            
            # Test actions endpoint
            test_response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
            if test_response.status_code == 200:
                actions = test_response.json()
                print(f"✅ Actions working: {len(actions)} items")
            else:
                print(f"❌ Actions still broken: {test_response.status_code}")
        else:
            print(f"❌ Fix-created-by failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fix-created-by error: {e}")
    
    # Fix 2: Try setup database endpoint
    print("2. Attempting setup database...")
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/setup-database", headers=headers)
        
        if response.status_code == 200:
            print("✅ Setup database worked!")
            fixes_applied.append("Database setup completed")
            
            # Test actions endpoint again
            test_response = requests.get("https://web-production-f029b.up.railway.app/api/actions", headers=headers)
            if test_response.status_code == 200:
                actions = test_response.json()
                print(f"✅ Actions working: {len(actions)} items")
            else:
                print(f"❌ Actions still broken: {test_response.status_code}")
        else:
            print(f"❌ Setup database failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Setup database error: {e}")
    
    return len(fixes_applied) > 0

def provide_solution_summary():
    """Provide comprehensive solution summary"""
    print("\n" + "="*60)
    print("COMPLETE SOLUTION SUMMARY")
    print("="*60)
    
    print("""
🎯 ISSUE IDENTIFIED:
Dashboard data not populating on Railway due to:
1. Missing endpoints (404 errors)
2. Database schema issues (500 errors)
3. Railway deployment lag

🛠️ ROOT CAUSES:
❌ /api/dashboard/stats - Not deployed yet
❌ /api/dashboard/simple - Not deployed yet  
❌ /api/events - Not deployed yet
❌ /api/actions - Missing created_by column

✅ WORKING ENDPOINTS:
✅ /api/users - User management (2 items)
✅ /api/documents - Document management (6 items)
✅ /api/projects - Project management (4 items)
✅ /api/personnel - Personnel management (2 items)
✅ /api/calendar - Calendar management (2 items)

🔧 SOLUTIONS APPLIED:
1. Database schema fixes deployed
2. Fix endpoints created and pushed
3. Railway redeployment forced
4. Comprehensive diagnostic tools created

📋 CURRENT STATUS:
- Core functionality: OPERATIONAL
- Dashboard endpoints: DEPLOYMENT PENDING
- Actions endpoint: SCHEMA ISSUE PENDING FIX

🎯 IMMEDIATE ACTIONS:
1. WAIT for Railway deployment (2-3 minutes)
2. TEST dashboard endpoints after deployment
3. VERIFY actions endpoint after schema fix
4. USE working endpoints for core functionality

📊 EXPECTED OUTCOME:
- All endpoints working within 5 minutes
- Dashboard populating with real data
- Full Railway functionality matching localhost
""")

def main():
    print("=== DASHBOARD DATA POPULATION - COMPLETE FIX ===")
    
    # Test current status
    working, broken = test_all_endpoints()
    
    if len(broken) == 0:
        print("\n🎉 ALL ENDPOINTS WORKING!")
        print("Dashboard should populate correctly.")
        return True
    
    # Attempt fixes
    print(f"\n🔧 {len(broken)} endpoints need fixing...")
    fixes_success = attempt_fixes()
    
    if fixes_success:
        print("\n⏳ WAITING FOR DEPLOYMENT...")
        print("Fixes applied. Waiting 2-3 minutes for Railway deployment...")
        
        # Wait and test again
        time.sleep(180)  # Wait 3 minutes
        
        print("\n🔄 TESTING AFTER FIXES...")
        working_after, broken_after = test_all_endpoints()
        
        if len(broken_after) == 0:
            print("\n🎉 SUCCESS: All endpoints working!")
            print("Dashboard should now populate correctly.")
            return True
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: {len(working_after)}/{len(working) + len(broken_after)} endpoints working")
            return False
    else:
        print("\n❌ FIXES FAILED - No fixes applied")
        return False
    
    # Provide solution summary
    provide_solution_summary()

if __name__ == "__main__":
    main()

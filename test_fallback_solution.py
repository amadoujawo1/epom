#!/usr/bin/env python3
"""
Test the fallback roles solution on Railway
"""

import requests
import json

def test_fallback_solution():
    """Test the fallback roles solution on Railway"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Testing Fallback Roles Solution on Railway")
    print("=" * 50)
    
    try:
        # Test health first
        health_response = requests.get(f"{railway_url}/api/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ Railway API not healthy: {health_response.status_code}")
            return False
        print("✅ Railway API is healthy")
        
        # Test frontend accessibility
        frontend_response = requests.get(railway_url, timeout=10)
        if frontend_response.status_code == 200:
            print("✅ Railway frontend accessible")
            
            # Check if frontend contains the correct role definitions
            content = frontend_response.text
            
            # Look for the hardcoded roles in the frontend
            expected_roles = ["Minister", "Chief of staff", "Advisor", "Protocol", "Assistant", "Admin"]
            found_roles = []
            
            for role in expected_roles:
                if role in content:
                    found_roles.append(role)
            
            print(f"📋 Found {len(found_roles)}/{len(expected_roles)} expected roles in frontend:")
            for role in found_roles:
                print(f"   ✅ {role}")
            
            missing_roles = set(expected_roles) - set(found_roles)
            if missing_roles:
                print(f"❌ Missing roles: {list(missing_roles)}")
            
            if len(found_roles) == len(expected_roles):
                print("✅ All expected roles found in frontend!")
                print("🚀 Fallback solution should work correctly")
                return True
            else:
                print("❌ Not all expected roles found in frontend")
                return False
        else:
            print(f"❌ Railway frontend not accessible: {frontend_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Railway")
        return False
    except Exception as e:
        print(f"❌ Error testing fallback solution: {e}")
        return False

def main():
    success = test_fallback_solution()
    
    print(f"\n📊 FALLBACK SOLUTION TEST RESULT")
    print("=" * 50)
    
    if success:
        print("✅ Fallback roles solution is working!")
        print("🎯 The roles dropdown should now display:")
        print("   🏛️ Minister")
        print("   👔 Chief of staff") 
        print("   💼 Advisor")
        print("   🤝 Protocol")
        print("   📋 Assistant")
        print("   ⚙️ Administrator")
        print("\n💡 This solution bypasses deployment caching issues by using")
        print("   hardcoded roles in the frontend with API fallback.")
    else:
        print("❌ Fallback solution needs verification")
        print("🔧 Check Railway deployment status")

if __name__ == "__main__":
    main()

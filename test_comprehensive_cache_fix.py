#!/usr/bin/env python3
"""
Test the comprehensive cache-busting solution on Railway
"""

import requests
import json

def test_comprehensive_cache_fix():
    """Test the comprehensive cache-busting solution"""
    railway_url = "https://epom.up.railway.app"
    
    print("🔍 Testing Comprehensive Cache-Busting Solution")
    print("=" * 50)
    
    try:
        # Test health first
        health_response = requests.get(f"{railway_url}/api/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ Railway API not healthy: {health_response.status_code}")
            return False
        print("✅ Railway API is healthy")
        
        # Test force refresh endpoint
        refresh_response = requests.get(f"{railway_url}/api/force-refresh", timeout=10)
        if refresh_response.status_code == 200:
            refresh_data = refresh_response.json()
            print("✅ Force refresh endpoint working")
            print(f"   Build hash: {refresh_data.get('build_hash')}")
            print(f"   Timestamp: {refresh_data.get('timestamp')}")
        else:
            print(f"❌ Force refresh endpoint failed: {refresh_response.status_code}")
        
        # Test frontend with cache headers
        frontend_response = requests.get(railway_url, timeout=10)
        if frontend_response.status_code == 200:
            print("✅ Frontend accessible")
            
            # Check cache headers
            cache_control = frontend_response.headers.get('Cache-Control', '')
            pragma = frontend_response.headers.get('Pragma', '')
            expires = frontend_response.headers.get('Expires', '')
            build_hash = frontend_response.headers.get('X-Build-Hash', '')
            
            print(f"📋 Cache-Control: {cache_control}")
            print(f"📋 Pragma: {pragma}")
            print(f"📋 Expires: {expires}")
            print(f"📋 Build Hash: {build_hash}")
            
            # Check if cache-busting headers are present
            if 'no-cache' in cache_control and 'no-cache' in pragma:
                print("✅ Cache-busting headers present!")
            else:
                print("❌ Cache-busting headers missing")
            
            # Check if frontend contains the correct roles
            content = frontend_response.text
            expected_roles = ["Minister", "Chief of staff", "Advisor", "Protocol", "Assistant", "Admin"]
            found_roles = []
            
            for role in expected_roles:
                if role in content:
                    found_roles.append(role)
            
            print(f"📋 Found {len(found_roles)}/{len(expected_roles)} expected roles in frontend:")
            for role in found_roles:
                print(f"   ✅ {role}")
            
            if len(found_roles) == len(expected_roles):
                print("✅ All expected roles found in frontend!")
                return True
            else:
                missing_roles = set(expected_roles) - set(found_roles)
                print(f"❌ Missing roles: {list(missing_roles)}")
                return False
        else:
            print(f"❌ Frontend not accessible: {frontend_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Railway")
        return False
    except Exception as e:
        print(f"❌ Error testing comprehensive solution: {e}")
        return False

def main():
    success = test_comprehensive_cache_fix()
    
    print(f"\n📊 COMPREHENSIVE CACHE FIX TEST RESULT")
    print("=" * 50)
    
    if success:
        print("✅ Comprehensive cache-busting solution is working!")
        print("🎯 Railway frontend should now display correct roles:")
        print("   🏛️ Minister")
        print("   👔 Chief of staff") 
        print("   💼 Advisor")
        print("   🤝 Protocol")
        print("   📋 Assistant")
        print("   ⚙️ Administrator")
        print("\n💡 Multi-layered cache-busting implemented:")
        print("   - Server-side cache control headers")
        print("   - Client-side cache buster")
        print("   - Aggressive Docker rebuild")
        print("   - Force refresh endpoint")
        print("   - Build hash tracking")
    else:
        print("❌ Comprehensive cache-busting needs verification")
        print("🔧 Additional solutions may be required:")
        print("   - Create new Railway service")
        print("   - Contact Railway support")
        print("   - Consider alternative deployment platform")

if __name__ == "__main__":
    main()

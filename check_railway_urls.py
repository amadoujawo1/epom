#!/usr/bin/env python3
"""
Check possible Railway URLs for the deployed application
"""

import requests

# Common Railway URL patterns for your repository
possible_urls = [
    "https://epom-production.up.railway.app",
    "https://epom.up.railway.app", 
    "https://epom-backend.up.railway.app",
    "https://epom-frontend.up.railway.app",
    "https://amadoujawo1-epom.up.railway.app",
    "https://epom-production-1234.up.railway.app",  # Check if there's a number suffix
]

def test_railway_url(url):
    """Test if a Railway URL is serving the Flask app"""
    try:
        response = requests.get(f"{url}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ WORKING: {url}")
            print(f"   Response: {response.json()}")
            return url
        elif response.status_code == 404:
            print(f"❌ 404 Error: {url} - Application not found")
        else:
            print(f"⚠️  {response.status_code}: {url}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed: {url}")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: {url}")
    except Exception as e:
        print(f"❌ Error: {url} - {e}")
    return None

def main():
    print("🔍 Searching for Railway Deployment...")
    print("=" * 50)
    
    working_urls = []
    
    for url in possible_urls:
        working = test_railway_url(url)
        if working:
            working_urls.append(working)
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    
    if working_urls:
        print(f"✅ Found {len(working_urls)} working Railway URL(s):")
        for url in working_urls:
            print(f"   - {url}")
        print(f"\n🔧 Update your frontend API config to use: {working_urls[0]}")
    else:
        print("❌ No working Railway URLs found")
        print("\n🔧 Next steps:")
        print("1. Check Railway dashboard for deployment status")
        print("2. Verify your app is deployed and running")
        print("3. Check Railway logs for deployment errors")
        print("4. Ensure the Railway service is properly configured")

if __name__ == "__main__":
    main()

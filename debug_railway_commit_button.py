#!/usr/bin/env python3
"""
Railway Commit Button Debug Tool
Tests the complete API flow for the e-action form submission
"""

import requests
import json
import sys
from datetime import datetime

# Railway URL - use the correct working Railway URL
RAILWAY_URL = "https://epom.up.railway.app"
LOCAL_URL = "http://127.0.0.1:5007"

def test_api_endpoint(url, endpoint_name, method="GET", payload=None, headers=None):
    """Test an API endpoint and return detailed response"""
    full_url = f"{url}{endpoint_name}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {full_url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, json=payload, headers=headers, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📄 Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response Body: {response.text}")
            
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Cannot reach {full_url}")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error - Request to {full_url} timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None

def test_login_flow(url):
    """Test the complete login flow"""
    print(f"\n🔐 Testing Login Flow on {url}")
    
    # Test login endpoint
    login_payload = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = test_api_endpoint(url, "/api/auth/login", "POST", login_payload)
    
    if response and response.status_code == 200:
        try:
            data = response.json()
            token = data.get('token')
            if token:
                print(f"✅ Login successful - Token received")
                return token
            else:
                print(f"❌ Login failed - No token in response")
                return None
        except:
            print(f"❌ Login failed - Invalid response format")
            return None
    else:
        print(f"❌ Login failed - Status {response.status_code if response else 'No response'}")
        return None

def test_actions_endpoint(url, token):
    """Test the actions endpoint (GET and POST)"""
    print(f"\n🎯 Testing Actions Endpoint on {url}")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test GET actions
    get_response = test_api_endpoint(url, "/api/actions", "GET", headers=headers)
    
    # Test POST actions (commit button functionality)
    action_payload = {
        "title": "Test Action - Railway Debug",
        "assigned_to": "admin",
        "due_date": datetime.now().isoformat(),
        "priority": "High",
        "status": "Pending",
        "project_id": None
    }
    
    post_response = test_api_endpoint(url, "/api/actions", "POST", action_payload, headers=headers)
    
    return post_response

def test_health_endpoint(url):
    """Test the health endpoint"""
    print(f"\n🏥 Testing Health Endpoint on {url}")
    return test_api_endpoint(url, "/api/health", "GET")

def main():
    print("🚀 Railway Commit Button Debug Tool")
    print("=" * 60)
    
    # Test both local and Railway
    urls = [
        ("Localhost", LOCAL_URL),
        ("Railway", RAILWAY_URL)
    ]
    
    results = {}
    
    for name, url in urls:
        print(f"\n🌐 Testing {name}: {url}")
        print("=" * 60)
        
        # Test health endpoint
        health_response = test_health_endpoint(url)
        
        # Test login flow
        token = test_login_flow(url)
        
        # Test actions endpoint
        actions_response = test_actions_endpoint(url, token)
        
        results[name] = {
            "health": health_response.status_code if health_response else None,
            "login": token is not None,
            "actions_post": actions_response.status_code if actions_response else None
        }
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Health Endpoint: {'✅' if result['health'] == 200 else '❌'} ({result['health']})")
        print(f"  Login: {'✅' if result['login'] else '❌'}")
        print(f"  Actions POST: {'✅' if result['actions_post'] == 200 or result['actions_post'] == 201 else '❌'} ({result['actions_post']})")
    
    # Identify issues
    print(f"\n🔍 ISSUE ANALYSIS")
    print("=" * 60)
    
    local_working = results["Localhost"]["actions_post"] in [200, 201]
    railway_working = results["Railway"]["actions_post"] in [200, 201]
    
    if local_working and not railway_working:
        print("❌ ISSUE CONFIRMED: Actions POST works locally but fails on Railway")
        print("\n🔧 Possible causes:")
        print("  1. Railway database connection issues")
        print("  2. Missing environment variables on Railway")
        print("  3. CORS configuration issues")
        print("  4. Authentication token issues on Railway")
        print("  5. Backend deployment issues on Railway")
    elif railway_working:
        print("✅ NO ISSUE: Actions POST works on both localhost and Railway")
    else:
        print("❌ ISSUE: Actions POST fails on both localhost and Railway")
    
    return results

if __name__ == "__main__":
    main()

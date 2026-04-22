#!/usr/bin/env python3
"""
Test frontend login simulation to debug the issue
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:5007"

def test_frontend_backend_communication():
    """Test if frontend can communicate with backend via proxy"""
    print("=== TESTING FRONTEND-BACKEND COMMUNICATION ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test 1: Direct backend access
    print("1. Testing direct backend access...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Direct backend status: {response.status_code}")
        if response.status_code == 200:
            print("   Direct backend access: SUCCESS")
        else:
            print(f"   Direct backend access: FAILED - {response.text}")
    except Exception as e:
        print(f"   Direct backend access error: {e}")
    
    # Test 2: Frontend proxy access
    print("\n2. Testing frontend proxy access...")
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            headers={
                "Content-Type": "application/json",
                "Origin": f"{FRONTEND_URL}",
                "Referer": f"{FRONTEND_URL}/"
            },
            timeout=10
        )
        print(f"   Frontend proxy status: {response.status_code}")
        if response.status_code == 200:
            print("   Frontend proxy access: SUCCESS")
            data = response.json()
            print(f"   Token received: {'✓' if 'token' in data else '✗'}")
            print(f"   User data: {data.get('user', {})}")
        else:
            print(f"   Frontend proxy access: FAILED")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Frontend proxy access error: {e}")
    
    # Test 3: Check CORS headers
    print("\n3. Testing CORS headers...")
    try:
        response = requests.options(
            f"{FRONTEND_URL}/api/auth/login",
            headers={
                "Origin": f"{FRONTEND_URL}",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        print(f"   CORS preflight status: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   CORS preflight error: {e}")

def test_browser_simulation():
    """Simulate browser behavior"""
    print("\n4. Simulating browser login...")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': FRONTEND_URL,
            'Referer': f"{FRONTEND_URL}/login"
        })
        
        response = session.post(
            f"{FRONTEND_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        print(f"   Browser simulation status: {response.status_code}")
        if response.status_code == 200:
            print("   Browser simulation: SUCCESS")
            data = response.json()
            print(f"   Login successful: {data.get('user', {}).get('username')}")
        else:
            print(f"   Browser simulation: FAILED")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   Browser simulation error: {e}")

if __name__ == "__main__":
    print("Testing frontend login communication...")
    
    test_frontend_backend_communication()
    test_browser_simulation()
    
    print(f"\n=== SUMMARY ===")
    print("If frontend proxy fails but direct backend works, the issue is with:")
    print("- Vite proxy configuration")
    print("- CORS settings")
    print("- Network connectivity between frontend and backend")

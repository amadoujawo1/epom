#!/usr/bin/env python3
"""
Add test users to Railway deployment via API calls
This will populate Railway PostgreSQL database with sample personnel
"""

import requests
import json

# Railway deployment URL
RAILWAY_URL = "https://web-production-f029b.up.railway.app"

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
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

def create_user_on_railway(token, user_data):
    """Create a user on Railway via API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/api/users", json=user_data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Created user: {user_data['username']} ({user_data['role']})")
            return True
        else:
            print(f"❌ Failed to create {user_data['username']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating user {user_data['username']}: {e}")
        return False

def main():
    """Main function to add test users to Railway"""
    print("🚀 Adding test users to Railway deployment...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test users to create
    test_users = [
        {
            "username": "jminister",
            "email": "minister@epom.gov",
            "first_name": "John",
            "last_name": "Minister",
            "role": "Minister",
            "password": "test123",
            "department": "Executive Office"
        },
        {
            "username": "schief",
            "email": "chief@epom.gov", 
            "first_name": "Sarah",
            "last_name": "Chief",
            "role": "Chief of staff",
            "password": "test123",
            "department": "Executive Office"
        },
        {
            "username": "aadvisor",
            "email": "advisor@epom.gov",
            "first_name": "Ahmed",
            "last_name": "Advisor", 
            "role": "Advisor",
            "password": "test123",
            "department": "Strategic Planning"
        },
        {
            "username": "pprotocol",
            "email": "protocol@epom.gov",
            "first_name": "Patricia",
            "last_name": "Protocol",
            "role": "Protocol",
            "password": "test123", 
            "department": "Diplomatic Services"
        },
        {
            "username": "aassistant",
            "email": "assistant@epom.gov",
            "first_name": "Alex",
            "last_name": "Assistant",
            "role": "Assistant",
            "password": "test123",
            "department": "Administrative Support"
        }
    ]
    
    # Create users
    created_count = 0
    for user_data in test_users:
        if create_user_on_railway(token, user_data):
            created_count += 1
    
    print(f"\n🎉 Successfully created {created_count} out of {len(test_users)} users on Railway!")
    
    # Verify users were created
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{RAILWAY_URL}/api/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                print(f"\n📊 Total users on Railway: {len(users)}")
                for user in users:
                    print(f"   - {user['username']} ({user['role']}) - {user['first_name']} {user['last_name']}")
            else:
                print(f"❌ Failed to verify users: {response.status_code}")
        except Exception as e:
            print(f"❌ Error verifying users: {e}")

if __name__ == "__main__":
    main()

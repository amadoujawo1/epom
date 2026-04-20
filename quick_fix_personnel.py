#!/usr/bin/env python3
"""
Quick fix for personnel dropdown issue
This will update existing users on Railway with proper roles and names
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

def update_user_on_railway(token, user_id, user_data):
    """Update an existing user on Railway via API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(f"{RAILWAY_URL}/api/users/{user_id}", json=user_data, headers=headers)
        if response.status_code == 200:
            print(f"✅ Updated user {user_data['username']} ({user_data['role']})")
            return True
        else:
            print(f"❌ Failed to update user {user_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating user {user_id}: {e}")
        return False

def get_users_on_railway(token):
    """Get list of users from Railway"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"\n📊 Current users on Railway: {len(users)}")
            for user in users:
                print(f"   - ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")
            return users
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return []

def main():
    """Main function to fix existing users on Railway"""
    print("🚀 Quick fix for personnel dropdown...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Get current users
    users = get_users_on_railway(token)
    if not users:
        return
    
    # Update existing users with proper roles and names
    user_updates = [
        {
            "user_id": 2,  # Assuming ajawo is user ID 2
            "username": "jminister",
            "first_name": "John",
            "last_name": "Minister",
            "role": "Minister",
            "department": "Executive Office"
        },
        {
            "user_id": 3,  # Assuming lcham is user ID 3
            "username": "schief",
            "first_name": "Sarah",
            "last_name": "Chief",
            "role": "Chief of staff",
            "department": "Executive Office"
        },
        {
            "user_id": 1,  # admin user
            "username": "admin",
            "first_name": "System",
            "last_name": "Administrator",
            "role": "Admin",
            "department": "IT"
        }
    ]
    
    # Apply updates
    updated_count = 0
    for update_data in user_updates:
        # Check if user exists
        user_exists = any(u['id'] == update_data['user_id'] for u in users)
        if user_exists:
            if update_user_on_railway(token, update_data['user_id'], update_data):
                updated_count += 1
        else:
            print(f"⚠️ User ID {update_data['user_id']} not found, skipping...")
    
    print(f"\n🎉 Successfully updated {updated_count} users on Railway!")
    
    # Verify updates
    print("\n🔍 Verifying updates...")
    final_users = get_users_on_railway(token)
    
    print(f"\n✅ Personnel dropdown should now show {len(final_users)} users:")
    for user in final_users:
        print(f"   - {user['username']} ({user['role']})")

if __name__ == "__main__":
    main()

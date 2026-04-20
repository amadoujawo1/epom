#!/usr/bin/env python3
"""
Final fix for personnel dropdown issue
Update existing users with proper roles for dropdown
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
    """Main function to fix personnel dropdown"""
    print("🚀 Final fix for personnel dropdown...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Get current users
    users = get_users_on_railway(token)
    if not users:
        return
    
    # Update existing users with proper roles for dropdown
    # Use the actual user IDs we found
    user_updates = [
        {
            "user_id": 5,  # admin
            "username": "admin",
            "first_name": "System",
            "last_name": "Administrator",
            "role": "Admin",
            "department": "IT"
        },
        {
            "user_id": 7,  # ajawo
            "username": "jminister",
            "first_name": "John",
            "last_name": "Minister",
            "role": "Minister",
            "department": "Executive Office"
        },
        {
            "user_id": 8,  # lcham
            "username": "schief",
            "first_name": "Sarah",
            "last_name": "Chief",
            "role": "Chief of staff",
            "department": "Executive Office"
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
    
    print(f"\n🌐 Test the dropdown at: {RAILWAY_URL}")
    print("   1. Login as admin/admin123")
    print("   2. Go to Actions page") 
    print("   3. Click '+ New Directive'")
    print("   4. Check 'Assign To Owner' dropdown")

if __name__ == "__main__":
    main()

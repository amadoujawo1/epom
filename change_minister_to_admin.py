#!/usr/bin/env python3
"""
Change minister user role to Admin
"""

import sqlite3
import os

def change_minister_to_admin():
    """Change the minister user's role to Admin"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== CHANGING MINISTER ROLE TO ADMIN ===')
        
        # Get current minister user info
        cursor.execute('SELECT id, username, first_name, last_name, role FROM users WHERE username = ?', ('minister',))
        minister_user = cursor.fetchone()
        
        if minister_user:
            user_id, username, first_name, last_name, role = minister_user
            print(f'Found minister user:')
            print(f'  ID: {user_id}')
            print(f'  Username: {username}')
            print(f'  Name: {first_name} {last_name}')
            print(f'  Current Role: {role}')
            
            # Update the role to Admin
            print(f'\nUpdating {username} role from "{role}" to "Admin"...')
            cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('Admin', 'minister'))
            conn.commit()
            
            # Verify the change
            cursor.execute('SELECT role FROM users WHERE username = ?', ('minister',))
            new_role = cursor.fetchone()
            print(f'Success! {username} role is now: {new_role[0]}')
            
        else:
            print('Minister user not found in database')
            
        # Show all users after the change
        print('\n=== UPDATED USER LIST ===')
        cursor.execute('SELECT id, username, role FROM users ORDER BY id')
        users = cursor.fetchall()
        
        for user in users:
            user_id, username, role = user
            print(f'ID: {user_id}, Username: {username}, Role: {role}')
            
    finally:
        conn.close()

if __name__ == "__main__":
    change_minister_to_admin()

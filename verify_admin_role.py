#!/usr/bin/env python3
"""
Verify admin user has the correct Admin role
"""

import sqlite3
import os

def verify_admin_role():
    """Verify admin user has the correct Admin role"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== VERIFYING ADMIN USER ROLE ===')
        
        # Check admin user role
        cursor.execute('SELECT id, username, role FROM users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, username, role = admin_user
            print(f'Admin User ID: {user_id}')
            print(f'Admin Username: {username}')
            print(f'Admin Role: {role}')
            
            if role == 'Admin':
                print('SUCCESS: Admin user has the correct Admin role')
            else:
                print(f'ISSUE: Admin user has role "{role}" instead of "Admin"')
                print('Updating admin user to have Admin role...')
                cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('Admin', 'admin'))
                conn.commit()
                print('Admin role updated successfully')
                
                # Verify the update
                cursor.execute('SELECT role FROM users WHERE username = ?', ('admin',))
                new_role = cursor.fetchone()
                print(f'Admin role is now: {new_role[0]}')
        else:
            print('Admin user not found in database')
            
    finally:
        conn.close()

if __name__ == "__main__":
    verify_admin_role()

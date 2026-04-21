#!/usr/bin/env python3
"""
Check and fix admin user role - remove minister role from admin
"""

import sqlite3
import os

def check_and_fix_admin_role():
    """Check if admin has minister role and fix it"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== CURRENT USER ROLES ===')
        
        # Get all users and their roles
        cursor.execute('SELECT id, username, first_name, last_name, email, role FROM users')
        users = cursor.fetchall()
        
        for user in users:
            user_id, username, first_name, last_name, email, role = user
            print(f'ID: {user_id}, Username: {username}, Role: {role}')
        
        print('\n=== CHECKING FOR ADMIN AS MINISTER ===')
        
        # Check if admin has minister role
        cursor.execute('SELECT role FROM users WHERE username = ?', ('admin',))
        admin_role = cursor.fetchone()
        
        if admin_role:
            print(f'Admin current role: {admin_role[0]}')
            
            if admin_role[0] == 'Minister':
                print('Admin has Minister role - updating to Admin role...')
                cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('Admin', 'admin'))
                conn.commit()
                print('Admin role updated to Admin')
                
                # Verify the change
                cursor.execute('SELECT role FROM users WHERE username = ?', ('admin',))
                new_role = cursor.fetchone()
                print(f'Admin role is now: {new_role[0]}')
            else:
                print('Admin does not have Minister role')
        else:
            print('Admin user not found')
            
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix_admin_role()

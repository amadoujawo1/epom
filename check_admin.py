#!/usr/bin/env python3
"""
Check admin user status
"""

import sqlite3
import os

def check_admin():
    """Check admin user status"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== CHECKING ADMIN USER ===')
        
        # Check if admin user exists
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f'Admin user found: ID {admin_user[0]}, Username {admin_user[1]}')
            print('Admin user exists with password hash')
        else:
            print('Admin user not found')
            
        # List all users
        cursor.execute('SELECT id, username, role FROM users')
        users = cursor.fetchall()
        
        print(f'\nTotal users: {len(users)}')
        for user in users:
            print(f'  ID: {user[0]}, Username: {user[1]}, Role: {user[2]}')
            
    finally:
        conn.close()

if __name__ == "__main__":
    check_admin()

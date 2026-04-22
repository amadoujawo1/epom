#!/usr/bin/env python3
"""
Fix admin login by resetting password properly
"""

import sqlite3
import bcrypt
import os

def fix_admin_login():
    """Fix admin login by resetting password"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== FIXING ADMIN LOGIN ===')
        
        # Get admin user
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', ('admin',))
        admin = cursor.fetchone()
        
        if admin:
            print(f'Admin user found: ID={admin[0]}, Username={admin[1]}')
            
            # Reset password to admin123
            new_password = 'admin123'
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password, 'admin'))
            conn.commit()
            
            print(f'Password reset to: {new_password}')
            
            # Verify the password
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('admin',))
            stored_hash = cursor.fetchone()[0]
            is_valid = bcrypt.checkpw(new_password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f'Password verification: {is_valid}')
            
            if is_valid:
                print('Admin login should now work with username: admin, password: admin123')
            else:
                print('Password verification failed')
        else:
            print('Admin user not found')
            
    except Exception as e:
        print(f'Error fixing admin login: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_admin_login()

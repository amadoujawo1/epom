#!/usr/bin/env python3
"""
Test admin password verification
"""

import sqlite3
import bcrypt
import os

def test_password():
    """Test admin password verification"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== TESTING ADMIN PASSWORD VERIFICATION ===')
        
        # Get admin user
        cursor.execute('SELECT username, password_hash FROM users WHERE username = ?', ('admin',))
        admin = cursor.fetchone()
        
        if admin:
            username, stored_hash = admin
            print(f'Admin user found: {username}')
            print(f'Stored hash: {stored_hash}')
            
            # Test password verification
            test_password = 'admin123'
            try:
                is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
                print(f'Password "{test_password}" is valid: {is_valid}')
                
                if not is_valid:
                    print('Password verification failed. Resetting password...')
                    # Reset password
                    new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, 'admin'))
                    conn.commit()
                    print('Password reset successfully')
                    
                    # Test again
                    cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('admin',))
                    new_stored_hash = cursor.fetchone()[0]
                    is_valid_new = bcrypt.checkpw(test_password.encode('utf-8'), new_stored_hash.encode('utf-8'))
                    print(f'New password verification: {is_valid_new}')
                    
            except Exception as e:
                print(f'Password verification error: {e}')
        else:
            print('Admin user not found')
            
    finally:
        conn.close()

if __name__ == "__main__":
    test_password()

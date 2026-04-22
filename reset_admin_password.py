#!/usr/bin/env python3
"""
Reset admin password to admin123
"""

import sqlite3
import bcrypt
import os

def reset_admin_password():
    """Reset admin password to admin123"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== RESETTING ADMIN PASSWORD ===')
        
        # Hash the password
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update admin password
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password, 'admin'))
        conn.commit()
        
        print('Admin password reset to: admin123')
        print('You can now login with username: admin, password: admin123')
        
    except Exception as e:
        print(f'Error resetting password: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_admin_password()

#!/usr/bin/env python3
"""
Verify admin fix by checking the Flask app's database connection
"""

import sqlite3
import os
import bcrypt

def verify_admin_fix():
    """Verify the admin fix by checking the actual database"""
    
    print('=== VERIFYING ADMIN FIX ===')
    
    # Check the database that Flask is actually using
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    
    if os.path.exists(db_path):
        print(f'Database file found: {db_path}')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check admin user
            cursor.execute('SELECT id, username, password_hash, is_active FROM users WHERE username = ?', ('admin',))
            admin = cursor.fetchone()
            
            if admin:
                print(f'Admin user found:')
                print(f'  ID: {admin[0]}')
                print(f'  Username: {admin[1]}')
                print(f'  Password hash: {admin[2][:50]}...')
                print(f'  Is active: {admin[3]}')
                
                # Test password verification
                test_password = 'admin123'
                try:
                    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), admin[2].encode('utf-8'))
                    print(f'Password verification for "{test_password}": {is_valid}')
                    
                    if not is_valid:
                        print('Password verification failed - updating password hash...')
                        
                        # Update password hash
                        new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, 'admin'))
                        conn.commit()
                        
                        # Verify again
                        cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('admin',))
                        updated_hash = cursor.fetchone()[0]
                        is_valid_now = bcrypt.checkpw(test_password.encode('utf-8'), updated_hash.encode('utf-8'))
                        print(f'Updated password verification: {is_valid_now}')
                        
                except Exception as e:
                    print(f'Password verification error: {e}')
                
                # Check if user is active
                if not admin[3]:
                    print('Admin user is not active - activating...')
                    cursor.execute('UPDATE users SET is_active = 1 WHERE username = ?', ('admin',))
                    conn.commit()
                    print('Admin user activated')
                
            else:
                print('Admin user not found in database')
                
                # Create admin user
                print('Creating admin user...')
                hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, role, first_name, last_name, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ('admin', 'admin@epom.gov', hashed_password, 'Admin', 'System', 'Administrator', 1))
                conn.commit()
                print('Admin user created successfully')
                
        except Exception as e:
            print(f'Database error: {e}')
            conn.rollback()
        finally:
            conn.close()
    else:
        print(f'Database file not found: {db_path}')
        print('Please ensure the Flask app has created the database')
    
    print('\n=== VERIFICATION COMPLETE ===')

if __name__ == "__main__":
    verify_admin_fix()

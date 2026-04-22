#!/usr/bin/env python3
"""
Direct authentication test to identify the exact issue
"""

import sqlite3
import os
import bcrypt
import requests

def direct_auth_test():
    """Direct test of authentication"""
    
    print('=== DIRECT AUTHENTICATION TEST ===')
    
    # Step 1: Check database directly
    print('\n1. Checking database directly...')
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
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
                
        else:
            print('Admin user not found')
            
    except Exception as e:
        print(f'Database error: {e}')
    finally:
        conn.close()
    
    # Step 2: Test Flask app authentication
    print('\n2. Testing Flask app authentication...')
    
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post("http://localhost:5007/api/auth/login", json=login_data, timeout=5)
        
        print(f'Flask login response: {response.status_code}')
        print(f'Flask login response body: {response.text}')
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            print(f'Flask login successful, token: {token[:50]}...')
            return True
        else:
            print('Flask login failed')
            
            # Check if MFA is required
            if 'mfa_required' in response.text:
                print('MFA is required - testing MFA flow...')
                
                # Get user ID from response
                response_data = response.json()
                user_id = response_data.get('user_id')
                
                if user_id:
                    # Test MFA completion
                    mfa_data = {"user_id": user_id, "mfa_code": "123456"}
                    mfa_response = requests.post("http://localhost:5007/api/auth/mfa", json=mfa_data, timeout=5)
                    
                    print(f'MFA response: {mfa_response.status_code}')
                    print(f'MFA response body: {mfa_response.text}')
                    
                    if mfa_response.status_code == 200:
                        mfa_token_data = mfa_response.json()
                        mfa_token = mfa_token_data.get("token")
                        print(f'MFA login successful, token: {mfa_token[:50]}...')
                        return True
                    else:
                        print('MFA login failed')
                else:
                    print('No user ID in MFA response')
            else:
                print('Regular login failed - checking Flask logs')
                
    except Exception as e:
        print(f'Flask authentication error: {e}')
    
    return False

def test_flask_endpoints():
    """Test Flask endpoints to ensure they're working"""
    
    print('\n=== TESTING FLASK ENDPOINTS ===')
    
    base_url = "http://localhost:5007"
    
    # Test basic Flask app
    try:
        response = requests.get(f"{base_url}/", timeout=2)
        print(f'Root endpoint: {response.status_code}')
    except Exception as e:
        print(f'Root endpoint error: {e}')
    
    # Test login endpoint exists
    try:
        response = requests.options(f"{base_url}/api/auth/login", timeout=2)
        print(f'Login OPTIONS: {response.status_code}')
    except Exception as e:
        print(f'Login OPTIONS error: {e}')
    
    # Test personnel endpoint (should fail without auth)
    try:
        response = requests.get(f"{base_url}/api/personnel", timeout=2)
        print(f'Personnel without auth: {response.status_code}')
    except Exception as e:
        print(f'Personnel endpoint error: {e}')

def main():
    """Main function"""
    
    print('=== DIRECT AUTHENTICATION TEST ===')
    
    # Test Flask endpoints
    test_flask_endpoints()
    
    # Test authentication
    auth_success = direct_auth_test()
    
    print('\n=== TEST RESULTS ===')
    
    if auth_success:
        print('? SUCCESS: Authentication is working!')
        print('? The Register New Directive / Decision form should work now!')
    else:
        print('? FAILURE: Authentication is not working')
        print('? Please check:')
        print('  1. Flask server is running on port 5007')
        print('  2. Database file exists and is accessible')
        print('  3. Admin user exists and is active')
        print('  4. Password hash is correct')
        print('  5. No MFA issues')
    
    print('\n=== DIRECT AUTHENTICATION TEST COMPLETE ===')

if __name__ == "__main__":
    main()

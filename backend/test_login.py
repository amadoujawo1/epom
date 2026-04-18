import requests
import json

# Test the login endpoint
try:
    response = requests.post(
        'http://localhost:5007/api/auth/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=5
    )
    print(f'Login Response Status: {response.status_code}')
    print(f'Login Response: {response.text}')
    
    # If successful, test a protected endpoint
    if response.status_code == 200:
        token = response.json().get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test getting users
        users_response = requests.get('http://localhost:5007/api/users', headers=headers, timeout=5)
        print(f'\\nUsers Response Status: {users_response.status_code}')
        print(f'Users Response: {users_response.text}')
        
except requests.exceptions.ConnectionError:
    print('Server connection failed - make sure the server is running on port 5007')
except Exception as e:
    print(f'Error testing login: {e}')
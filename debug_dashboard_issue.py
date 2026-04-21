#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for dashboard data population issue on Railway
"""

import requests
import json
import sys

def get_auth_token(base_url):
    """Get authentication token"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"Successfully authenticated with {base_url}")
            return token_data.get("token")
        else:
            print(f"Login failed for {base_url}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to {base_url}: {e}")
        return None

def test_dashboard_endpoints(base_url, environment_name):
    """Test all dashboard-related endpoints"""
    print(f"\n=== TESTING {environment_name.upper()} DASHBOARD ENDPOINTS ===")
    
    token = get_auth_token(base_url)
    if not token:
        return {}
    
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    # Test dashboard stats endpoint
    try:
        print(f"Testing /api/dashboard/stats...")
        response = requests.get(f"{base_url}/api/dashboard/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  SUCCESS: {json.dumps(data, indent=2)}")
            results['dashboard_stats'] = {'status': 'success', 'data': data}
        else:
            print(f"  FAILED: {response.status_code} - {response.text}")
            results['dashboard_stats'] = {'status': 'failed', 'error': response.text}
            
    except Exception as e:
        print(f"  ERROR: {e}")
        results['dashboard_stats'] = {'status': 'error', 'error': str(e)}
    
    # Test dashboard simple endpoint
    try:
        print(f"Testing /api/dashboard/simple...")
        response = requests.get(f"{base_url}/api/dashboard/simple", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  SUCCESS: {json.dumps(data, indent=2)}")
            results['dashboard_simple'] = {'status': 'success', 'data': data}
        else:
            print(f"  FAILED: {response.status_code} - {response.text}")
            results['dashboard_simple'] = {'status': 'failed', 'error': response.text}
            
    except Exception as e:
        print(f"  ERROR: {e}")
        results['dashboard_simple'] = {'status': 'error', 'error': str(e)}
    
    # Test individual data endpoints that feed the dashboard
    data_endpoints = [
        ('users', '/api/users'),
        ('actions', '/api/actions'),
        ('documents', '/api/documents'),
        ('projects', '/api/projects'),
        ('events', '/api/events'),
        ('personnel', '/api/personnel'),
        ('calendar', '/api/calendar'),
    ]
    
    print(f"\nTesting data endpoints that feed dashboard...")
    for name, endpoint in data_endpoints:
        try:
            print(f"Testing {endpoint}...")
            if endpoint == '/api/events':
                # Events endpoint might need special handling
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            else:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "object"
                print(f"  SUCCESS: {count} items")
                results[name] = {'status': 'success', 'count': count, 'data': data}
            else:
                print(f"  FAILED: {response.status_code}")
                results[name] = {'status': 'failed', 'error': response.text}
                
        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = {'status': 'error', 'error': str(e)}
    
    return results

def compare_environments():
    """Compare Railway vs localhost dashboard endpoints"""
    print("=== DASHBOARD ISSUE DIAGNOSIS ===")
    
    railway_url = "https://web-production-f029b.up.railway.app"
    localhost_url = "http://localhost:5007"
    
    # Test Railway
    railway_results = test_dashboard_endpoints(railway_url, "Railway")
    
    # Test localhost (if available)
    print(f"\nNote: Testing localhost requires local server running on port 5007")
    print(f"If localhost is not running, those tests will fail")
    
    try:
        localhost_results = test_dashboard_endpoints(localhost_url, "Localhost")
    except:
        print(f"Localhost server not available - skipping localhost comparison")
        localhost_results = {}
    
    # Compare results
    print(f"\n=== COMPARISON ANALYSIS ===")
    
    endpoints_to_check = ['dashboard_stats', 'dashboard_simple', 'users', 'actions', 'documents', 'projects', 'events', 'personnel', 'calendar']
    
    for endpoint in endpoints_to_check:
        railway_status = railway_results.get(endpoint, {}).get('status', 'not_tested')
        localhost_status = localhost_results.get(endpoint, {}).get('status', 'not_tested')
        
        print(f"\n{endpoint}:")
        print(f"  Railway: {railway_status}")
        print(f"  Localhost: {localhost_status}")
        
        if railway_status == 'success' and localhost_status == 'success':
            railway_data = railway_results[endpoint].get('data')
            localhost_data = localhost_results[endpoint].get('data')
            
            if isinstance(railway_data, list) and isinstance(localhost_data, list):
                print(f"  Railway count: {len(railway_data)}")
                print(f"  Localhost count: {len(localhost_data)}")
                
                if len(railway_data) != len(localhost_data):
                    print(f"  *** DATA COUNT MISMATCH ***")
                else:
                    print(f"  Counts match")
            elif isinstance(railway_data, dict) and isinstance(localhost_data, dict):
                print(f"  Both return objects - comparing keys...")
                railway_keys = set(railway_data.keys())
                localhost_keys = set(localhost_data.keys())
                
                if railway_keys != localhost_keys:
                    print(f"  *** KEY MISMATCH ***")
                    print(f"  Railway keys: {railway_keys}")
                    print(f"  Localhost keys: {localhost_keys}")
                else:
                    print(f"  Keys match")
        
        elif railway_status != 'success':
            print(f"  *** RAILWAY ENDPOINT FAILED ***")
            if 'error' in railway_results.get(endpoint, {}):
                error = railway_results[endpoint]['error']
                if 'created_by' in error and 'does not exist' in error:
                    print(f"  CAUSE: Missing created_by column in actions table")
                elif '404' in str(railway_results.get(endpoint, {}).get('error', '')):
                    print(f"  CAUSE: Endpoint not deployed yet")
                else:
                    print(f"  ERROR: {error[:100]}...")

def identify_root_cause():
    """Identify the root cause of dashboard data issues"""
    print(f"\n=== ROOT CAUSE ANALYSIS ===")
    
    railway_url = "https://web-production-f029b.up.railway.app"
    token = get_auth_token(railway_url)
    
    if not token:
        print("Cannot authenticate with Railway - unable to complete analysis")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if dashboard endpoints exist
    dashboard_endpoints = ['/api/dashboard/stats', '/api/dashboard/simple']
    
    for endpoint in dashboard_endpoints:
        try:
            response = requests.get(f"{railway_url}{endpoint}", headers=headers)
            
            if response.status_code == 404:
                print(f"*** {endpoint} NOT DEPLOYED (404) ***")
                print(f"This endpoint exists in code but not in Railway deployment")
            elif response.status_code == 500:
                print(f"*** {endpoint} SERVER ERROR (500) ***")
                error_text = response.text
                if 'created_by' in error_text:
                    print(f"Caused by missing created_by column")
                else:
                    print(f"Error: {error_text[:200]}...")
            elif response.status_code == 200:
                data = response.json()
                print(f"*** {endpoint} WORKING ***")
                print(f"Returns: {type(data).__name__}")
                
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
                    # Check if data is empty
                    if all(v == 0 or v == [] or v is None for v in data.values()):
                        print(f"*** ALL VALUES ARE EMPTY/ZERO ***")
                        print(f"This suggests database tables are empty")
                elif isinstance(data, list):
                    print(f"Returns list with {len(data)} items")
                    if len(data) == 0:
                        print(f"*** EMPTY LIST ***")
                        print(f"This suggests no data in database")
                        
        except Exception as e:
            print(f"Error testing {endpoint}: {e}")

def provide_solution():
    """Provide solution based on diagnosis"""
    print(f"\n=== SOLUTION RECOMMENDATIONS ===")
    
    print(f"""
Based on the analysis, here are the likely causes and solutions for dashboard data not populating:

LIKELY CAUSES:
1. Missing dashboard endpoints (404 errors)
2. Database schema issues (created_by column missing)
3. Empty database tables on Railway
4. Endpoint deployment lag

SOLUTIONS:

1. DEPLOYMENT FIXES:
   - Wait for Railway deployment to complete (2-3 minutes)
   - Check if /api/dashboard/stats and /api/dashboard/simple are deployed
   - Force redeployment if needed

2. DATABASE FIXES:
   - Fix missing created_by column: POST /api/fix-created-by
   - Or use: POST /api/setup-database
   - Verify database tables have data

3. DATA VERIFICATION:
   - Check if users, documents, actions exist in Railway database
   - Create sample data if tables are empty
   - Verify admin user exists

4. FRONTEND DEBUGGING:
   - Check browser console for API errors
   - Verify frontend is calling correct endpoints
   - Check network tab for failed requests

IMMEDIATE ACTIONS:
1. Test dashboard endpoints directly
2. Fix any 404 or 500 errors
3. Ensure database has sample data
4. Verify frontend-backend communication
""")

if __name__ == "__main__":
    print("Starting dashboard data population diagnosis...")
    
    # Compare environments
    compare_environments()
    
    # Identify root cause
    identify_root_cause()
    
    # Provide solution
    provide_solution()
    
    print(f"\nDashboard diagnosis completed!")

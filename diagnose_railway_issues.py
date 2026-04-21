#!/usr/bin/env python3
"""
Comprehensive diagnostic tool to identify why features work locally but not on Railway
"""

import requests
import json
import os
from datetime import datetime

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post("https://web-production-f029b.up.railway.app/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("Successfully authenticated with Railway")
            return token_data.get("token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to Railway: {e}")
        return None

def test_railway_endpoints():
    """Test all key endpoints on Railway"""
    print("=== RAILWAY ENDPOINT DIAGNOSTICS ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot test endpoints without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    endpoints = [
        ("GET", "/api/users", "Users endpoint"),
        ("GET", "/api/actions", "Actions endpoint"),
        ("GET", "/api/documents", "Documents endpoint"),
        ("GET", "/api/projects", "Projects endpoint"),
        ("GET", "/api/events", "Events endpoint"),
        ("GET", "/api/personnel", "Personnel endpoint"),
        ("GET", "/api/dashboard/stats", "Dashboard stats"),
        ("GET", "/api/dashboard/simple", "Dashboard simple"),
        ("GET", "/api/calendar", "Calendar endpoint"),
    ]
    
    results = {}
    
    for method, endpoint, description in endpoints:
        try:
            print(f"\nTesting {description}: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            
            status = "SUCCESS" if response.status_code == 200 else f"FAILED ({response.status_code})"
            print(f"  Status: {status}")
            
            if response.status_code != 200:
                print(f"  Error: {response.text}")
                results[endpoint] = {"status": "failed", "error": response.text}
            else:
                data = response.json()
                count = len(data) if isinstance(data, list) else "object"
                print(f"  Data type: {type(data).__name__}, Count: {count}")
                results[endpoint] = {"status": "success", "count": count, "type": type(data).__name__}
                
        except Exception as e:
            print(f"  Exception: {e}")
            results[endpoint] = {"status": "exception", "error": str(e)}
    
    return results

def test_document_workflow():
    """Test complete document workflow on Railway"""
    print("\n=== DOCUMENT WORKFLOW TEST ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot test document workflow without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    try:
        # 1. Create document
        print("1. Creating document...")
        doc_data = {
            "title": f"Test Document {datetime.now().isoformat()}",
            "content": "Test content for Railway diagnosis",
            "category": "Minister Briefings",
            "doc_type": "Briefing Note"
        }
        
        create_response = requests.post(f"{base_url}/api/documents/template", json=doc_data, headers=headers)
        
        if create_response.status_code == 201:
            doc_info = create_response.json()
            doc_id = doc_info['id']
            print(f"   SUCCESS: Document created with ID: {doc_id}")
            
            # 2. Retrieve documents
            print("2. Retrieving documents...")
            docs_response = requests.get(f"{base_url}/api/documents", headers=headers)
            
            if docs_response.status_code == 200:
                docs = docs_response.json()
                print(f"   SUCCESS: Retrieved {len(docs)} documents")
                
                # 3. Update document status (submit button functionality)
                print("3. Testing document submit (status update)...")
                update_response = requests.put(f"{base_url}/api/documents/{doc_id}", 
                                             json={"status": "Pending Leader Clearance"}, 
                                             headers=headers)
                
                if update_response.status_code == 200:
                    print(f"   SUCCESS: Document status updated to 'Pending Leader Clearance'")
                    
                    # 4. Verify update
                    print("4. Verifying document update...")
                    verify_response = requests.get(f"{base_url}/api/documents", headers=headers)
                    
                    if verify_response.status_code == 200:
                        updated_docs = verify_response.json()
                        updated_doc = next((d for d in updated_docs if d['id'] == doc_id), None)
                        
                        if updated_doc and updated_doc['status'] == 'Pending Leader Clearance':
                            print(f"   SUCCESS: Document workflow complete - status verified")
                            return True
                        else:
                            print(f"   FAILED: Document status not updated correctly")
                            return False
                    else:
                        print(f"   FAILED: Could not verify document update")
                        return False
                else:
                    print(f"   FAILED: Document status update failed - {update_response.text}")
                    return False
            else:
                print(f"   FAILED: Could not retrieve documents - {docs_response.text}")
                return False
        else:
            print(f"   FAILED: Document creation failed - {create_response.text}")
            return False
            
    except Exception as e:
        print(f"   EXCEPTION: {e}")
        return False

def test_action_workflow():
    """Test action workflow on Railway"""
    print("\n=== ACTION WORKFLOW TEST ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot test action workflow without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    try:
        # 1. Get users for assignment
        print("1. Getting users for action assignment...")
        users_response = requests.get(f"{base_url}/api/users", headers=headers)
        
        if users_response.status_code != 200:
            print(f"   FAILED: Cannot get users - {users_response.text}")
            return False
        
        users = users_response.json()
        if not users:
            print("   FAILED: No users available for action assignment")
            return False
        
        admin_user = users[0]
        print(f"   Using user: {admin_user['username']} (ID: {admin_user['id']})")
        
        # 2. Create action
        print("2. Creating action...")
        action_data = {
            "title": f"Test Action {datetime.now().isoformat()}",
            "description": "Test action for Railway diagnosis",
            "assigned_to": admin_user["id"],
            "status": "Pending",
            "priority": "Medium"
        }
        
        create_response = requests.post(f"{base_url}/api/actions", json=action_data, headers=headers)
        
        if create_response.status_code == 201:
            print("   SUCCESS: Action created")
            
            # 3. Retrieve actions
            print("3. Retrieving actions...")
            actions_response = requests.get(f"{base_url}/api/actions", headers=headers)
            
            if actions_response.status_code == 200:
                actions = actions_response.json()
                print(f"   SUCCESS: Retrieved {len(actions)} actions")
                
                if actions:
                    sample_action = actions[0]
                    print(f"   Sample action: {sample_action['title']} - {sample_action['status']}")
                    return True
                else:
                    print("   WARNING: No actions found after creation")
                    return False
            else:
                print(f"   FAILED: Cannot retrieve actions - {actions_response.text}")
                return False
        else:
            print(f"   FAILED: Action creation failed - {create_response.text}")
            return False
            
    except Exception as e:
        print(f"   EXCEPTION: {e}")
        return False

def check_database_migration():
    """Check if database migration is needed"""
    print("\n=== DATABASE MIGRATION CHECK ===")
    
    token = get_auth_token()
    if not token:
        print("Cannot check database without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://web-production-f029b.up.railway.app"
    
    try:
        # Test actions endpoint to see if created_by column issue exists
        print("Testing actions endpoint for created_by column issue...")
        response = requests.get(f"{base_url}/api/actions", headers=headers)
        
        if response.status_code == 200:
            print("   SUCCESS: Actions endpoint working - no migration needed")
            return True
        elif response.status_code == 500:
            error_text = response.text
            if "created_by" in error_text and "does not exist" in error_text:
                print("   ISSUE: created_by column missing - migration needed")
                
                # Try migration
                print("   Attempting migration...")
                migration_response = requests.post(f"{base_url}/api/migrate-actions", headers=headers)
                
                if migration_response.status_code == 200:
                    print("   SUCCESS: Migration completed")
                    
                    # Test again
                    test_response = requests.get(f"{base_url}/api/actions", headers=headers)
                    if test_response.status_code == 200:
                        print("   SUCCESS: Actions endpoint working after migration")
                        return True
                    else:
                        print(f"   FAILED: Actions still broken after migration - {test_response.text}")
                        return False
                else:
                    print(f"   FAILED: Migration failed - {migration_response.text}")
                    return False
            else:
                print(f"   DIFFERENT ERROR: {error_text}")
                return False
        else:
            print(f"   UNEXPECTED STATUS: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   EXCEPTION: {e}")
        return False

def generate_summary_report(endpoint_results, doc_workflow, action_workflow, migration_status):
    """Generate a comprehensive summary report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE RAILWAY DIAGNOSIS REPORT")
    print("="*60)
    
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    
    # Endpoint Summary
    print(f"\n1. ENDPOINT STATUS SUMMARY:")
    working_endpoints = sum(1 for r in endpoint_results.values() if r["status"] == "success")
    total_endpoints = len(endpoint_results)
    print(f"   Working: {working_endpoints}/{total_endpoints}")
    
    for endpoint, result in endpoint_results.items():
        status_icon = "SUCCESS" if result["status"] == "success" else "FAILED"
        print(f"   {endpoint}: {status_icon}")
        if result["status"] != "success":
            print(f"     Error: {result.get('error', 'Unknown error')}")
    
    # Workflow Summary
    print(f"\n2. WORKFLOW FUNCTIONALITY:")
    print(f"   Document Workflow: {'WORKING' if doc_workflow else 'BROKEN'}")
    print(f"   Action Workflow: {'WORKING' if action_workflow else 'BROKEN'}")
    print(f"   Database Migration: {'COMPLETED' if migration_status else 'NEEDED'}")
    
    # Recommendations
    print(f"\n3. RECOMMENDATIONS:")
    
    if not migration_status:
        print("   - Run database migration: POST /api/migrate-actions")
    
    if not doc_workflow:
        print("   - Check document creation and update endpoints")
        print("   - Verify document submit functionality")
    
    if not action_workflow:
        print("   - Check action creation endpoint")
        print("   - Verify actions table schema")
    
    failed_endpoints = [ep for ep, r in endpoint_results.items() if r["status"] != "success"]
    if failed_endpoints:
        print("   - Fix failing endpoints:")
        for ep in failed_endpoints:
            print(f"     * {ep}")
    
    if working_endpoints == total_endpoints and doc_workflow and action_workflow and migration_status:
        print("   - All systems working correctly!")
    
    print(f"\n4. NEXT STEPS:")
    if not migration_status:
        print("   1. Call migration endpoint first")
    print("   2. Test individual failing endpoints")
    print("   3. Check Railway environment variables")
    print("   4. Verify database connectivity")

if __name__ == "__main__":
    print("Starting comprehensive Railway diagnosis...")
    
    # Run all diagnostics
    endpoint_results = test_railway_endpoints()
    migration_status = check_database_migration()
    doc_workflow = test_document_workflow()
    action_workflow = test_action_workflow()
    
    # Generate report
    generate_summary_report(endpoint_results, doc_workflow, action_workflow, migration_status)
    
    print(f"\nDiagnosis complete!")

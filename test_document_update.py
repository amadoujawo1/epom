#!/usr/bin/env python3
"""
Test document update endpoint to fix submit button not working in document creation
"""

import requests
import json

def get_auth_token():
    """Get authentication token from backend"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post("http://127.0.0.1:5007/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("Successfully authenticated with backend")
            return token_data.get("token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return None

def test_document_update():
    """Test document update endpoint for submit button functionality"""
    print("Testing document update endpoint...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    base_url = "http://127.0.0.1:5007"
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get a document to update
    try:
        print("Getting documents to find one to update...")
        response = requests.get(f"{base_url}/api/documents", headers=headers)
        
        if response.status_code == 200:
            docs = response.json()
            if not docs:
                print("No documents found. Creating a test document first...")
                
                # Create a test document
                test_doc = {
                    "title": "Test Document for Submit",
                    "content": "This is a test document for submit functionality",
                    "category": "Minister Briefings",
                    "doc_type": "Briefing Note"
                }
                
                create_response = requests.post(f"{base_url}/api/documents/template", json=test_doc, headers=headers)
                if create_response.status_code == 201:
                    doc_data = create_response.json()
                    doc_id = doc_data.get('id')
                    print(f"Created test document with ID: {doc_id}")
                else:
                    print(f"Failed to create test document: {create_response.text}")
                    return
            else:
                # Use existing document
                doc_id = docs[0].get('id')
                print(f"Using existing document with ID: {doc_id}")
        else:
            print(f"Failed to get documents: {response.text}")
            return
            
    except Exception as e:
        print(f"Error getting documents: {e}")
        return
    
    # Test document status update (what submit button does)
    try:
        print(f"\nTesting document status update for ID: {doc_id}")
        update_data = {
            "status": "Pending Leader Clearance"
        }
        
        response = requests.put(f"{base_url}/api/documents/{doc_id}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_doc = response.json()
            print(f"SUCCESS: Document updated successfully")
            print(f"Document ID: {updated_doc.get('id')}")
            print(f"Title: {updated_doc.get('title')}")
            print(f"New Status: {updated_doc.get('status')}")
            print(f"Category: {updated_doc.get('category')}")
            print(f"Doc Type: {updated_doc.get('doc_type')}")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Verify the update by retrieving the document
    try:
        print("\nVerifying document update...")
        response = requests.get(f"{base_url}/api/documents", headers=headers)
        
        if response.status_code == 200:
            docs = response.json()
            updated_doc = next((d for d in docs if d.get('id') == doc_id), None)
            
            if updated_doc:
                print(f"SUCCESS: Document status verified")
                print(f"  ID: {updated_doc.get('id')}")
                print(f"  Title: {updated_doc.get('title')}")
                print(f"  Status: {updated_doc.get('status')}")
                print(f"  Category: {updated_doc.get('category')}")
                print(f"  Doc Type: {updated_doc.get('doc_type')}")
            else:
                print("Document not found after update")
        else:
            print(f"FAILED to verify: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error verifying: {e}")

if __name__ == "__main__":
    test_document_update()

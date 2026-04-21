#!/usr/bin/env python3
"""
Test document template endpoint to fix Digitized Briefing / Decision Note submission failed error
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

def test_document_template():
    """Test document template endpoint"""
    print("Testing document template endpoint...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    base_url = "http://127.0.0.1:5007"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test document template creation (what frontend actually calls)
    test_document = {
        "title": "Test Digitized Briefing from Template",
        "content": "This is a test briefing content from template",
        "category": "Minister Briefings",
        "doc_type": "Briefing Note"
    }
    
    try:
        print("Creating document from template...")
        response = requests.post(f"{base_url}/api/documents/template", json=test_document, headers=headers)
        
        if response.status_code == 201:
            doc_data = response.json()
            print(f"SUCCESS: Document created from template")
            print(f"Document ID: {doc_data.get('id')}")
            print(f"Title: {doc_data.get('title')}")
            print(f"Status: {doc_data.get('status')}")
            print(f"Category: {doc_data.get('category')}")
            print(f"Doc Type: {doc_data.get('doc_type')}")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test document retrieval to verify it was created
    try:
        print("\nTesting document retrieval...")
        response = requests.get(f"{base_url}/api/documents", headers=headers)
        
        if response.status_code == 200:
            docs = response.json()
            print(f"SUCCESS: Retrieved {len(docs)} documents")
            if docs:
                print("Latest document:")
                latest = docs[0]
                print(f"  ID: {latest.get('id')}")
                print(f"  Title: {latest.get('title')}")
                print(f"  Status: {latest.get('status')}")
                print(f"  Category: {latest.get('category')}")
                print(f"  Doc Type: {latest.get('doc_type')}")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_document_template()

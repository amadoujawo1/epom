#!/usr/bin/env python3
"""
Test document creation endpoint to fix Digitized Briefing / Decision Note submission failed error
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

def test_document_creation():
    """Test document creation endpoint"""
    print("Testing document creation endpoint...")
    
    token = get_auth_token()
    if not token:
        print("Cannot test without authentication")
        return
    
    base_url = "http://127.0.0.1:5007"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test document creation
    test_document = {
        "title": "Test Digitized Briefing",
        "content": "This is a test briefing content",
        "category": "Briefing",
        "doc_type": "Briefing",
        "status": "Draft"
    }
    
    try:
        print("Creating test document...")
        response = requests.post(f"{base_url}/api/documents", json=test_document, headers=headers)
        
        if response.status_code == 201:
            doc_data = response.json()
            print(f"SUCCESS: Document created successfully")
            print(f"Document ID: {doc_data.get('id')}")
            print(f"Title: {doc_data.get('title')}")
            print(f"Status: {doc_data.get('status')}")
            print(f"Category: {doc_data.get('category')}")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test document retrieval
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
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_document_creation()

#!/usr/bin/env python3
"""
Test all dashboard functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_all_functionality():
    print("Testing All Dashboard Functionality")
    print("=" * 50)
    
    # First login to get token
    login_data = {
        "email": "demo@example.com",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code != 200:
            print("Login failed")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Test 1: Available Schemes
    print("\n1. Testing Available Schemes...")
    try:
        response = requests.get(f"{BASE_URL}/schemes/", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            schemes = data.get('schemes', [])
            print(f"   Available schemes: {len(schemes)}")
            for scheme in schemes:
                print(f"   - {scheme['name']} (Score: {scheme['score']})")
        else:
            print(f"   Schemes failed: {response.status_code}")
    except Exception as e:
        print(f"   Schemes error: {e}")
    
    # Test 2: Transactions
    print("\n2. Testing Transactions...")
    try:
        response = requests.get(f"{BASE_URL}/transactions/", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])
            print(f"   Transactions: {len(transactions)}")
            for txn in transactions[:3]:  # Show first 3
                print(f"   - {txn['type']}: {txn['description']}")
        else:
            print(f"   Transactions failed: {response.status_code}")
    except Exception as e:
        print(f"   Transactions error: {e}")
    
    # Test 3: Quick Actions - QR Generation
    print("\n3. Testing QR Generation...")
    try:
        response = requests.post(f"{BASE_URL}/qr/generate", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   QR generated: {len(data.get('qr_text', ''))} characters")
        else:
            print(f"   QR generation failed: {response.status_code}")
    except Exception as e:
        print(f"   QR generation error: {e}")
    
    # Test 4: Quick Actions - Smart Card
    print("\n4. Testing Smart Card...")
    try:
        response = requests.get(f"{BASE_URL}/qr/smartcard", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print(f"   Smart card: {user.get('idverse_number', 'N/A')}")
            print(f"   VCs: {len(data.get('verifiable_credentials', []))}")
            print(f"   Benefits: {data.get('benefits', {}).get('total_applications', 0)}")
        else:
            print(f"   Smart card failed: {response.status_code}")
    except Exception as e:
        print(f"   Smart card error: {e}")
    
    # Test 5: Quick Actions - Check Scheme Status
    print("\n5. Testing Check Scheme Status...")
    try:
        response = requests.get(f"{BASE_URL}/benefits/applications", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            applications = data.get('applications', [])
            print(f"   Applications: {len(applications)}")
            for app in applications:
                print(f"   - {app['scheme_name']}: {app['status']}")
        else:
            print(f"   Applications failed: {response.status_code}")
    except Exception as e:
        print(f"   Applications error: {e}")
    
    # Test 6: Document Upload (simulate)
    print("\n6. Testing Document Upload...")
    try:
        # Create a simple text file for testing
        test_file = "test_document.txt"
        with open(test_file, 'w') as f:
            f.write("This is a test document for IDverse system.")
        
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print(f"   Document uploaded: {data.get('filename')} (CID: {data.get('cid')[:20]}...)")
        else:
            print(f"   Document upload failed: {response.status_code}")
        
        # Clean up test file
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
            
    except Exception as e:
        print(f"   Document upload error: {e}")
    
    # Test 7: Document Listing
    print("\n7. Testing Document Listing...")
    try:
        response = requests.get(f"{BASE_URL}/documents/list", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"   Documents: {len(documents)}")
            for doc in documents:
                print(f"   - {doc['filename']} ({doc['file_size']} bytes)")
        else:
            print(f"   Document listing failed: {response.status_code}")
    except Exception as e:
        print(f"   Document listing error: {e}")
    
    # Test 8: Linked IDs
    print("\n8. Testing Linked IDs...")
    try:
        response = requests.get(f"{BASE_URL}/linked-ids/", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            linked_ids = data.get('linked_ids', [])
            print(f"   Linked IDs: {len(linked_ids)}")
            for linked_id in linked_ids:
                print(f"   - {linked_id['name']}: {linked_id['number']} ({linked_id['status']})")
        else:
            print(f"   Linked IDs failed: {response.status_code}")
    except Exception as e:
        print(f"   Linked IDs error: {e}")
    
    print("\n" + "=" * 50)
    print("All functionality testing complete!")

if __name__ == "__main__":
    test_all_functionality()

#!/usr/bin/env python3
"""
Test new functionality endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_new_endpoints():
    print("🚀 Testing New Functionality Endpoints")
    print("=" * 50)
    
    # First login to get token
    login_data = {
        "email": "demo@example.com",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code != 200:
            print("❌ Login failed")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test transactions endpoint
    print("\n📊 Testing Transactions Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/transactions/", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transactions: {data.get('total', 0)} transactions found")
            if data.get('transactions'):
                print(f"   - {data['transactions'][0]['description']}")
        else:
            print(f"❌ Transactions failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Transactions error: {e}")
    
    # Test transactions summary
    print("\n📈 Testing Transactions Summary...")
    try:
        response = requests.get(f"{BASE_URL}/transactions/summary", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            print(f"✅ Summary: {summary.get('total_benefits_received', 0)} INR benefits, {summary.get('total_applications', 0)} applications")
        else:
            print(f"❌ Summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Summary error: {e}")
    
    # Test QR generation
    print("\n🔲 Testing QR Generation...")
    try:
        response = requests.post(f"{BASE_URL}/qr/generate", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ QR generation successful")
            print(f"   - Data length: {len(data.get('qr_text', ''))} characters")
        else:
            print(f"❌ QR generation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ QR generation error: {e}")
    
    # Test smart card
    print("\n💳 Testing Smart Card...")
    try:
        response = requests.get(f"{BASE_URL}/qr/smartcard", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print(f"✅ Smart card: {user.get('idverse_number', 'N/A')}")
            print(f"   - VCs: {len(data.get('verifiable_credentials', []))}")
            print(f"   - Benefits: {data.get('benefits', {}).get('total_applications', 0)}")
        else:
            print(f"❌ Smart card failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Smart card error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 New functionality test complete!")

if __name__ == "__main__":
    test_new_endpoints()


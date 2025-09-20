#!/usr/bin/env python3
"""
Quick IDVerse API Test Script
Tests all endpoints with proper error handling
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
jwt_token = None

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        if response.status_code < 400:
            return response.json()
        else:
            print(f"❌ {method} {endpoint}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error calling {method} {endpoint}: {e}")
        return None

def test_health():
    """Test health endpoint"""
    print("1. Testing Health Check...")
    result = make_request("GET", "/health")
    if result and result.get("status") == "ok":
        print("✅ Health Check: OK")
        return True
    else:
        print("❌ Health Check: Failed")
        return False

def test_registration():
    """Test user registration"""
    print("\n2. Testing User Registration...")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "password123"
    }
    
    result = make_request("POST", "/auth/register", data)
    if result and "message" in result:
        print(f"✅ Registration: {result['message']}")
        return data["email"]  # Return email for login
    else:
        print("❌ Registration: Failed")
        return None

def test_login(email):
    """Test user login"""
    print("\n3. Testing User Login...")
    data = {
        "email": email,
        "password": "password123"
    }
    
    result = make_request("POST", "/auth/login", data)
    if result and "access_token" in result:
        global jwt_token
        jwt_token = result["access_token"]
        print(f"✅ Login: JWT token received")
        print(f"   User: {result['user']['username']}")
        return True
    else:
        print("❌ Login: Failed")
        return False

def test_vc_request():
    """Test VC request issue"""
    print("\n4. Testing VC Request Issue...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {
        "type": "GovID",
        "claims": {
            "name": "Shubham Ugale",
            "age": 25,
            "address": "Mumbai, India"
        }
    }
    
    result = make_request("POST", "/vc/request-issue", data, headers)
    if result and "request_id" in result:
        print(f"✅ VC Request: {result['request_id']}")
        return result["request_id"]
    else:
        print("❌ VC Request: Failed")
        return None

def test_vc_issue(request_id):
    """Test VC issue"""
    print("\n5. Testing VC Issue...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"request_id": request_id}
    
    result = make_request("POST", "/vc/issue", data, headers)
    if result and "vc_id" in result:
        print(f"✅ VC Issue: {result['vc_id']}")
        print(f"   CID: {result.get('cid', 'N/A')}")
        return result["vc_id"]
    else:
        print("❌ VC Issue: Failed")
        return None

def test_vc_status(vc_id):
    """Test VC status check"""
    print("\n6. Testing VC Status...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    result = make_request("GET", f"/vc/status/{vc_id}", headers=headers)
    if result and "status" in result:
        print(f"✅ VC Status: {result['status']}")
        print(f"   Verifiable: {result.get('verifiable', 'N/A')}")
        return True
    else:
        print("❌ VC Status: Failed")
        return False

def test_benefits_apply():
    """Test benefits application"""
    print("\n7. Testing Benefits Apply...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {
        "scheme_id": "scheme-001",
        "scheme_name": "PM Kisan Yojana",
        "required_credentials": ["GovID"],
        "application_data": {
            "land_holding": "2 acres",
            "bank_account": "1234567890"
        }
    }
    
    result = make_request("POST", "/benefits/apply", data, headers)
    if result and "application_id" in result:
        print(f"✅ Benefits Apply: {result['application_id']}")
        return result["application_id"]
    else:
        print("❌ Benefits Apply: Failed")
        return None

def test_benefits_wallet():
    """Test benefits wallet"""
    print("\n8. Testing Benefits Wallet...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    result = make_request("GET", "/benefits/wallet", headers=headers)
    if result and "wallet_items" in result:
        print(f"✅ Benefits Wallet: {result['total_entitlements']} items")
        return True
    else:
        print("❌ Benefits Wallet: Failed")
        return False

def test_schemes():
    """Test schemes list"""
    print("\n9. Testing Schemes List...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    result = make_request("GET", "/schemes/", headers=headers)
    if result and "schemes" in result:
        print(f"✅ Schemes: {result['total']} available")
        return True
    else:
        print("❌ Schemes: Failed")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n10. Testing Error Handling...")
    headers = {"Authorization": "Bearer invalid_token"}
    
    result = make_request("GET", "/benefits/wallet", headers=headers)
    if result is None:  # Should fail with invalid token
        print("✅ Error Handling: Correctly rejected invalid JWT")
        return True
    else:
        print("❌ Error Handling: Should have rejected invalid JWT")
        return False

def main():
    """Run all tests"""
    print("🧪 IDVerse Complete System Testing")
    print("=================================")
    
    # Test basic connectivity
    if not test_health():
        print("\n❌ Server not responding. Make sure Flask app is running on localhost:5000")
        sys.exit(1)
    
    # Test user flow
    email = test_registration()
    if not email:
        print("\n❌ Registration failed. Check database connection.")
        sys.exit(1)
    
    if not test_login(email):
        print("\n❌ Login failed. Check authentication.")
        sys.exit(1)
    
    # Test VC flow
    request_id = test_vc_request()
    if request_id:
        vc_id = test_vc_issue(request_id)
        if vc_id:
            test_vc_status(vc_id)
    
    # Test benefits flow
    test_benefits_apply()
    test_benefits_wallet()
    
    # Test other endpoints
    test_schemes()
    test_error_handling()
    
    print("\n🎉 Testing Complete!")
    print("===================")
    print("Check results above for any failures.")

if __name__ == "__main__":
    main()

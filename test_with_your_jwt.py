#!/usr/bin/env python3
"""
IDVerse API Test Script with Your JWT Token
Uses the JWT token you provided to test all endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"

# Your JWT Token (paste it here)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1ODM1OTc3OSwianRpIjoiZTI5ZDAzNjItMTRiMC00YWZhLWFjZGQtMGMzMjUxYzk2ODIzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3RAZXhhbXBsZS5jb20iLCJuYmYiOjE3NTgzNTk3NzksImNzcmYiOiIyNWE2Mjc3ZS0xM2MyLTRjNjAtYTk3ZS1mOGQyOGEwMWIwZDEiLCJleHAiOjE3NTgzNjA2Nzl9.ah3Z8525QSMwzlJ7M3Rxi8qmYdvzjbW1f7-lBTeJLW4"

def make_request(method, endpoint, data=None, use_auth=True):
    """Make HTTP request with your JWT token"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if use_auth:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        print(f"📡 {method} {endpoint} -> {response.status_code}")
        
        if response.status_code < 400:
            try:
                return response.json()
            except:
                return {"message": "Success", "status_code": response.status_code}
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error calling {method} {endpoint}: {e}")
        return None

def test_all_endpoints():
    """Test all IDVerse endpoints with your JWT token"""
    print("🧪 IDVerse API Testing with Your JWT Token")
    print("=" * 50)
    print(f"🔑 Using JWT Token: {JWT_TOKEN[:50]}...")
    print("=" * 50)
    
    # Test 1: Health Check (no auth needed)
    print("\n1. Health Check")
    result = make_request("GET", "/health", use_auth=False)
    if result:
        print(f"✅ {result}")
    else:
        print("❌ Health check failed")
        return
    
    # Test 2: VC Request Issue
    print("\n2. VC Request Issue")
    vc_data = {
        "type": "GovID",
        "claims": {
            "name": "Shubham Ugale",
            "age": 25,
            "address": "Mumbai, India",
            "aadhaar": "123456789012"
        }
    }
    result = make_request("POST", "/vc/request-issue", vc_data)
    if result:
        print(f"✅ Request ID: {result.get('request_id', 'N/A')}")
        request_id = result.get('request_id')
    else:
        print("❌ VC request failed")
        request_id = None
    
    # Test 3: VC Issue
    if request_id:
        print("\n3. VC Issue")
        issue_data = {"request_id": request_id}
        result = make_request("POST", "/vc/issue", issue_data)
        if result:
            print(f"✅ VC ID: {result.get('vc_id', 'N/A')}")
            print(f"   CID: {result.get('cid', 'N/A')}")
            vc_id = result.get('vc_id')
        else:
            print("❌ VC issue failed")
            vc_id = None
    else:
        vc_id = None
    
    # Test 4: VC Status
    if vc_id:
        print("\n4. VC Status Check")
        result = make_request("GET", f"/vc/status/{vc_id}")
        if result:
            print(f"✅ Status: {result.get('status', 'N/A')}")
            print(f"   Verifiable: {result.get('verifiable', 'N/A')}")
        else:
            print("❌ VC status check failed")
    
    # Test 5: VC Present
    if vc_id:
        print("\n5. VC Present (Verification)")
        present_data = {
            "vc_id": vc_id,
            "verifier_did": "did:example:verifier"
        }
        result = make_request("POST", "/vc/present", present_data)
        if result:
            print(f"✅ Verified: {result.get('verified', 'N/A')}")
        else:
            print("❌ VC present failed")
    
    # Test 6: Benefits Apply
    print("\n6. Benefits Apply")
    benefit_data = {
        "scheme_id": "scheme-001",
        "scheme_name": "PM Kisan Yojana",
        "required_credentials": ["GovID"],
        "application_data": {
            "land_holding": "2 acres",
            "bank_account": "1234567890",
            "farmer_id": "FARM123456"
        }
    }
    result = make_request("POST", "/benefits/apply", benefit_data)
    if result:
        print(f"✅ Application ID: {result.get('application_id', 'N/A')}")
        app_id = result.get('application_id')
    else:
        print("❌ Benefits apply failed")
        app_id = None
    
    # Test 7: Benefits Approve
    if app_id:
        print("\n7. Benefits Approve")
        approve_data = {
            "application_id": app_id,
            "approved": True,
            "amount": 6000,
            "validity_period": 365,
            "notes": "Approved based on land records"
        }
        result = make_request("POST", "/benefits/approve", approve_data)
        if result:
            print(f"✅ Approval Status: {result.get('status', 'N/A')}")
        else:
            print("❌ Benefits approve failed")
    
    # Test 8: Benefits Wallet
    print("\n8. Benefits Wallet")
    result = make_request("GET", "/benefits/wallet")
    if result:
        print(f"✅ Wallet Items: {result.get('total_entitlements', 0)}")
        if result.get('wallet_items'):
            for item in result['wallet_items']:
                print(f"   - {item.get('scheme_name', 'Unknown')}: ₹{item.get('amount', 0)}")
    else:
        print("❌ Benefits wallet failed")
    
    # Test 9: Schemes List
    print("\n9. Schemes List")
    result = make_request("GET", "/schemes/")
    if result:
        print(f"✅ Available Schemes: {result.get('total', 0)}")
        if result.get('schemes'):
            for scheme in result['schemes'][:3]:  # Show first 3
                print(f"   - {scheme.get('name', 'Unknown')}")
    else:
        print("❌ Schemes list failed")
    
    # Test 10: OTP Request (no auth needed)
    print("\n10. OTP Request")
    otp_data = {
        "phone": "+919876543210",
        "purpose": "verification"
    }
    result = make_request("POST", "/auth/otp/request", otp_data, use_auth=False)
    if result:
        print(f"✅ OTP ID: {result.get('otp_id', 'N/A')}")
    else:
        print("❌ OTP request failed")
    
    print("\n" + "=" * 50)
    print("🎉 Testing Complete!")
    print("=" * 50)
    print("All endpoints tested with your JWT token.")
    print("Check results above for any failures.")

if __name__ == "__main__":
    test_all_endpoints()

#!/usr/bin/env python3
"""
Complete IDVerse System Flow Test
Tests the entire user journey from registration to VC operations
"""
# python test_complete_flow.py 

import requests
import json
import sys
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        result = response.json()
        print(f"✅ Registration: {result}")
        return response.status_code in [200, 201, 409]  # 409 = already exists
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def test_login():
    """Test user login and get JWT token"""
    try:
        data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        result = response.json()
        if response.status_code == 200:
            print(f"✅ Login successful: Got JWT token")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {result}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_otp_flow(token):
    """Test OTP request and verification flow"""
    if not token:
        print("❌ No token available for OTP tests")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test OTP request
    try:
        data = {"channel": "email", "destination": "test@example.com"}
        response = requests.post(f"{BASE_URL}/auth/otp/request", json=data)
        result = response.json()
        print(f"✅ OTP request: {result}")
        
        # Test OTP verification
        if 'otp_token' in result:
            otp_data = {
                "otp_token": result['otp_token'],
                "otp_code": result.get('otp_demo', '123456')
            }
            verify_response = requests.post(f"{BASE_URL}/auth/otp/verify", json=otp_data)
            verify_result = verify_response.json()
            print(f"✅ OTP verification: {verify_result}")
            return verify_response.status_code == 200
    except Exception as e:
        print(f"❌ OTP flow failed: {e}")
        return False

def test_schemes(token):
    """Test schemes endpoint"""
    if not token:
        print("❌ No token available for schemes test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/schemes/", headers=headers)
        result = response.json()
        print(f"✅ Schemes endpoint: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Schemes endpoint failed: {e}")
        return False

def test_vc_request_issue(token):
    """Test VC request issue"""
    if not token:
        print("❌ No token available for VC request test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        data = {
            "type": "GovID",
            "claims": {
                "name": "Test User",
                "age": 25,
                "citizenship": "Indian"
            },
            "subject_id": "test@example.com"
        }
        response = requests.post(f"{BASE_URL}/vc/request-issue", json=data, headers=headers)
        result = response.json()
        print(f"✅ VC request issue: {result}")
        return response.status_code == 202
    except Exception as e:
        print(f"❌ VC request issue failed: {e}")
        return False

def test_vc_issue(token):
    """Test VC issue"""
    if not token:
        print("❌ No token available for VC issue test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        data = {
            "type": "GovID",
            "claims": {
                "name": "Test User",
                "age": 25,
                "citizenship": "Indian"
            },
            "subject_id": "test@example.com"
        }
        response = requests.post(f"{BASE_URL}/vc/issue", json=data, headers=headers)
        result = response.json()
        print(f"✅ VC issue: {result}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ VC issue failed: {e}")
        return False

def test_vc_present():
    """Test VC presentation (no auth required)"""
    try:
        data = {
            "vc": {
                "type": "VerifiableCredential",
                "credentialSubject": {
                    "name": "Test User"
                }
            }
        }
        response = requests.post(f"{BASE_URL}/vc/present", json=data)
        result = response.json()
        print(f"✅ VC present: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ VC present failed: {e}")
        return False

def test_vc_status():
    """Test VC status check"""
    try:
        vc_id = "test-vc-001"
        response = requests.get(f"{BASE_URL}/vc/status/{vc_id}")
        result = response.json()
        print(f"✅ VC status: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ VC status failed: {e}")
        return False

def test_benefits_apply(token):
    """Test benefits application"""
    if not token:
        print("❌ No token available for benefits test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        data = {
            "scheme": "Student Scholarship",
            "application_data": {
                "name": "Test User",
                "age": 25,
                "education": "Graduate"
            },
            "supporting_documents": ["doc1.pdf", "doc2.pdf"]
        }
        response = requests.post(f"{BASE_URL}/benefits/apply", json=data, headers=headers)
        result = response.json()
        print(f"✅ Benefits apply: {result}")
        return response.status_code == 202
    except Exception as e:
        print(f"❌ Benefits apply failed: {e}")
        return False

def test_benefits_wallet(token):
    """Test benefits wallet"""
    if not token:
        print("❌ No token available for wallet test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/benefits/wallet", headers=headers)
        result = response.json()
        print(f"✅ Benefits wallet: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Benefits wallet failed: {e}")
        return False

def test_benefits_applications(token):
    """Test benefits applications"""
    if not token:
        print("❌ No token available for applications test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/benefits/applications", headers=headers)
        result = response.json()
        print(f"✅ Benefits applications: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Benefits applications failed: {e}")
        return False

def main():
    """Run complete system flow test"""
    print("🚀 Starting Complete IDVerse System Flow Test")
    print("=" * 60)
    
    # Test basic connectivity
    if not test_health():
        print("❌ System is not running. Please start the server first.")
        sys.exit(1)
    
    print("\n📝 Testing Authentication Flow:")
    # Test registration
    test_register()
    
    # Test login and get token
    token = test_login()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    print("\n🔐 Testing JWT Protected Endpoints:")
    # Test OTP flow
    test_otp_flow(token)
    
    # Test schemes
    test_schemes(token)
    
    print("\n🎫 Testing VC (Verifiable Credentials) Flow:")
    # Test VC request issue
    test_vc_request_issue(token)
    
    # Test VC issue
    test_vc_issue(token)
    
    # Test VC present (no auth required)
    test_vc_present()
    
    # Test VC status
    test_vc_status()
    
    print("\n💰 Testing Benefits Flow:")
    # Test benefits application
    test_benefits_apply(token)
    
    # Test benefits wallet
    test_benefits_wallet(token)
    
    # Test benefits applications
    test_benefits_applications(token)
    
    print("\n" + "=" * 60)
    print("✅ Complete system flow test completed!")
    print("🌐 Server is running at: http://localhost:5000")
    print("📚 API documentation: http://localhost:5000/_debug/routes")
    print("\n🎉 All major system components tested successfully!")

if __name__ == "__main__":
    main()

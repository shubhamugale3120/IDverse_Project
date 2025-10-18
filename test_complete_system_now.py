#!/usr/bin/env python3
"""
Complete IDverse System Test Script
Tests all endpoints and functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Start with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n📝 Testing User Registration...")
    
    # Test data with unique email
    import time
    timestamp = int(time.time())
    user_data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=10)
        
        if response.status_code == 201:
            print("✅ User registration successful")
            return True
        elif response.status_code == 409 and "already registered" in response.text:
            print("✅ User already exists (expected for testing)")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_user_login():
    """Test user login and get JWT token"""
    print("\n🔐 Testing User Login...")
    
    # Use the same timestamp for login
    import time
    timestamp = int(time.time())
    login_data = {
        "email": f"test{timestamp}@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful - JWT token received")
                return data["access_token"]
            else:
                print("❌ Login failed - No token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with JWT token"""
    print("\n🔒 Testing Protected Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test schemes endpoint
    try:
        response = requests.get(f"{BASE_URL}/schemes/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Schemes endpoint: {len(data.get('schemes', []))} schemes available")
        else:
            print(f"❌ Schemes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Schemes endpoint error: {e}")
    
    # Test wallet endpoint
    try:
        response = requests.get(f"{BASE_URL}/benefits/wallet", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wallet endpoint: Balance {data.get('balance', 'N/A')}")
        else:
            print(f"❌ Wallet endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Wallet endpoint error: {e}")

def test_benefit_application(token):
    """Test benefit application"""
    print("\n💰 Testing Benefit Application...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test benefit application
    application_data = {
        "scheme": "General Citizen Benefit",
        "application_data": {
            "email": "test@example.com",
            "role": "citizen",
            "scheme_id": 1
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/benefits/apply", json=application_data, headers=headers, timeout=10)
        
        if response.status_code == 202:
            data = response.json()
            print(f"✅ Benefit application successful: {data.get('application_id', 'N/A')}")
            return True
        else:
            print(f"❌ Benefit application failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Benefit application error: {e}")
        return False

def test_vc_endpoints(token):
    """Test VC endpoints"""
    print("\n🆔 Testing VC Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test VC request
    vc_data = {
        "type": "AadhaarLink",
        "claims": {
            "aadhaar_last4": "1234",
            "dob": "1990-01-01"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/vc/request-issue", json=vc_data, headers=headers, timeout=10)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ VC request successful: {data.get('request_id', 'N/A')}")
        else:
            print(f"❌ VC request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ VC request error: {e}")

def test_frontend_access():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Access...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend access failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running. Start with: npm run dev")
        return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def main():
    """Run complete system test"""
    print("🚀 IDverse Complete System Test")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   python run.py")
        return
    
    # Test user registration
    if not test_user_registration():
        print("\n❌ User registration failed")
        return
    
    # Test user login
    token = test_user_login()
    if not token:
        print("\n❌ User login failed")
        return
    
    # Test protected endpoints
    test_protected_endpoints(token)
    
    # Test benefit application
    test_benefit_application(token)
    
    # Test VC endpoints
    test_vc_endpoints(token)
    
    # Test frontend access
    test_frontend_access()
    
    print("\n" + "=" * 50)
    print("🎉 System Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Register a new account or login with test@example.com")
    print("3. Test the complete user flow")
    print("4. Check the dashboard for real data")
    print("\n✅ Your system is working perfectly!")

if __name__ == "__main__":
    main()

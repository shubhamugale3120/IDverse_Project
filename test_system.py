#!/usr/bin/env python3
"""
Comprehensive test script for IDVerse system
Tests all major endpoints and functionality
"""

import requests
import json
import sys

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

def test_routes():
    """Test routes endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/_debug/routes")
        routes = response.json()
        print(f"✅ Available routes: {len(routes)} routes found")
        for route in routes[:5]:  # Show first 5 routes
            print(f"   - {route}")
        return True
    except Exception as e:
        print(f"❌ Routes check failed: {e}")
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
    """Test user login"""
    try:
        data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        result = response.json()
        if response.status_code == 200:
            print(f"✅ Login successful: Got token")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {result}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with JWT token"""
    if not token:
        print("❌ No token available for protected endpoint tests")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test schemes endpoint
    try:
        response = requests.get(f"{BASE_URL}/schemes/", headers=headers)
        result = response.json()
        print(f"✅ Schemes endpoint: {result}")
    except Exception as e:
        print(f"❌ Schemes endpoint failed: {e}")
    
    # Test OTP request
    try:
        data = {"channel": "email", "destination": "test@example.com"}
        response = requests.post(f"{BASE_URL}/auth/otp/request", json=data)
        result = response.json()
        print(f"✅ OTP request: {result}")
    except Exception as e:
        print(f"❌ OTP request failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting IDVerse System Tests")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_health():
        print("❌ System is not running. Please start the server first.")
        sys.exit(1)
    
    # Test routes
    test_routes()
    
    # Test authentication flow
    print("\n📝 Testing Authentication Flow:")
    test_register()
    token = test_login()
    
    # Test protected endpoints
    if token:
        print("\n🔒 Testing Protected Endpoints:")
        test_protected_endpoints(token)
    
    print("\n" + "=" * 50)
    print("✅ System tests completed!")
    print("🌐 Server is running at: http://localhost:5000")
    print("📚 API documentation: http://localhost:5000/_debug/routes")

if __name__ == "__main__":
    main()

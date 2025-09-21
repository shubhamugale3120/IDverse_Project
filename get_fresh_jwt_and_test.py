#!/usr/bin/env python3
"""
Get fresh JWT token and test the system
This script will register/login to get a fresh JWT token and then test all endpoints
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment variables for in-memory database
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

BASE_URL = "http://127.0.0.1:5000"

def start_server():
    """Start the Flask server in background"""
    print("🚀 Starting IDVerse server...")
    
    try:
        from backend import create_app
        app = create_app()
        
        print("✅ Server started successfully!")
        print("🌐 Server running on http://127.0.0.1:5000")
        
        # Start server in background
        import threading
        server_thread = threading.Thread(
            target=lambda: app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        import time
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 Testing: {method} {endpoint}")
    if description:
        print(f"   Description: {description}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers or {}, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers or {}, timeout=5)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False, None
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Success!")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
                return True, result
            except:
                print(f"   Response: {response.text}")
                return True, response.text
        else:
            print(f"   ❌ Error!")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Make sure the server is running on {BASE_URL}")
        return False, None
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False, None

def get_fresh_jwt_token():
    """Get a fresh JWT token by registering and logging in"""
    print("\n🔑 Getting fresh JWT token...")
    
    # Test data
    test_user = {
        "name": "Shubham Ugale",
        "email": "shubham.ugale@example.com",
        "password": "testpassword123"
    }
    
    # Step 1: Register user
    print("\n📝 Step 1: Registering user...")
    success, result = test_endpoint("POST", "/auth/register", test_user, 
                                   description="Register new user")
    
    if not success:
        print("   ⚠️  Registration failed, trying login...")
    
    # Step 2: Login to get JWT token
    print("\n🔐 Step 2: Logging in to get JWT token...")
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    success, result = test_endpoint("POST", "/auth/login", login_data,
                                   description="Login to get JWT token")
    
    if success and result and "access_token" in result:
        jwt_token = result["access_token"]
        print(f"   ✅ JWT token obtained: {jwt_token[:50]}...")
        return jwt_token
    else:
        print("   ❌ Failed to get JWT token")
        return None

def test_all_endpoints(jwt_token):
    """Test all endpoints with the JWT token"""
    print(f"\n🧪 Testing all endpoints with JWT token...")
    
    auth_headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Test endpoints
    endpoints = [
        # Health check
        ("GET", "/", None, None, "Health check"),
        
        # OTP endpoints
        ("POST", "/otp/request", {"phone": "+919876543210"}, None, "Request OTP"),
        ("POST", "/otp/verify", {"phone": "+919876543210", "otp": "123456"}, None, "Verify OTP"),
        
        # VC endpoints
        ("POST", "/vc/request-issue", {
            "type": "GovID",
            "claims": {"name": "Shubham Ugale", "age": 25},
            "subject_id": "shubham.ugale@example.com"
        }, auth_headers, "Request VC issuance"),
        
        ("POST", "/vc/issue", {
            "type": "GovID",
            "subject_id": "shubham.ugale@example.com",
            "claims": {"name": "Shubham Ugale", "age": 25}
        }, auth_headers, "Issue VC"),
        
        # Benefits endpoints
        ("POST", "/benefits/apply", {
            "benefit_type": "RationCard",
            "personal_info": {"name": "Shubham Ugale", "age": 25, "income": 50000}
        }, auth_headers, "Apply for benefit"),
        
        ("GET", "/benefits/applications", None, auth_headers, "Get user applications"),
        ("GET", "/benefits/wallet", None, auth_headers, "Get user wallet"),
    ]
    
    results = []
    for method, endpoint, data, headers, description in endpoints:
        success, result = test_endpoint(method, endpoint, data, headers, description)
        results.append((endpoint, success))
    
    return results

def main():
    """Main function"""
    print("🚀 IDVerse Complete System Test with Fresh JWT")
    print("=" * 60)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Start server
    if not start_server():
        print("❌ Cannot proceed without server")
        return 1
    
    # Step 2: Get fresh JWT token
    jwt_token = get_fresh_jwt_token()
    if not jwt_token:
        print("❌ Cannot proceed without JWT token")
        return 1
    
    # Step 3: Test all endpoints
    results = test_all_endpoints(jwt_token)
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"   Total endpoints tested: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success rate: {(passed/total)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {endpoint}: {status}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")
    
    print(f"\n🔑 Your fresh JWT token: {jwt_token}")
    print("💡 You can use this token in Postman or other API clients")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

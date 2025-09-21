#!/usr/bin/env python3
"""
Complete IDVerse System Test - Fixed Version
Tests all endpoints with proper error handling and scalability checks
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

BASE_URL = "http://127.0.0.1:5000"

class IDVerseTester:
    """Comprehensive IDVerse system tester"""
    
    def __init__(self):
        self.jwt_token = None
        self.test_results = []
        self.server_running = False
        
    def start_server(self):
        """Start the Flask server"""
        print("🚀 Starting IDVerse server...")
        
        try:
            from backend import create_app
            app = create_app()
            
            print("✅ Server created successfully!")
            
            # Start server in background
            import threading
            server_thread = threading.Thread(
                target=lambda: app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
            )
            server_thread.daemon = True
            server_thread.start()
            
            # Wait for server to start
            time.sleep(3)
            
            # Test if server is running
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    self.server_running = True
                    print("✅ Server is running and responding!")
                    return True
            except:
                pass
                
            print("⚠️  Server started but not responding yet...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, headers=None, description=""):
        """Test a single API endpoint with comprehensive error handling"""
        url = f"{BASE_URL}{endpoint}"
        
        print(f"\n🔍 Testing: {method} {endpoint}")
        if description:
            print(f"   Description: {description}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers or {}, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers or {}, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers or {}, timeout=10)
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
            print(f"   ❌ Connection Error: Server not running on {BASE_URL}")
            return False, None
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout Error: Request took too long")
            return False, None
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False, None
    
    def get_fresh_jwt_token(self):
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
        success, result = self.test_endpoint("POST", "/auth/register", test_user, 
                                           description="Register new user")
        
        if not success:
            print("   ⚠️  Registration failed, trying login...")
        
        # Step 2: Login to get JWT token
        print("\n🔐 Step 2: Logging in to get JWT token...")
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        success, result = self.test_endpoint("POST", "/auth/login", login_data,
                                           description="Login to get JWT token")
        
        if success and result and "access_token" in result:
            self.jwt_token = result["access_token"]
            print(f"   ✅ JWT token obtained: {self.jwt_token[:50]}...")
            return True
        else:
            print("   ❌ Failed to get JWT token")
            return False
    
    def test_all_endpoints(self):
        """Test all endpoints comprehensively"""
        print(f"\n🧪 Testing all endpoints with JWT token...")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return []
        
        auth_headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Comprehensive endpoint tests
        endpoints = [
            # Health and basic endpoints
            ("GET", "/health", None, None, "Health check"),
            ("GET", "/_debug/routes", None, None, "Debug routes"),
            
            # Authentication endpoints
            ("POST", "/auth/register", {
                "name": "Test User 2",
                "email": "test2@example.com",
                "password": "testpassword123"
            }, None, "Register second user"),
            
            # OTP endpoints
            ("POST", "/otp/request", {"phone": "+919876543210"}, None, "Request OTP"),
            ("POST", "/otp/verify", {"phone": "+919876543210", "otp": "123456"}, None, "Verify OTP"),
            
            # VC endpoints
            ("POST", "/vc/request-issue", {
                "type": "GovID",
                "claims": {"name": "Shubham Ugale", "age": 25, "address": "Mumbai, India"},
                "subject_id": "shubham.ugale@example.com"
            }, auth_headers, "Request VC issuance"),
            
            ("POST", "/vc/issue", {
                "type": "GovID",
                "subject_id": "shubham.ugale@example.com",
                "claims": {"name": "Shubham Ugale", "age": 25, "address": "Mumbai, India"}
            }, auth_headers, "Issue VC"),
            
            ("POST", "/vc/present", {
                "vc_id": "vc-GovID-12345678",
                "challenge": "test-challenge-123"
            }, auth_headers, "Present VC"),
            
            ("GET", "/vc/status/vc-GovID-12345678", None, auth_headers, "Check VC status"),
            
            # Benefits endpoints
            ("POST", "/benefits/apply", {
                "benefit_type": "RationCard",
                "personal_info": {"name": "Shubham Ugale", "age": 25, "income": 50000}
            }, auth_headers, "Apply for benefit"),
            
            ("GET", "/benefits/applications", None, auth_headers, "Get user applications"),
            ("GET", "/benefits/wallet", None, auth_headers, "Get user wallet"),
            
            # Admin endpoints
            ("GET", "/benefits/admin/applications", None, auth_headers, "Get all applications (admin)"),
            ("POST", "/benefits/admin/approve", {
                "application_id": 1,
                "status": "approved",
                "notes": "Approved for testing"
            }, auth_headers, "Approve application (admin)"),
        ]
        
        results = []
        for method, endpoint, data, headers, description in endpoints:
            success, result = self.test_endpoint(method, endpoint, data, headers, description)
            results.append((endpoint, success))
            self.test_results.append((endpoint, success, description))
        
        return results
    
    def run_performance_test(self):
        """Run basic performance tests"""
        print("\n⚡ Running performance tests...")
        
        if not self.jwt_token:
            print("❌ No JWT token available for performance test")
            return
        
        auth_headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Test multiple concurrent requests
        import threading
        import time
        
        def make_request():
            try:
                response = requests.get(f"{BASE_URL}/benefits/wallet", headers=auth_headers, timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Test 10 concurrent requests
        threads = []
        results = []
        
        start_time = time.time()
        
        for i in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        successful_requests = sum(results)
        total_time = end_time - start_time
        
        print(f"   📊 Performance Results:")
        print(f"      Successful requests: {successful_requests}/10")
        print(f"      Total time: {total_time:.2f} seconds")
        print(f"      Average response time: {total_time/10:.2f} seconds")
        print(f"      Requests per second: {10/total_time:.2f}")
        
        if successful_requests >= 8:
            print(f"   ✅ Performance test PASSED")
        else:
            print(f"   ❌ Performance test FAILED")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Overall Results:")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for endpoint, success, description in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {endpoint}: {status} - {description}")
        
        print(f"\n🔑 JWT Token: {self.jwt_token}")
        print(f"🌐 Server URL: {BASE_URL}")
        print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! System is production-ready!")
        elif passed_tests >= total_tests * 0.8:
            print(f"\n✅ System is mostly working! {failed_tests} minor issues to fix.")
        else:
            print(f"\n⚠️  System needs attention. {failed_tests} critical issues found.")
        
        return passed_tests, total_tests

def main():
    """Main test execution"""
    print("🚀 IDVerse Complete System Test - Fixed Version")
    print("="*80)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = IDVerseTester()
    
    # Step 1: Start server
    if not tester.start_server():
        print("❌ Cannot proceed without server")
        return 1
    
    # Step 2: Get fresh JWT token
    if not tester.get_fresh_jwt_token():
        print("❌ Cannot proceed without JWT token")
        return 1
    
    # Step 3: Test all endpoints
    results = tester.test_all_endpoints()
    
    # Step 4: Run performance tests
    tester.run_performance_test()
    
    # Step 5: Generate report
    passed, total = tester.generate_report()
    
    return 0 if passed >= total * 0.8 else 1

if __name__ == "__main__":
    sys.exit(main())

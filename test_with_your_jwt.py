#!/usr/bin/env python3
"""
Test IDVerse API with your JWT token
This script tests all endpoints using your provided JWT token
"""

import requests
import os
import json
import sys
from datetime import datetime

# Your JWT token from yesterday
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1ODQ0MTk3NiwianRpIjoiZTg2YjVmN2YtYTNmMy00NDAzLTk2ZjAtZWEyYTlhMzg5NDVkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InNodWJoYW0udWdhbGVAZXhhbXBsZS5jb20iLCJuYmYiOjE3NTg0NDE5NzYsImNzcmYiOiI1M2YxMzU1Ni0xYmJhLTQ4YTYtYmJhYi0yYTkwMzJjNmQ1NDkiLCJleHAiOjE3NTg0NDI4NzZ9.woBddKQRwF1ef0OgdL8N1eiMDM9A9sdG6fVJx9E-uas"

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000"

# Headers with JWT token for protected endpoints
AUTH_HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 Testing: {method} {endpoint}")
    if description:
        print(f"   Description: {description}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers or {})
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers or {})
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers or {})
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Success!")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response: {response.text}")
        else:
            print(f"   ❌ Error!")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Error: {response.text}")
                
        return response.status_code < 400
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Make sure the server is running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🚀 IDVerse API Testing with Your JWT Token")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Using JWT Token: {JWT_TOKEN[:50]}...")
    
    # Test 1: Health Check (No Auth Required)
    print_section("HEALTH CHECK")
    test_endpoint("GET", "/", description="Basic health check")
    
    # Test 2: Authentication Endpoints (No Auth Required)
    print_section("AUTHENTICATION ENDPOINTS")
    test_endpoint("POST", "/auth/register", {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }, description="User registration")
    
    test_endpoint("POST", "/auth/login", {
        "email": "test@example.com", 
        "password": "testpassword123"
    }, description="User login")
    
    # Test 3: OTP Endpoints (No Auth Required)
    print_section("OTP ENDPOINTS")
    test_endpoint("POST", "/otp/request", {
        "phone": "+919876543210"
    }, description="Request OTP")
    
    test_endpoint("POST", "/otp/verify", {
        "phone": "+919876543210",
        "otp": "123456"
    }, description="Verify OTP")
    
    # Test 4: VC Endpoints (Auth Required)
    print_section("VERIFIABLE CREDENTIAL ENDPOINTS")
    test_endpoint("POST", "/vc/request-issue", {
        "type": "GovID",
        "claims": {
            "name": "Shubham Ugale",
            "age": 25,
            "address": "Mumbai, India"
        },
        "subject_id": "shubham.ugale@example.com"
    }, AUTH_HEADERS, description="Request VC issuance")
    
    test_endpoint("POST", "/vc/issue", {
        "type": "GovID",
        "subject_id": "shubham.ugale@example.com",
        "claims": {
            "name": "Shubham Ugale",
            "age": 25,
            "address": "Mumbai, India"
        }
    }, AUTH_HEADERS, description="Issue VC")
    
    test_endpoint("POST", "/vc/present", {
        "vc_id": "vc-GovID-12345678",
        "challenge": "test-challenge-123"
    }, AUTH_HEADERS, description="Present VC")
    
    test_endpoint("GET", "/vc/status/vc-GovID-12345678", headers=AUTH_HEADERS, description="Check VC status")
    
    # Test 5: Benefits Endpoints (Auth Required)
    print_section("BENEFITS ENDPOINTS")
    test_endpoint("POST", "/benefits/apply", {
        "benefit_type": "RationCard",
        "personal_info": {
            "name": "Shubham Ugale",
            "age": 25,
            "income": 50000
        }
    }, AUTH_HEADERS, description="Apply for benefit")
    
    test_endpoint("GET", "/benefits/applications", headers=AUTH_HEADERS, description="Get user applications")
    
    test_endpoint("GET", "/benefits/wallet", headers=AUTH_HEADERS, description="Get user wallet")
    
    # Test 6: Admin Endpoints (Auth Required)
    print_section("ADMIN ENDPOINTS")
    test_endpoint("GET", "/benefits/admin/applications", headers=AUTH_HEADERS, description="Get all applications (admin)")
    
    test_endpoint("POST", "/benefits/admin/approve", {
        "application_id": 1,
        "status": "approved",
        "notes": "Approved for testing"
    }, AUTH_HEADERS, description="Approve application (admin)")
    
    print_section("TEST COMPLETED")
    print("🎉 All tests completed!")
    print("📝 Check the results above to see which endpoints are working")
    print("💡 If you see connection errors, make sure the server is running with: python run.py")

if __name__ == "__main__":
    main()
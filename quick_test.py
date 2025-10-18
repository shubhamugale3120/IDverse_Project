#!/usr/bin/env python3
"""
Quick test to verify system is working
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_system():
    print("🚀 Quick IDverse System Test")
    print("=" * 40)
    
    # Test 1: Backend Health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        print("Start backend with: python run.py")
        return
    
    # Test 2: Schemes endpoint (requires auth - will test after login)
    
    # Test 3: Try to register a new user
    try:
        user_data = {
            "username": "demouser",
            "email": "demo@example.com", 
            "password": "demo123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=5)
        if response.status_code == 201:
            print("✅ User registration successful")
        elif response.status_code == 409:
            print("✅ User already exists (expected)")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 4: Try to login
    try:
        login_data = {
            "email": "demo@example.com",
            "password": "demo123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful - JWT token received")
                token = data["access_token"]
                
                # Test 5: Test protected endpoints
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test wallet endpoint
                response = requests.get(f"{BASE_URL}/benefits/wallet", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Wallet endpoint: Balance {data.get('balance', 'N/A')}")
                else:
                    print(f"❌ Wallet endpoint failed: {response.status_code}")
                
                # Test schemes endpoint
                response = requests.get(f"{BASE_URL}/schemes/", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    schemes = data.get('schemes', [])
                    print(f"✅ Schemes endpoint: {len(schemes)} schemes available")
                    if schemes:
                        print(f"   - {schemes[0]['name']} (Score: {schemes[0]['score']})")
                else:
                    print(f"❌ Schemes endpoint failed: {response.status_code}")
            else:
                print("❌ No token in login response")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Quick test complete!")
    print("\n📋 Next steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Register a new account")
    print("3. Login and test the dashboard")
    print("4. Try applying for benefits")

if __name__ == "__main__":
    test_system()

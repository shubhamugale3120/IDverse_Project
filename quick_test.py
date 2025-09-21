#!/usr/bin/env python3
"""
Quick test script to verify JWT token and system components
This script tests the system without requiring a running server
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from backend import create_app
        print("✅ Backend import successful")
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False
    
    try:
        from backend.model import User, VCRequest, VerifiableCredential
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from backend.services.ipfs_service import get_ipfs_service
        from backend.services.signing_service import get_signing_service
        from backend.services.registry_service import get_registry_service
        print("✅ Services import successful")
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        return False
    
    return True

def test_jwt_token():
    """Test JWT token validity"""
    print("\n🔍 Testing JWT token...")
    
    # Your JWT token
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1ODM1OTc3OSwianRpIjoiZTI5ZDAzNjItMTRiMC00YWZhLWFjZGQtMGMzMjUxYzk2ODIzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3RAZXhhbXBsZS5jb20iLCJuYmYiOjE3NTgzNTk3NzksImNzcmYiOiIyNWE2Mjc3ZS0xM2MyLTRjNjAtYTk3ZS1mOGQyOGEwMWIwZDEiLCJleHAiOjE3NTgzNjA2Nzl9.ah3Z8525QSMwzlJ7M3Rxi8qmYdvzjbW1f7-lBTeJLW4"
    
    try:
        import jwt
        from datetime import datetime
        
        # Decode without verification to check structure
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        
        print(f"✅ JWT token structure valid")
        print(f"   Subject: {decoded.get('sub', 'N/A')}")
        print(f"   Issued at: {datetime.fromtimestamp(decoded.get('iat', 0))}")
        print(f"   Expires at: {datetime.fromtimestamp(decoded.get('exp', 0))}")
        
        # Check if expired
        exp_time = decoded.get('exp', 0)
        current_time = datetime.now().timestamp()
        
        if exp_time < current_time:
            print(f"⚠️  JWT token is EXPIRED!")
            print(f"   Expired: {datetime.fromtimestamp(exp_time)}")
            print(f"   Current: {datetime.fromtimestamp(current_time)}")
            return False
        else:
            print(f"✅ JWT token is VALID (not expired)")
            return True
            
    except Exception as e:
        print(f"❌ JWT token test failed: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        # Set environment variables
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = 'True'
        
        from backend import create_app
        app = create_app()
        
        print("✅ Flask app created successfully")
        print(f"   App name: {app.name}")
        print(f"   Debug mode: {app.debug}")
        
        # Test routes
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.methods} {rule.rule}")
            
            print(f"   Available routes: {len(routes)}")
            for route in routes[:5]:  # Show first 5 routes
                print(f"     {route}")
            if len(routes) > 5:
                print(f"     ... and {len(routes) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 IDVerse Quick System Test")
    print("=" * 50)
    
    # Test 1: Imports
    imports_ok = test_imports()
    
    # Test 2: JWT Token
    jwt_ok = test_jwt_token()
    
    # Test 3: App Creation
    app_ok = test_app_creation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   JWT Token: {'✅ PASS' if jwt_ok else '❌ FAIL'}")
    print(f"   App Creation: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if all([imports_ok, jwt_ok, app_ok]):
        print("\n🎉 All tests passed! System is ready.")
        print("💡 Next step: Start the server with: python run.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        
        if not jwt_ok:
            print("🔑 JWT Token Issue: Your token may be expired.")
            print("   Solution: Get a fresh token by logging in again.")
        
        if not app_ok:
            print("🔧 App Creation Issue: Check database configuration.")
            print("   Solution: Verify .env file and database permissions.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple test script to verify OAuth2 endpoints
Run this after setting up your .env file with Google OAuth2 credentials
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("backend/.env")

BASE_URL = "http://localhost:8000"


def test_auth_endpoints():
    """Test the authentication endpoints"""

    print("🧪 Testing OAuth2 Authentication Endpoints")
    print("=" * 50)

    # Test 1: Get authorization URL
    print("\n1. Testing /api/auth/login endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Authorization URL generated:")
            print(f"   URL: {data.get('auth_url', 'Not found')[:100]}...")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Test protected endpoint without auth
    print("\n2. Testing protected endpoint without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me")
        if response.status_code == 401:
            print("✅ Success! Endpoint correctly requires authentication")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Test dashboard endpoint without auth
    print("\n3. Testing dashboard endpoint without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard")
        if response.status_code == 401:
            print("✅ Success! Dashboard endpoint correctly requires authentication")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4: Test with invalid token
    print("\n4. Testing with invalid JWT token...")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 401:
            print("✅ Success! Invalid token correctly rejected")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


def check_environment():
    """Check if environment variables are set"""
    print("\n🔧 Environment Check")
    print("=" * 30)

    required_vars = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "JWT_SECRET_KEY"]

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (set)")
        else:
            print(f"❌ {var}: Not set")


def main():
    print("🚀 WatchLog Insights OAuth2 Test")
    print("=" * 40)

    # Check environment
    check_environment()

    # Test endpoints
    test_auth_endpoints()

    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Make sure your backend server is running: python backend/main.py")
    print("2. Set up your Google OAuth2 credentials in backend/.env")
    print("3. Test the full OAuth flow by visiting http://localhost:3000")
    print("4. Check the OAUTH_SETUP.md file for detailed instructions")


if __name__ == "__main__":
    main()

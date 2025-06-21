#!/usr/bin/env python3
"""
Test script for admin functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_admin_login():
    """Test admin login with special PIN"""
    print("Testing admin login...")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json={"pin": "cardsagainsthumanity"})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('user', {}).get('is_admin'):
            print("✅ Admin login successful!")
            print(f"Admin user: {data['user']}")
            return True
        else:
            print("❌ Admin login failed - not marked as admin")
            return False
    else:
        print(f"❌ Admin login failed - HTTP {response.status_code}")
        print(response.text)
        return False

def test_admin_endpoints():
    """Test admin endpoints"""
    print("\nTesting admin endpoints...")
    
    # Test get users
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Get users successful - {len(users)} users found")
    else:
        print(f"❌ Get users failed - HTTP {response.status_code}")
    
    # Test get boards
    response = requests.get(f"{BASE_URL}/api/admin/boards")
    if response.status_code == 200:
        boards = response.json()
        print(f"✅ Get boards successful - {len(boards)} boards found")
    else:
        print(f"❌ Get boards failed - HTTP {response.status_code}")

def test_regular_login():
    """Test that regular login still works"""
    print("\nTesting regular login...")
    
    # Try with a non-existent PIN
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json={"pin": "testpin123"})
    
    if response.status_code == 401:
        print("✅ Regular login correctly rejects invalid PIN")
        return True
    else:
        print(f"❌ Regular login unexpected response - HTTP {response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Admin Panel Implementation")
    print("=" * 50)
    
    success = True
    
    success &= test_admin_login()
    success &= test_regular_login()
    test_admin_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")

#!/usr/bin/env python3
"""
Test script to verify display name uniqueness enforcement.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User

def test_display_name_uniqueness():
    print("Testing display name uniqueness enforcement...")
    
    # Try to create another user with the same display name
    print("\nAttempting to create user with display name 'Mayjay' (should fail)...")
    user = User.create("5678", "Mayjay")
    
    if user is None:
        print("✓ Display name uniqueness enforced correctly - creation failed as expected")
        return True
    else:
        print("✗ Display name uniqueness NOT enforced - creation succeeded when it should have failed")
        print(f"Created user: {user}")
        return False

def test_case_sensitivity():
    print("\nTesting case sensitivity...")
    
    # Try different cases
    test_cases = ["mayjay", "MAYJAY", "MayJay"]
    
    for case in test_cases:
        print(f"Attempting to create user with display name '{case}'...")
        user = User.create(f"test_{case}", case)
        
        if user is None:
            print(f"✓ Case variation '{case}' was rejected (good if case-insensitive)")
        else:
            print(f"✗ Case variation '{case}' was accepted")
            # Clean up
            print(f"Created user: {user}")

def test_new_unique_name():
    print("\nTesting creation with unique display name...")
    
    user = User.create("9999", "TestUser")
    if user:
        print(f"✓ Successfully created user with unique name: {user['display_name']}")
        return True
    else:
        print("✗ Failed to create user with unique name")
        return False

def main():
    print("=== Display Name Uniqueness Tests ===")
    
    success = True
    
    # Test 1: Try to create duplicate display name
    if not test_display_name_uniqueness():
        success = False
    
    # Test 2: Test case sensitivity
    test_case_sensitivity()
    
    # Test 3: Test creating with unique name
    if not test_new_unique_name():
        success = False
    
    print("\n=== Test Results ===")
    if success:
        print("✓ All critical tests passed!")
    else:
        print("✗ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

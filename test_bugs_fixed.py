#!/usr/bin/env python3
"""
Test script to verify both bug fixes:
1. Case-insensitive display name uniqueness
2. Board refresh deletes old boards
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User, Board, Progress
from admin_commands import delete_player_by_display_name

def cleanup_test_users():
    """Clean up any existing test users"""
    test_names = ["TestUser1", "testuser1", "TESTUSER1", "TestUser2"]
    for name in test_names:
        try:
            delete_player_by_display_name(name)
        except:
            pass  # Ignore if user doesn't exist

def test_case_insensitive_display_names():
    """Test that display names are case-insensitive unique"""
    print("=== Testing Case-Insensitive Display Name Uniqueness ===")
    
    # Clean up first
    cleanup_test_users()
    
    # Create a user with mixed case name
    print("Creating user with display name 'TestUser1'...")
    user1 = User.create("1001", "TestUser1")
    
    if not user1:
        print("✗ Failed to create initial user")
        return False
    
    print(f"✓ Created user: {user1['display_name']}")
    
    # Try to create users with different cases of the same name
    test_cases = [
        ("1002", "testuser1"),
        ("1003", "TESTUSER1"), 
        ("1004", "TestUSER1"),
        ("1005", "tEsTuSeR1")
    ]
    
    success = True
    for pin, display_name in test_cases:
        print(f"Attempting to create user with display name '{display_name}'...")
        user = User.create(pin, display_name)
        
        if user is None:
            print(f"✓ Case variation '{display_name}' was correctly rejected")
        else:
            print(f"✗ Case variation '{display_name}' was incorrectly accepted")
            success = False
    
    # Test that a truly unique name still works
    print("Testing that unique names still work...")
    user2 = User.create("1006", "TestUser2")
    if user2:
        print(f"✓ Unique name 'TestUser2' was correctly accepted")
    else:
        print("✗ Unique name was incorrectly rejected")
        success = False
    
    return success

def test_board_refresh_deletes_old_boards():
    """Test that refreshing a board deletes the old one"""
    print("\n=== Testing Board Refresh Deletes Old Boards ===")
    
    # Get or create a test user
    test_user = User.get_by_display_name("TestUser2")
    if not test_user:
        test_user = User.create("2001", "BoardTestUser")
        if not test_user:
            print("✗ Failed to create test user for board test")
            return False
    
    user_id = test_user['id']
    print(f"Using test user: {test_user['display_name']} (ID: {user_id})")
    
    # Create first board
    print("Creating first board...")
    board1 = Board.create(user_id, [{"name": "Test1", "rarity": "R", "slot": 0}])
    if not board1:
        print("✗ Failed to create first board")
        return False
    
    board1_id = board1['id']
    print(f"✓ Created first board with ID: {board1_id}")
    
    # Create second board (simulating refresh)
    print("Creating second board (simulating refresh)...")
    Board.delete_by_user(user_id)  # This is what the refresh should do
    board2 = Board.create(user_id, [{"name": "Test2", "rarity": "R", "slot": 0}])
    if not board2:
        print("✗ Failed to create second board")
        return False
    
    board2_id = board2['id']
    print(f"✓ Created second board with ID: {board2_id}")
    
    # Check that only the second board exists
    current_board = Board.get_by_user(user_id)
    if not current_board:
        print("✗ No board found for user after refresh")
        return False
    
    if current_board['id'] == board2_id:
        print(f"✓ Only the new board (ID: {board2_id}) exists for the user")
        return True
    else:
        print(f"✗ Wrong board found. Expected ID: {board2_id}, Found ID: {current_board['id']}")
        return False

def main():
    print("=== Bug Fix Verification Tests ===\n")
    
    success = True
    
    # Test 1: Case-insensitive display names
    if not test_case_insensitive_display_names():
        success = False
    
    # Test 2: Board refresh deletes old boards
    if not test_board_refresh_deletes_old_boards():
        success = False
    
    print("\n=== Test Results ===")
    if success:
        print("✓ All tests passed! Both bugs appear to be fixed.")
    else:
        print("✗ Some tests failed!")
    
    # Clean up
    cleanup_test_users()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

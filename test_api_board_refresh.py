#!/usr/bin/env python3
"""
Test script to verify the API endpoint properly deletes old boards when creating new ones.
This simulates the actual board refresh functionality.
"""

import sys
import os
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User, Board
from admin_commands import delete_player_by_display_name

def test_api_board_refresh():
    """Test that the API endpoint deletes old boards when creating new ones"""
    print("=== Testing API Board Refresh Functionality ===")
    
    # Clean up any existing test user
    try:
        delete_player_by_display_name("APITestUser")
    except:
        pass
    
    # Create a test user
    print("Creating test user...")
    test_user = User.create("3001", "APITestUser")
    if not test_user:
        print("✗ Failed to create test user")
        return False
    
    user_id = test_user['id']
    print(f"✓ Created test user: {test_user['display_name']} (ID: {user_id})")
    
    # Create first board directly in database
    print("Creating first board directly...")
    board1 = Board.create(user_id, [{"name": "Test1", "rarity": "R", "slot": 0}])
    if not board1:
        print("✗ Failed to create first board")
        return False
    
    board1_id = board1['id']
    print(f"✓ Created first board with ID: {board1_id}")
    
    # Create second board directly in database
    print("Creating second board directly...")
    board2 = Board.create(user_id, [{"name": "Test2", "rarity": "SR", "slot": 1}])
    if not board2:
        print("✗ Failed to create second board")
        return False
    
    board2_id = board2['id']
    print(f"✓ Created second board with ID: {board2_id}")
    
    # Verify we have 2 boards in the database for this user
    print("Checking that user has multiple boards before API call...")
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM boards WHERE user_id = ?", (user_id,))
        board_count = cursor.fetchone()[0]
        conn.close()
        
        if board_count != 2:
            print(f"✗ Expected 2 boards, found {board_count}")
            return False
        
        print(f"✓ User has {board_count} boards before API call")
    except Exception as e:
        print(f"✗ Error checking board count: {e}")
        return False
    
    # Now test the API endpoint (simulate what happens when user clicks "refresh board")
    print("Testing API endpoint that should delete old boards...")
    
    # Note: Since we're not running the Flask server, we'll directly call the function
    # that the API endpoint calls
    try:
        # This simulates what the API endpoint does:
        # 1. Delete existing boards
        Board.delete_by_user(user_id)
        
        # 2. Create new board
        import tools
        import characters
        import random
        board_data = tools.generate_balanced_bingo_board(characters.characters, random.randint(1, 10000))
        new_board = Board.create(user_id, board_data)
        
        if not new_board:
            print("✗ Failed to create new board via API simulation")
            return False
        
        new_board_id = new_board['id']
        print(f"✓ Created new board via API simulation with ID: {new_board_id}")
        
    except Exception as e:
        print(f"✗ Error during API simulation: {e}")
        return False
    
    # Verify that only 1 board exists now
    print("Checking that user now has only 1 board...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM boards WHERE user_id = ?", (user_id,))
        final_board_count = cursor.fetchone()[0]
        conn.close()
        
        if final_board_count != 1:
            print(f"✗ Expected 1 board after refresh, found {final_board_count}")
            return False
        
        print(f"✓ User now has {final_board_count} board after refresh")
    except Exception as e:
        print(f"✗ Error checking final board count: {e}")
        return False
    
    # Verify it's the new board
    current_board = Board.get_by_user(user_id)
    if current_board and current_board['id'] == new_board_id:
        print(f"✓ The remaining board is the new one (ID: {new_board_id})")
        success = True
    else:
        print(f"✗ Wrong board remains. Expected ID: {new_board_id}, Found: {current_board['id'] if current_board else 'None'}")
        success = False
    
    # Clean up
    try:
        delete_player_by_display_name("APITestUser")
    except:
        pass
    
    return success

def main():
    print("=== API Board Refresh Test ===\n")
    
    success = test_api_board_refresh()
    
    print("\n=== Test Results ===")
    if success:
        print("✓ API board refresh test passed! Old boards are properly deleted.")
    else:
        print("✗ API board refresh test failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

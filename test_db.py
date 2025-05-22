"""
Test script for database operations.
This script tests the basic functionality of the database models.
"""

import logging
import json
from models import User, Board, Progress
from database import init_db
import tools
import characters
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_user_operations():
    """Test user creation and retrieval"""
    logger.info("Testing user operations...")
    
    # Create a test user
    test_pin = "1234"
    test_name = "Test User"
    
    user = User.create(test_pin, test_name)
    logger.info(f"Created user: {user}")
    
    # Retrieve the user by PIN
    retrieved_user = User.get_by_pin(test_pin)
    logger.info(f"Retrieved user: {retrieved_user}")
    
    # Get all users
    all_users = User.get_all()
    logger.info(f"All users: {all_users}")
    
    return user

def test_board_operations(user_id):
    """Test board creation and retrieval"""
    logger.info("Testing board operations...")
    
    # Generate a board
    board_data = tools.generate_balanced_bingo_board(characters.characters, random.randint(1, 10000))
    
    # Create a board for the user
    board = Board.create(user_id, board_data)
    logger.info(f"Created board: {board}")
    
    # Retrieve the board by user
    retrieved_board = Board.get_by_user(user_id)
    logger.info(f"Retrieved board: {retrieved_board}")
    
    return board

def test_progress_operations(user_id, board_id):
    """Test progress creation and updates"""
    logger.info("Testing progress operations...")
    
    # Create initial progress with FREE space marked
    marked_cells = [12]  # Assuming index 12 is the FREE space
    progress = Progress.create_or_update(user_id, board_id, marked_cells)
    logger.info(f"Created progress: {progress}")
    
    # Update progress with more marked cells
    marked_cells = [12, 0, 5, 10, 15]
    score = 15
    updated_progress = Progress.create_or_update(user_id, board_id, marked_cells, score)
    logger.info(f"Updated progress: {updated_progress}")
    
    # Retrieve progress
    retrieved_progress = Progress.get_by_user_board(user_id, board_id)
    logger.info(f"Retrieved progress: {retrieved_progress}")
    
    # Get leaderboard
    leaderboard = Progress.get_leaderboard()
    logger.info(f"Leaderboard: {leaderboard}")
    
    return progress

def run_tests():
    """Run all tests"""
    logger.info("Starting database tests...")
    
    # Initialize the database
    init_db()
    
    # Test user operations
    user = test_user_operations()
    
    if user:
        # Test board operations
        board = test_board_operations(user['id'])
        
        if board:
            # Test progress operations
            test_progress_operations(user['id'], board['id'])
    
    logger.info("Database tests completed.")

if __name__ == "__main__":
    run_tests()

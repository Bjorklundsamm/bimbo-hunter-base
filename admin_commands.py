#!/usr/bin/env python3
"""
Admin Commands for Bingo Hunter Application

This script provides administrative commands for managing the bingo board application.
Available commands:
1. delete-all-boards - Delete all boards and progress data
2. delete-board <display_name> - Delete a specific user's board by display name
3. generate-test-user [squares_claimed] - Generate a test user with random name and optional claimed squares

Usage:
    python admin_commands.py delete-all-boards
    python admin_commands.py delete-board "username"
    python admin_commands.py generate-test-user
    python admin_commands.py generate-test-user 5
"""

import sys
import os
import random
import argparse
import logging
from typing import Optional, List

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User, Board, Progress
from database import get_db_connection, init_db
import tools
import characters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Random name components for generating test users
FIRST_NAMES = [
    "Alex", "Blake", "Casey", "Drew", "Emery", "Finley", "Gray", "Harper",
    "Indigo", "Jordan", "Kai", "Lane", "Morgan", "Nova", "Ocean", "Parker",
    "Quinn", "River", "Sage", "Taylor", "Unity", "Vale", "Winter", "Zara",
    "Ash", "Brook", "Cedar", "Dawn", "Echo", "Frost", "Grove", "Haven",
    "Iris", "Jade", "Knox", "Luna", "Moss", "North", "Onyx", "Pine",
    "Quest", "Rain", "Storm", "Teal", "Urban", "Vega", "Wave", "Zen"
]

ADJECTIVES = [
    "Swift", "Bright", "Cool", "Wild", "Calm", "Bold", "Wise", "Free",
    "Pure", "Brave", "Quick", "Sharp", "Smooth", "Strong", "Gentle", "Fierce",
    "Silent", "Mystic", "Golden", "Silver", "Crystal", "Shadow", "Flame", "Frost",
    "Thunder", "Lightning", "Cosmic", "Stellar", "Lunar", "Solar", "Neon", "Prism"
]

def generate_random_name() -> str:
    """Generate a random display name for test users."""
    first = random.choice(FIRST_NAMES)
    adj = random.choice(ADJECTIVES)
    num = random.randint(10, 999)

    # Try different combinations to avoid duplicates
    combinations = [
        f"{adj}{first}",
        f"{first}{adj}",
        f"{adj}{first}{num}",
        f"{first}{num}",
        f"{adj}{num}"
    ]

    return random.choice(combinations)

def delete_all_boards() -> bool:
    """
    Delete all boards and progress data from the database.

    Returns:
        bool: True if successful, False otherwise
    """
    print("🗑️  Deleting all boards and progress data...")

    conn = get_db_connection()
    if conn is None:
        print("❌ Failed to connect to database")
        return False

    try:
        cursor = conn.cursor()

        # Delete all progress first (due to foreign key constraints)
        cursor.execute("DELETE FROM progress")
        progress_deleted = cursor.rowcount

        # Delete all boards
        cursor.execute("DELETE FROM boards")
        boards_deleted = cursor.rowcount

        conn.commit()

        print(f"✅ Successfully deleted {boards_deleted} boards and {progress_deleted} progress records")
        return True

    except Exception as e:
        print(f"❌ Error deleting boards: {e}")
        return False
    finally:
        conn.close()

def delete_player_by_display_name(display_name: str) -> bool:
    """
    Delete a specific player (user) and all their associated data by display name.

    Args:
        display_name: The display name of the player to delete

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"🗑️  Deleting player '{display_name}' and all associated data...")

    # First, find the user
    user = User.get_by_display_name(display_name)
    if not user:
        print(f"❌ Player '{display_name}' not found")
        return False

    conn = get_db_connection()
    if conn is None:
        print("❌ Failed to connect to database")
        return False

    try:
        cursor = conn.cursor()

        # Delete progress for this user
        cursor.execute("DELETE FROM progress WHERE user_id = ?", (user['id'],))
        progress_deleted = cursor.rowcount

        # Delete boards for this user
        cursor.execute("DELETE FROM boards WHERE user_id = ?", (user['id'],))
        boards_deleted = cursor.rowcount

        # Delete the user
        cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
        user_deleted = cursor.rowcount

        conn.commit()

        if user_deleted > 0:
            print(f"✅ Successfully deleted player '{display_name}' with {boards_deleted} boards and {progress_deleted} progress records")
        else:
            print(f"❌ Failed to delete player '{display_name}'")
            return False

        return True

    except Exception as e:
        print(f"❌ Error deleting player '{display_name}': {e}")
        return False
    finally:
        conn.close()

def delete_all_players() -> bool:
    """
    Delete all players (users) and all their associated data from the database.

    Returns:
        bool: True if successful, False otherwise
    """
    print("🗑️  Deleting all players and associated data...")

    conn = get_db_connection()
    if conn is None:
        print("❌ Failed to connect to database")
        return False

    try:
        cursor = conn.cursor()

        # Delete all progress first (due to foreign key constraints)
        cursor.execute("DELETE FROM progress")
        progress_deleted = cursor.rowcount

        # Delete all boards
        cursor.execute("DELETE FROM boards")
        boards_deleted = cursor.rowcount

        # Delete all users
        cursor.execute("DELETE FROM users")
        users_deleted = cursor.rowcount

        conn.commit()

        print(f"✅ Successfully deleted {users_deleted} players, {boards_deleted} boards, and {progress_deleted} progress records")
        return True

    except Exception as e:
        print(f"❌ Error deleting all players: {e}")
        return False
    finally:
        conn.close()

def delete_board_by_display_name(display_name: str) -> bool:
    """
    Delete a specific user's board and progress by display name.

    Args:
        display_name: The display name of the user whose board to delete

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"🗑️  Deleting board for user '{display_name}'...")

    # First, find the user
    user = User.get_by_display_name(display_name)
    if not user:
        print(f"❌ User '{display_name}' not found")
        return False

    conn = get_db_connection()
    if conn is None:
        print("❌ Failed to connect to database")
        return False

    try:
        cursor = conn.cursor()

        # Delete progress for this user
        cursor.execute("DELETE FROM progress WHERE user_id = ?", (user['id'],))
        progress_deleted = cursor.rowcount

        # Delete boards for this user
        cursor.execute("DELETE FROM boards WHERE user_id = ?", (user['id'],))
        boards_deleted = cursor.rowcount

        conn.commit()

        if boards_deleted > 0 or progress_deleted > 0:
            print(f"✅ Successfully deleted {boards_deleted} boards and {progress_deleted} progress records for '{display_name}'")
        else:
            print(f"ℹ️  No boards found for user '{display_name}'")

        return True

    except Exception as e:
        print(f"❌ Error deleting board for '{display_name}': {e}")
        return False
    finally:
        conn.close()

def generate_test_user(squares_claimed: Optional[int] = None, display_name: Optional[str] = None) -> bool:
    """
    Generate a test user with random or specified name and optionally claim random squares.

    Args:
        squares_claimed: Number of squares to claim (random if None)
        display_name: Specific display name to use (random if None)

    Returns:
        bool: True if successful, False otherwise
    """
    print("👤 Generating test user...")

    # Generate or use provided display name
    if display_name is None:
        # Generate random name and ensure uniqueness
        max_attempts = 50
        for _ in range(max_attempts):
            display_name = generate_random_name()

            # Check if name already exists
            existing_user = User.get_by_display_name(display_name)
            if not existing_user:
                break
        else:
            print(f"❌ Failed to generate unique display name after {max_attempts} attempts")
            return False
    else:
        # Check if provided name already exists
        existing_user = User.get_by_display_name(display_name)
        if existing_user:
            print(f"❌ Display name '{display_name}' already exists")
            return False

    # Generate random PIN
    pin = str(random.randint(1000, 9999))

    # Create the user
    user = User.create(pin, display_name)
    if not user:
        print(f"❌ Failed to create user '{display_name}'")
        return False

    print(f"✅ Created user: '{display_name}' (PIN: {pin}, ID: {user['id']})")

    # Generate a board for the user
    board_data = tools.generate_balanced_bingo_board(characters.characters, random.randint(1, 10000))
    board = Board.create(user['id'], board_data)

    if not board:
        print(f"❌ Failed to create board for user '{display_name}'")
        return False

    print(f"✅ Created board for user '{display_name}' (Board ID: {board['id']})")

    # Determine how many squares to claim
    if squares_claimed is None:
        # Random between 1 and 15 (reasonable range)
        squares_claimed = random.randint(1, 15)

    # Ensure we don't claim more squares than available
    squares_claimed = min(squares_claimed, 25)

    # Always include the FREE space (center)
    marked_cells = []
    free_index = next((i for i, char in enumerate(board_data) if char['rarity'] == 'FREE'), -1)
    if free_index != -1:
        marked_cells.append(free_index)

    # Add random additional squares
    available_indices = list(range(25))
    if free_index != -1:
        available_indices.remove(free_index)

    additional_squares = min(squares_claimed - 1, len(available_indices))
    if additional_squares > 0:
        additional_indices = random.sample(available_indices, additional_squares)
        marked_cells.extend(additional_indices)

    # Calculate score based on claimed squares
    score = 0
    for index in marked_cells:
        char = board_data[index]
        score += tools.RARITY_POINTS.get(char['rarity'], 0)

    # Create progress
    progress = Progress.create_or_update(user['id'], board['id'], marked_cells, score)

    if progress:
        print(f"✅ Created progress: {len(marked_cells)} squares claimed, {score} points")
        print(f"🎯 Test user ready! Access at: /boards/{display_name}")
    else:
        print(f"❌ Failed to create progress for user '{display_name}'")
        return False

    return True

def main():
    """Main function to handle command line arguments and execute admin commands."""
    parser = argparse.ArgumentParser(
        description="Admin commands for Bingo Hunter application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python admin_commands.py delete-all-boards
  python admin_commands.py delete-board "Mayjay"
  python admin_commands.py generate-test-user
  python admin_commands.py generate-test-user 8
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Delete all boards command
    subparsers.add_parser('delete-all-boards', help='Delete all boards and progress data')

    # Delete specific board command
    delete_board_parser = subparsers.add_parser('delete-board', help='Delete a specific user\'s board')
    delete_board_parser.add_argument('display_name', help='Display name of the user whose board to delete')

    # Delete all players command
    subparsers.add_parser('delete-all-players', help='Delete all players and their associated data')

    # Delete specific player command
    delete_player_parser = subparsers.add_parser('delete-player', help='Delete a specific player and all their data')
    delete_player_parser.add_argument('display_name', help='Display name of the player to delete')

    # Generate test user command
    test_parser = subparsers.add_parser('generate-test-user', help='Generate a test user with random data')
    test_parser.add_argument('squares_claimed', nargs='?', type=int,
                           help='Number of squares to claim (random if not specified)')
    test_parser.add_argument('--name', type=str,
                           help='Specific display name to use (random if not specified)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize database
    print("🔧 Initializing database...")
    init_db()

    # Execute the requested command
    success = False

    if args.command == 'delete-all-boards':
        success = delete_all_boards()

    elif args.command == 'delete-board':
        success = delete_board_by_display_name(args.display_name)

    elif args.command == 'delete-all-players':
        success = delete_all_players()

    elif args.command == 'delete-player':
        success = delete_player_by_display_name(args.display_name)

    elif args.command == 'generate-test-user':
        success = generate_test_user(args.squares_claimed, args.name)

    if success:
        print("\n🎉 Command completed successfully!")
    else:
        print("\n💥 Command failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
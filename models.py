"""
Models module for database operations.
Provides CRUD operations for users, boards, and progress.
"""

import json
import logging
import sqlite3
from sqlite3 import Error
from datetime import datetime
from database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class User:
    """User model for authentication and profile management."""

    @staticmethod
    def create(pin, display_name):
        """
        Create a new user.

        Args:
            pin (str): User's PIN for authentication
            display_name (str): User's display name

        Returns:
            dict: User data if created successfully, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()

            # Check if user with this PIN already exists
            cursor.execute("SELECT * FROM users WHERE pin = ?", (pin,))
            existing_user = cursor.fetchone()

            if existing_user:
                logger.warning(f"User with PIN {pin} already exists")
                conn.close()
                return dict(existing_user)

            # Check if display name is already taken (case-insensitive)
            cursor.execute("SELECT * FROM users WHERE LOWER(display_name) = LOWER(?)", (display_name,))
            existing_display_name = cursor.fetchone()

            if existing_display_name:
                logger.warning(f"Display name '{display_name}' is already taken (case-insensitive)")
                conn.close()
                return None

            # Create new user
            cursor.execute(
                "INSERT INTO users (pin, display_name) VALUES (?, ?)",
                (pin, display_name)
            )
            conn.commit()

            # Get the created user
            user_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

            return dict(user) if user else None

        except Error as e:
            logger.error(f"Error creating user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_pin(pin):
        """
        Get a user by PIN.

        Args:
            pin (str): User's PIN

        Returns:
            dict: User data if found, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE pin = ?", (pin,))
            user = cursor.fetchone()

            # Update last login time
            if user:
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user['id'],)
                )
                conn.commit()

            return dict(user) if user else None

        except Error as e:
            logger.error(f"Error getting user by PIN: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_display_name(display_name):
        """
        Get a user by display name.

        Args:
            display_name (str): User's display name

        Returns:
            dict: User data if found, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE display_name = ?", (display_name,))
            user = cursor.fetchone()

            return dict(user) if user else None

        except Error as e:
            logger.error(f"Error getting user by display name: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """
        Get all users.

        Returns:
            list: List of user dictionaries
        """
        conn = get_db_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY display_name")
            users = cursor.fetchall()

            return [dict(user) for user in users]

        except Error as e:
            logger.error(f"Error getting all users: {e}")
            return []
        finally:
            conn.close()


class Board:
    """Board model for bingo board management."""

    @staticmethod
    def create(user_id, board_data):
        """
        Create a new board for a user.

        Args:
            user_id (int): User ID
            board_data (list): Board data as a list of characters

        Returns:
            dict: Board data if created successfully, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()

            # Convert board data to JSON string
            board_json = json.dumps(board_data)

            # Create new board
            cursor.execute(
                "INSERT INTO boards (user_id, board_data) VALUES (?, ?)",
                (user_id, board_json)
            )
            conn.commit()

            # Get the created board
            board_id = cursor.lastrowid
            cursor.execute("SELECT * FROM boards WHERE id = ?", (board_id,))
            board = cursor.fetchone()

            if board:
                board_dict = dict(board)
                # Parse the JSON string back to a list
                board_dict['board_data'] = json.loads(board_dict['board_data'])
                return board_dict
            return None

        except Error as e:
            logger.error(f"Error creating board: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_user(user_id):
        """
        Get a user's board.

        Args:
            user_id (int): User ID

        Returns:
            dict: Board data if found, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM boards WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            board = cursor.fetchone()

            if board:
                board_dict = dict(board)
                # Parse the JSON string back to a list
                board_dict['board_data'] = json.loads(board_dict['board_data'])
                return board_dict
            return None

        except Error as e:
            logger.error(f"Error getting board by user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(board_id):
        """
        Get a board by ID.

        Args:
            board_id (int): Board ID

        Returns:
            dict: Board data if found, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM boards WHERE id = ?", (board_id,))
            board = cursor.fetchone()

            if board:
                board_dict = dict(board)
                # Parse the JSON string back to a list
                board_dict['board_data'] = json.loads(board_dict['board_data'])
                return board_dict
            return None

        except Error as e:
            logger.error(f"Error getting board by ID: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def delete_by_user(user_id):
        """
        Delete all boards and associated progress for a user.

        Args:
            user_id (int): User ID

        Returns:
            bool: True if successful, False otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()

            # Delete progress first (due to foreign key constraints)
            cursor.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
            progress_deleted = cursor.rowcount

            # Delete boards for this user
            cursor.execute("DELETE FROM boards WHERE user_id = ?", (user_id,))
            boards_deleted = cursor.rowcount

            conn.commit()

            logger.info(f"Deleted {boards_deleted} boards and {progress_deleted} progress records for user {user_id}")
            return True

        except Error as e:
            logger.error(f"Error deleting boards for user {user_id}: {e}")
            return False
        finally:
            conn.close()


class Progress:
    """Progress model for tracking user progress on boards."""

    @staticmethod
    def create_or_update(user_id, board_id, marked_cells, score=0, user_images=None):
        """
        Create or update progress for a user on a board.

        Args:
            user_id (int): User ID
            board_id (int): Board ID
            marked_cells (list): List of marked cell indices
            score (int): Current score
            user_images (dict): Dictionary mapping square indices to user image paths

        Returns:
            dict: Progress data if created/updated successfully, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()

            # Convert marked cells to JSON string
            marked_cells_json = json.dumps(list(marked_cells))

            # Convert user_images to JSON string
            if user_images is None:
                user_images = {}
            user_images_json = json.dumps(user_images)

            # Check if progress already exists
            cursor.execute(
                "SELECT * FROM progress WHERE user_id = ? AND board_id = ?",
                (user_id, board_id)
            )
            existing_progress = cursor.fetchone()

            if existing_progress:
                # Update existing progress
                cursor.execute(
                    """
                    UPDATE progress
                    SET marked_cells = ?, user_images = ?, score = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND board_id = ?
                    """,
                    (marked_cells_json, user_images_json, score, user_id, board_id)
                )
            else:
                # Create new progress
                cursor.execute(
                    """
                    INSERT INTO progress (user_id, board_id, marked_cells, user_images, score)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, board_id, marked_cells_json, user_images_json, score)
                )

            conn.commit()

            # Get the updated progress
            cursor.execute(
                "SELECT * FROM progress WHERE user_id = ? AND board_id = ?",
                (user_id, board_id)
            )
            progress = cursor.fetchone()

            if progress:
                progress_dict = dict(progress)
                # Parse the JSON strings back to their original types
                progress_dict['marked_cells'] = json.loads(progress_dict['marked_cells'])
                progress_dict['user_images'] = json.loads(progress_dict.get('user_images', '{}'))
                return progress_dict
            return None

        except Error as e:
            logger.error(f"Error creating/updating progress: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_user_board(user_id, board_id):
        """
        Get progress for a user on a board.

        Args:
            user_id (int): User ID
            board_id (int): Board ID

        Returns:
            dict: Progress data if found, None otherwise
        """
        conn = get_db_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM progress WHERE user_id = ? AND board_id = ?",
                (user_id, board_id)
            )
            progress = cursor.fetchone()

            if progress:
                progress_dict = dict(progress)
                # Parse the JSON strings back to their original types
                progress_dict['marked_cells'] = json.loads(progress_dict['marked_cells'])
                progress_dict['user_images'] = json.loads(progress_dict.get('user_images', '{}'))
                return progress_dict
            return None

        except Error as e:
            logger.error(f"Error getting progress: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_leaderboard():
        """
        Get leaderboard data sorted by score.

        Returns:
            list: List of user progress with display names and scores
        """
        conn = get_db_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT u.id as user_id, u.display_name, p.score, p.updated_at
                FROM progress p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.score DESC
                """
            )
            leaderboard = cursor.fetchall()

            return [dict(entry) for entry in leaderboard]

        except Error as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
        finally:
            conn.close()

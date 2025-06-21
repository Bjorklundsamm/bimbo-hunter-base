"""
Database module for SQLite connection and management.
Handles database initialization, connection, and schema setup.
"""

import os
import sqlite3
from sqlite3 import Error
import json
import logging
from config import DB_FILE

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Create a database connection to the SQLite database.

    Returns:
        Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        logger.error(f"Error connecting to database: {e}")
        if conn:
            conn.close()
        return None

def init_db():
    """
    Initialize the database with the required schema.
    Creates tables if they don't exist.
    """
    # SQL to create tables
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pin TEXT NOT NULL,
        display_name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_boards_table = """
    CREATE TABLE IF NOT EXISTS boards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        board_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """

    create_progress_table = """
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        board_id INTEGER NOT NULL,
        marked_cells TEXT NOT NULL,
        user_images TEXT DEFAULT '{}',
        score INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (board_id) REFERENCES boards (id) ON DELETE CASCADE
    );
    """

    create_paimon_context_table = """
    CREATE TABLE IF NOT EXISTS paimon_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        context_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_paimon_updates_table = """
    CREATE TABLE IF NOT EXISTS paimon_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        update_type TEXT NOT NULL,
        update_data TEXT NOT NULL,
        processed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP NULL
    );
    """

    # Connect to database and create tables
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(create_users_table)
            cursor.execute(create_boards_table)
            cursor.execute(create_progress_table)
            cursor.execute(create_paimon_context_table)
            cursor.execute(create_paimon_updates_table)
            conn.commit()
            logger.info("Database schema created successfully")
        except Error as e:
            logger.error(f"Error creating database schema: {e}")
        finally:
            conn.close()
    else:
        logger.error("Error: Could not establish database connection")

def check_db_exists():
    """
    Check if the database file exists.

    Returns:
        bool: True if exists, False otherwise
    """
    return os.path.exists(DB_FILE)

def clear_database():
    """
    Clear all data from the database tables.
    """
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database")
        return False

    try:
        cursor = conn.cursor()

        # Delete all data from tables (in order due to foreign key constraints)
        cursor.execute("DELETE FROM progress")
        cursor.execute("DELETE FROM boards")
        cursor.execute("DELETE FROM users")

        conn.commit()
        print("Database cleared successfully")
        return True

    except Error as e:
        print(f"Error clearing database: {e}")
        return False
    finally:
        if conn:
            conn.close()

def create_test_user():
    """
    Create a test user named 'Mayjay'.
    """
    from models import User

    # Create test user
    user = User.create("1234", "Mayjay")
    if user:
        print(f"Test user created: {user}")
        return user
    else:
        print("Failed to create test user")
        return None

# Initialize the database if it doesn't exist
if not check_db_exists():
    logger.info("Database file not found. Creating new database...")
    init_db()
else:
    logger.info("Database file found.")
    # Verify schema is up to date
    init_db()

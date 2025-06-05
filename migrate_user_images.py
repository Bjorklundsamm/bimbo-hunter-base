#!/usr/bin/env python3
"""
Migration script to add user_images column to the progress table.
This script safely adds the new column if it doesn't exist.
"""

import sqlite3
import json
import logging
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_user_images():
    """Add user_images column to progress table if it doesn't exist."""
    conn = get_db_connection()
    if conn is None:
        logger.error("Could not connect to database")
        return False

    try:
        cursor = conn.cursor()
        
        # Check if user_images column exists
        cursor.execute("PRAGMA table_info(progress)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_images' not in columns:
            logger.info("Adding user_images column to progress table...")
            cursor.execute("ALTER TABLE progress ADD COLUMN user_images TEXT DEFAULT '{}'")
            conn.commit()
            logger.info("Successfully added user_images column")
        else:
            logger.info("user_images column already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_user_images()
    if success:
        print("✅ Migration completed successfully")
    else:
        print("❌ Migration failed")

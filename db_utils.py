"""
Database utilities module for common database operations.
Provides reusable database functions and error handling.
"""

import sqlite3
import logging
from contextlib import contextmanager
from config import DB_FILE

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles connection cleanup and error handling.
    
    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query with automatic connection management.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters
        fetch_one (bool): Whether to fetch one result
        fetch_all (bool): Whether to fetch all results
        
    Returns:
        Query result or None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
    except sqlite3.Error as e:
        logger.error(f"Query execution failed: {e}")
        return None

def execute_many(query, params_list):
    """
    Execute a query multiple times with different parameters.
    
    Args:
        query (str): SQL query to execute
        params_list (list): List of parameter tuples
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Batch execution failed: {e}")
        return False

def table_exists(table_name):
    """
    Check if a table exists in the database.
    
    Args:
        table_name (str): Name of the table
        
    Returns:
        bool: True if table exists, False otherwise
    """
    query = """
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name=?
    """
    result = execute_query(query, (table_name,), fetch_one=True)
    return result is not None

def get_table_info(table_name):
    """
    Get information about a table's columns.
    
    Args:
        table_name (str): Name of the table
        
    Returns:
        list: List of column information
    """
    query = f"PRAGMA table_info({table_name})"
    return execute_query(query, fetch_all=True)

def backup_database(backup_path):
    """
    Create a backup of the database.
    
    Args:
        backup_path (str): Path for the backup file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as source:
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
            logger.info(f"Database backed up to {backup_path}")
            return True
    except sqlite3.Error as e:
        logger.error(f"Backup failed: {e}")
        return False

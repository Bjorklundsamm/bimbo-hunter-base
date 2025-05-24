#!/usr/bin/env python3
"""
Script to clear the database and create test user 'Mayjay'.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import clear_database, create_test_user, init_db

def main():
    print("Starting database setup...")
    
    # Initialize database schema (in case it needs updating)
    print("Initializing database schema...")
    init_db()
    
    # Clear all existing data
    print("Clearing existing database data...")
    if clear_database():
        print("✓ Database cleared successfully")
    else:
        print("✗ Failed to clear database")
        return False
    
    # Create test user
    print("Creating test user 'Mayjay'...")
    user = create_test_user()
    if user:
        print(f"✓ Test user created successfully: {user['display_name']} (ID: {user['id']})")
    else:
        print("✗ Failed to create test user")
        return False
    
    print("\nDatabase setup completed successfully!")
    print(f"Test user 'Mayjay' can be accessed at: /boards/Mayjay")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Script to check recent Paimon updates in the database
"""

import sqlite3
import json
from datetime import datetime
from config import DB_FILE

def check_recent_updates():
    """Check recent Paimon updates"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get recent updates
        cursor.execute("""
            SELECT id, update_type, update_data, processed, created_at, processed_at
            FROM paimon_updates 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        updates = cursor.fetchall()
        
        print("🔍 Recent Paimon Updates:")
        print("=" * 80)
        
        if not updates:
            print("No updates found in database.")
            return
        
        for update in updates:
            print(f"\nID: {update['id']}")
            print(f"Type: {update['update_type']}")
            print(f"Processed: {'✅' if update['processed'] else '❌'}")
            print(f"Created: {update['created_at']}")
            if update['processed_at']:
                print(f"Processed: {update['processed_at']}")
            
            # Parse and display update data
            try:
                data = json.loads(update['update_data'])
                print("Data:")
                for key, value in data.items():
                    if key == 'new_claims' and isinstance(value, list):
                        print(f"  {key}: {len(value)} claims")
                        for claim in value:
                            print(f"    - {claim.get('name', 'Unknown')} ({claim.get('rarity', 'Unknown')})")
                    else:
                        print(f"  {key}: {value}")
            except json.JSONDecodeError:
                print(f"  Raw data: {update['update_data']}")
            
            print("-" * 40)
        
        # Check for any UR+ claims specifically
        cursor.execute("""
            SELECT id, update_type, update_data, created_at
            FROM paimon_updates 
            WHERE update_data LIKE '%UR+%'
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        ur_updates = cursor.fetchall()
        
        if ur_updates:
            print("\n🌟 Recent UR+ Related Updates:")
            print("=" * 80)
            
            for update in ur_updates:
                print(f"\nID: {update['id']} - {update['created_at']}")
                try:
                    data = json.loads(update['update_data'])
                    if 'new_claims' in data:
                        for claim in data['new_claims']:
                            if claim.get('rarity') == 'UR+':
                                print(f"  🎯 UR+ Claim: {claim.get('name', 'Unknown')} by {data.get('display_name', 'Unknown')}")
                except json.JSONDecodeError:
                    pass
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_recent_updates()

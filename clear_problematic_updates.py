#!/usr/bin/env python3
"""
Script to clear problematic updates from the database
"""

import sqlite3
import json
from config import DB_FILE

def clear_problematic_updates():
    """Clear updates that might be causing the 'Name' error"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get all unprocessed updates
        cursor.execute("""
            SELECT id, update_type, update_data
            FROM paimon_updates 
            WHERE processed = FALSE
        """)
        
        updates = cursor.fetchall()
        
        print("🔍 Checking for problematic updates...")
        
        problematic_ids = []
        
        for update in updates:
            update_id, update_type, update_data_str = update
            
            try:
                update_data = json.loads(update_data_str)
                
                # Check if this is a progress update with new_claims
                if update_type == 'progress_updated' and 'new_claims' in update_data:
                    new_claims = update_data['new_claims']
                    
                    for claim in new_claims:
                        # Check if claim has neither 'Name' nor 'name'
                        if not claim.get('Name') and not claim.get('name'):
                            print(f"❌ Found problematic update {update_id}: missing character name")
                            problematic_ids.append(update_id)
                            break
                        # Check if claim tries to access 'Name' but doesn't have it
                        elif 'Name' not in claim and 'name' not in claim:
                            print(f"❌ Found problematic update {update_id}: no name field")
                            problematic_ids.append(update_id)
                            break
                            
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"❌ Found malformed update {update_id}: {e}")
                problematic_ids.append(update_id)
        
        if problematic_ids:
            print(f"\n🧹 Marking {len(problematic_ids)} problematic updates as processed...")
            
            for update_id in problematic_ids:
                cursor.execute("""
                    UPDATE paimon_updates 
                    SET processed = TRUE, processed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (update_id,))
            
            conn.commit()
            print("✅ Problematic updates have been marked as processed")
        else:
            print("✅ No problematic updates found")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_problematic_updates()

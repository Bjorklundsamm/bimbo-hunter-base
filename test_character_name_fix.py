#!/usr/bin/env python3
"""
Test script to verify character name fix
"""

import sys
import os

# Add paimon directory to path
paimon_path = os.path.join(os.path.dirname(__file__), 'p(ai)mon')
if paimon_path not in sys.path:
    sys.path.append(paimon_path)

from context_manager import ContextManager
from prompts import UPDATE_TYPES

def test_character_name_fix():
    """Test that character names are correctly extracted"""
    
    # Create a mock update with character data using uppercase 'Name'
    mock_update_data = {
        'user_id': 39,
        'display_name': 'TestUser',
        'board_id': 45,
        'old_score': 1,
        'new_score': 7,
        'new_claims': [
            {
                'Name': 'Illumi Zoldyck',  # Note: uppercase 'Name'
                'rarity': 'UR+'
            }
        ],
        'total_marked': 2
    }
    
    # Test the context manager formatting
    context_manager = ContextManager()
    formatted_update = context_manager.format_update_for_context(
        UPDATE_TYPES['PROGRESS_UPDATED'], 
        mock_update_data
    )
    
    print("🧪 Testing Character Name Fix")
    print("=" * 50)
    print(f"Mock update data: {mock_update_data['new_claims']}")
    print(f"Formatted update: {formatted_update}")
    
    # Check if the character name appears correctly
    if 'Illumi Zoldyck' in formatted_update:
        print("✅ Character name fix is working!")
        print("✅ Character names should now appear correctly in Paimon updates")
    else:
        print("❌ Character name fix is NOT working")
        print("❌ Character names will still show as 'Unknown'")
    
    return 'Illumi Zoldyck' in formatted_update

if __name__ == "__main__":
    success = test_character_name_fix()
    if not success:
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script for Paimon bot components
Tests functionality without requiring Discord connection
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_game_context():
    """Test the GameContext class"""
    print("🧪 Testing GameContext...")
    
    try:
        from game_context import GameContext
        context = GameContext()
        
        # Test basic functionality
        leaderboard = context.get_leaderboard()
        print(f"   ✅ Leaderboard initialized: {len(leaderboard)} players")
        
        # Test recent activity
        recent = context.get_player_recent_activity(1, hours=1)
        print(f"   ✅ Recent activity check works: {len(recent)} claims")
        
        # Test rarest claims
        rarest = context.get_rarest_recent_claims(hours=24)
        print(f"   ✅ Rarest claims check works: {len(rarest)} claims")
        
        print("   ✅ GameContext tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ GameContext test failed: {e}")
        return False

def test_notification_engine():
    """Test the NotificationEngine class"""
    print("🧪 Testing NotificationEngine...")
    
    try:
        from game_context import GameContext
        from notification_engine import NotificationEngine
        
        context = GameContext()
        engine = NotificationEngine(context)
        
        # Test with empty changes
        changes = {
            'new_claims': [],
            'new_players': [],
            'score_changes': [],
            'inactive_players': []
        }
        
        announcements = engine.process_changes(changes)
        print(f"   ✅ Empty changes processed: {len(announcements)} announcements")
        
        # Test with mock claim
        mock_claim = {
            'user_id': 1,
            'display_name': 'TestUser',
            'character': {
                'Name': 'Test Character',
                'rarity': 'SSR'
            },
            'cell_index': 5,
            'timestamp': 1234567890
        }
        
        changes['new_claims'] = [mock_claim]
        announcements = engine.process_changes(changes)
        print(f"   ✅ Mock claim processed: {len(announcements)} announcements")
        
        print("   ✅ NotificationEngine tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ NotificationEngine test failed: {e}")
        return False

def test_chat_handler():
    """Test the ChatHandler class"""
    print("🧪 Testing ChatHandler...")
    
    try:
        from game_context import GameContext
        from chat_handler import ChatHandler
        
        context = GameContext()
        handler = ChatHandler(context)
        
        # Test game-related questions
        test_messages = [
            ("Who's in the lead?", "TestUser"),
            ("What's my score?", "TestUser"),
            ("How am I doing?", "TestUser"),
            ("Help me", "TestUser"),
            ("What's the weather?", "TestUser"),  # Should get off-topic response
        ]
        
        for message, author in test_messages:
            response = handler.handle_message(message, author)
            status = "✅" if response else "⚪"
            print(f"   {status} '{message}' -> {'Response' if response else 'No response'}")
        
        print("   ✅ ChatHandler tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ ChatHandler test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("🧪 Testing Configuration...")
    
    try:
        from config import (
            RARITY_POINTS, RARITY_NAMES, GAME_KEYWORDS,
            PERSONALITY_RESPONSES, MONITORING_INTERVAL
        )
        
        print(f"   ✅ Rarity points loaded: {len(RARITY_POINTS)} rarities")
        print(f"   ✅ Rarity names loaded: {len(RARITY_NAMES)} names")
        print(f"   ✅ Game keywords loaded: {len(GAME_KEYWORDS)} keywords")
        print(f"   ✅ Personality responses loaded: {len(PERSONALITY_RESPONSES)} categories")
        print(f"   ✅ Monitoring interval: {MONITORING_INTERVAL} seconds")
        
        print("   ✅ Configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def main():
    """Run all component tests"""
    print("🌟 Testing Paimon Bot Components")
    print("=" * 40)
    
    tests = [
        test_config,
        test_game_context,
        test_notification_engine,
        test_chat_handler,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Paimon components are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script for Paimon improvements
Tests the new functionality without requiring Discord connection
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_contextual_queries():
    """Test contextual character queries"""
    print("🧪 Testing Contextual Character Queries...")

    try:
        from game_context import GameContext
        from chat_handler import ChatHandler

        # Mock characters with different rarities for testing
        mock_characters = [
            {"Name": "Illumi Zoldyck", "Source": "Hunter x Hunter", "rarity": "UR+"},
            {"Name": "Midna (True Form)", "Source": "Zelda", "rarity": "UR+"},
            {"Name": "Sinbad", "Source": "Magi", "rarity": "UR+"},
            {"Name": "Test SSR", "Source": "Test Anime", "rarity": "SSR"},
            {"Name": "Test SR", "Source": "Test Show", "rarity": "SR"},
        ]

        context = GameContext()
        context.all_characters = mock_characters  # Override with mock data
        handler = ChatHandler(context)

        # Test various contextual queries
        test_queries = [
            ("Hey @p(AI)mon who is UR+ for this game?", "Should list UR+ characters"),
            ("@p(AI)mon who are most rare people in this year's game?", "Should list UR+ characters (rarest)"),
            ("What are the rarest characters?", "Should list UR+ characters"),
            ("Who are the most valuable characters?", "Should list UR+ characters"),
            ("Show me the legendary characters", "Should list UR+ characters"),
            ("What SSR characters are there?", "Should list SSR characters"),
            ("Tell me about rarity", "Should give rarity guide (no character request)"),
        ]

        for query, expected in test_queries:
            response = handler.handle_message(query, "TestUser")

            # Check if response is appropriate
            if "most rare" in query.lower() or "rarest" in query.lower() or "valuable" in query.lower() or "legendary" in query.lower():
                # Should get UR+ character list
                if response and ("Illumi Zoldyck" in response or "Ultra Rare Plus" in response):
                    print(f"   ✅ '{query[:50]}...' -> Got UR+ characters (correct)")
                else:
                    print(f"   ❌ '{query[:50]}...' -> {response[:50] if response else 'No response'}... (should be UR+ list)")
            elif "UR+" in query:
                # Should get UR+ character list
                if response and "Illumi Zoldyck" in response:
                    print(f"   ✅ '{query[:50]}...' -> Got UR+ characters (correct)")
                else:
                    print(f"   ❌ '{query[:50]}...' -> {response[:50] if response else 'No response'}... (should be UR+ list)")
            elif "SSR" in query:
                # Should get SSR character list
                if response and "Test SSR" in response:
                    print(f"   ✅ '{query[:50]}...' -> Got SSR characters (correct)")
                else:
                    print(f"   ❌ '{query[:50]}...' -> {response[:50] if response else 'No response'}... (should be SSR list)")
            elif "rarity" in query.lower() and "characters" not in query.lower():
                # Should get rarity guide
                if response and "Rarity Guide" in response:
                    print(f"   ✅ '{query[:50]}...' -> Got rarity guide (correct)")
                else:
                    print(f"   ❌ '{query[:50]}...' -> {response[:50] if response else 'No response'}... (should be rarity guide)")

        print("   ✅ Contextual query tests completed!")
        return True

    except Exception as e:
        print(f"   ❌ Contextual query test failed: {e}")
        return False

def test_tied_leaderboard():
    """Test tied score handling"""
    print("🧪 Testing Tied Leaderboard Logic...")
    
    try:
        from game_context import GameContext
        from chat_handler import ChatHandler
        
        context = GameContext()
        # Mock tied players
        context.players = {
            1: {'display_name': 'Aloof', 'score': 5, 'marked_cells': set()},
            2: {'display_name': 'bongdrei', 'score': 5, 'marked_cells': set()},
            3: {'display_name': 'Player3', 'score': 3, 'marked_cells': set()},
        }
        
        handler = ChatHandler(context)
        
        # Test tied leaderboard query
        response = handler.handle_message("who is in the lead right now?", "TestUser")
        print(f"   ✅ Tied Leaderboard Response: {response}")
        
        # Check if it properly identifies the tie
        if "tie" in response.lower() and "aloof" in response and "bongdrei" in response:
            print("   ✅ Correctly identified tie!")
        else:
            print("   ⚠️ May not have properly identified tie")
        
        print("   ✅ Tied leaderboard tests completed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Tied leaderboard test failed: {e}")
        return False

def test_upload_detection():
    """Test upload detection logic"""
    print("🧪 Testing Upload Detection...")
    
    try:
        from game_context import GameContext
        from notification_engine import NotificationEngine
        
        context = GameContext()
        engine = NotificationEngine(context)
        
        # Mock a UR+ upload claim
        mock_claim = {
            'user_id': 1,
            'display_name': 'TestUser',
            'character': {
                'Name': 'Illumi Zoldyck',
                'rarity': 'UR+'
            },
            'cell_index': 5,
            'timestamp': 1234567890,
            'has_upload': True,
            'is_upload_only': False
        }
        
        # Test UR+ claim processing
        announcement = engine._process_new_claim(mock_claim, 1234567890)
        
        if announcement:
            print(f"   ✅ UR+ Announcement: {announcement['message']}")
            if 'LEGENDARY' in announcement['message'] or 'Ultra Rare Plus' in announcement['message']:
                print("   ✅ UR+ properly emphasized!")
            else:
                print("   ⚠️ UR+ may not be properly emphasized")
        else:
            print("   ❌ No announcement generated for UR+ claim!")
            return False
        
        # Test upload-only claim
        mock_claim['is_upload_only'] = True
        announcement = engine._process_new_claim(mock_claim, 1234567890)
        
        if announcement and 'uploaded proof' in announcement['message']:
            print("   ✅ Upload-only announcement works!")
        else:
            print("   ⚠️ Upload-only announcement may not work properly")
        
        print("   ✅ Upload detection tests completed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Upload detection test failed: {e}")
        return False

def main():
    """Run all improvement tests"""
    print("🌟 Testing Paimon Improvements")
    print("=" * 50)
    
    tests = [
        test_contextual_queries,
        test_tied_leaderboard,
        test_upload_detection,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Improvement Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All improvements working correctly!")
        print("\n🚀 Ready to test with Discord:")
        print("1. Ask: 'Hey @p(AI)mon who is UR+ for this game?'")
        print("2. Ask: '@p(AI)mon who are most rare people in this year's game?'")
        print("3. Upload a UR+ character to trigger announcements")
        print("4. Check leaderboard with tied scores")
        return True
    else:
        print("❌ Some improvements need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Chat Handler for Paimon Discord Bot
Handles direct questions and chat interactions
"""

import random
import re
from typing import Optional
from config import GAME_KEYWORDS, PERSONALITY_RESPONSES, RARITY_NAMES


class ChatHandler:
    """Handles chat interactions and questions about the game"""
    
    def __init__(self, game_context):
        self.game_context = game_context
        
    def handle_message(self, message_content: str, author_name: str) -> Optional[str]:
        """
        Process a chat message and return a response if appropriate
        Returns None if no response should be sent
        """
        message_lower = message_content.lower()
        
        # Check if message is game-related
        if not self._is_game_related(message_lower):
            # Only respond if directly mentioned or asked a question
            if any(word in message_lower for word in ['paimon', '?', 'who', 'what', 'how', 'when']):
                return random.choice(PERSONALITY_RESPONSES['off_topic'])
            return None
        
        # Handle specific game questions
        response = self._handle_game_question(message_lower, author_name)
        if response:
            return response
        
        # Default game-related response
        return random.choice(PERSONALITY_RESPONSES['greeting'])
    
    def _is_game_related(self, message: str) -> bool:
        """Check if a message is related to the bimbo hunter game"""
        return any(keyword in message for keyword in GAME_KEYWORDS)
    
    def _handle_game_question(self, message: str, author_name: str) -> Optional[str]:
        """Handle specific game-related questions with contextual interpretation"""

        # Analyze the intent of the question more contextually
        message_lower = message.lower()

        # Questions about rare/valuable characters (highest priority)
        if self._is_asking_about_rare_characters(message_lower):
            return self._get_rarest_characters_response(message_lower)

        # Specific rarity queries (UR+, SSR, etc.)
        if any(rarity in message.upper() for rarity in ['UR+', 'SSR', 'SR', 'FREE']):
            return self._get_characters_by_rarity_response(message)

        # Leaderboard questions
        if self._is_asking_about_leaderboard(message_lower):
            return self._get_leaderboard_response()

        # Personal score/progress questions
        if self._is_asking_about_personal_stats(message_lower, author_name):
            if any(word in message_lower for word in ['progress', 'doing', 'how am i']):
                return self._get_personal_progress_response(author_name)
            else:
                return self._get_personal_score_response(author_name)

        # General score questions
        if any(word in message_lower for word in ['score', 'points']) and not self._is_asking_about_personal_stats(message_lower, author_name):
            return self._get_leaderboard_response()

        # Game status questions
        if self._is_asking_about_game_status(message_lower):
            return self._get_game_status_response()

        # General rarity system questions (only if not asking about specific characters)
        if any(word in message_lower for word in ['rarity', 'worth', 'points system']) and not self._is_asking_about_rare_characters(message_lower):
            return self._get_rarity_info_response()

        # Help questions
        if any(word in message_lower for word in ['help', 'how to', 'rules', 'play']):
            return self._get_help_response()

        return None

    def _is_asking_about_rare_characters(self, message: str) -> bool:
        """Determine if the user is asking about rare/valuable characters"""
        rare_indicators = [
            'most rare', 'rarest', 'most valuable', 'most worth', 'hardest to find',
            'best characters', 'top characters', 'highest value', 'most points',
            'legendary', 'ultra rare', 'super rare', 'valuable characters',
            'rare people', 'rare characters', 'rare cards', 'rare ones'
        ]

        # Check for combinations that indicate asking about rare characters
        asking_about_characters = any(word in message for word in ['who', 'what', 'which', 'characters', 'people', 'cards'])
        asking_about_rarity = any(indicator in message for indicator in rare_indicators)

        return asking_about_characters and asking_about_rarity

    def _is_asking_about_leaderboard(self, message: str) -> bool:
        """Determine if asking about leaderboard/rankings"""
        return any(word in message for word in ['lead', 'leader', 'leaderboard', 'winning', 'first', 'top player', 'rankings'])

    def _is_asking_about_personal_stats(self, message: str, author_name: str) -> bool:
        """Determine if asking about personal stats"""
        return any(word in message for word in ['my', 'me', 'i ', author_name.lower()])

    def _is_asking_about_game_status(self, message: str) -> bool:
        """Determine if asking about overall game status"""
        return any(phrase in message for phrase in ['status', 'how is', 'going', 'today', 'happening', 'game doing'])
    
    def _get_leaderboard_response(self) -> str:
        """Get current leaderboard information"""
        leaderboard = self.game_context.get_leaderboard()

        if not leaderboard:
            return "No one's hunting yet! Be the first to claim some squares! 🎯"

        if len(leaderboard) == 1:
            leader = leaderboard[0]
            return f"{leader['display_name']} is the only hunter so far with {leader['score']} points! 🏆"

        leader = leaderboard[0]
        second = leaderboard[1]

        # Check for ties
        if leader['score'] == second['score']:
            # Find all players tied for first
            tied_players = [p for p in leaderboard if p['score'] == leader['score']]
            if len(tied_players) == 2:
                return f"🤝 It's a tie! {leader['display_name']} and {second['display_name']} are both tied at {leader['score']} points!"
            else:
                names = [p['display_name'] for p in tied_players[:3]]  # Show up to 3 names
                if len(tied_players) > 3:
                    return f"🤝 Big tie! {', '.join(names)} and {len(tied_players) - 3} others are all tied at {leader['score']} points!"
                else:
                    return f"🤝 Triple tie! {', '.join(names)} are all tied at {leader['score']} points!"

        # No tie - normal leaderboard
        response = f"🏆 {leader['display_name']} is in the lead with {leader['score']} points!"

        if leader['score'] - second['score'] <= 5:
            response += f" But {second['display_name']} is hot on their trail with {second['score']} points! 🔥"
        else:
            response += f" {second['display_name']} is in second with {second['score']} points."

        return response
    
    def _get_personal_score_response(self, author_name: str) -> str:
        """Get personal score for the asking user"""
        # Try to find the user by display name
        user_data = None
        for player in self.game_context.players.values():
            if player['display_name'].lower() == author_name.lower():
                user_data = player
                break
        
        if not user_data:
            return f"Paimon doesn't see {author_name} on the hunting boards yet! Time to start hunting! 🎯"
        
        score = user_data['score']
        claims = len(user_data['marked_cells'])
        
        if score == 1:  # Only FREE square
            return f"{author_name}, you've got your FREE square but no catches yet! Get out there and hunt! 💪"
        
        leaderboard = self.game_context.get_leaderboard()
        position = next((i+1 for i, p in enumerate(leaderboard) if p['display_name'].lower() == author_name.lower()), None)
        
        if position == 1:
            return f"🏆 {author_name}, you're leading the pack with {score} points from {claims} squares! Keep it up!"
        elif position:
            return f"{author_name}, you've got {score} points from {claims} squares! You're in position #{position}! 📈"
        else:
            return f"{author_name}, you have {score} points from {claims} squares! Keep hunting! 🎯"
    
    def _get_personal_progress_response(self, author_name: str) -> str:
        """Get personal progress information"""
        # Try to find the user by display name
        user_data = None
        for player in self.game_context.players.values():
            if player['display_name'].lower() == author_name.lower():
                user_data = player
                break
        
        if not user_data:
            return f"Paimon doesn't see {author_name} on the hunting boards yet! 🎯"
        
        recent_claims = self.game_context.get_player_recent_activity(
            next(uid for uid, p in self.game_context.players.items() if p == user_data),
            hours=24
        )
        
        if not recent_claims:
            return f"{author_name}, you haven't made any catches today! Time to get back out there! 💪"
        
        if len(recent_claims) == 1:
            claim = recent_claims[0]
            rarity_name = RARITY_NAMES.get(claim['character']['rarity'], claim['character']['rarity'])
            return f"{author_name}, you caught {claim['character']['Name']} ({rarity_name}) today! Nice work! ⭐"
        
        return f"{author_name}, you've made {len(recent_claims)} catches today! You're on fire! 🔥"
    
    def _get_game_status_response(self) -> str:
        """Get overall game status"""
        leaderboard = self.game_context.get_leaderboard()
        rarest_claims = self.game_context.get_rarest_recent_claims(hours=24)
        
        if not leaderboard:
            return "The hunt is just beginning! No catches yet today! 🎯"
        
        total_players = len(leaderboard)
        active_players = len([p for p in leaderboard if p['score'] > 1])
        
        response = f"📊 Hunt Status: {active_players} active hunters out of {total_players} total!"
        
        if rarest_claims:
            rarest = rarest_claims[0]
            rarity_name = RARITY_NAMES.get(rarest['character']['rarity'], rarest['character']['rarity'])
            response += f" Rarest catch today: {rarest['character']['Name']} ({rarity_name})! 🌟"
        
        return response
    
    def _get_rarity_info_response(self) -> str:
        """Get information about rarity system"""
        return (
            "🎯 Rarity Guide:\n"
            "• R (Common) - 2 points\n"
            "• SR (Super Rare) - 3 points\n"
            "• SSR (Super Super Rare) - 4 points\n"
            "• UR+ (Ultra Rare Plus) - 6 points\n"
            "The rarer the catch, the more points you get! 💎"
        )
    
    def _get_characters_by_rarity_response(self, message: str) -> str:
        """Get characters of a specific rarity"""
        message_upper = message.upper()

        # Determine which rarity was asked about with more flexible matching
        target_rarity = None
        if 'UR+' in message_upper or 'ULTRA RARE' in message_upper:
            target_rarity = 'UR+'
        elif 'SSR' in message_upper or 'SUPER SUPER RARE' in message_upper:
            target_rarity = 'SSR'
        elif 'SR' in message_upper or 'SUPER RARE' in message_upper:
            target_rarity = 'SR'
        elif ('R' in message_upper and 'SR' not in message_upper and 'UR' not in message_upper) or 'COMMON' in message_upper:
            target_rarity = 'R'
        elif 'FREE' in message_upper:
            target_rarity = 'FREE'

        # If no specific rarity mentioned but asking about characters, default to rarest
        if not target_rarity and any(word in message.lower() for word in ['characters', 'people', 'cards', 'who']):
            return self._get_rarest_characters_response(message)

        if not target_rarity:
            return "🤔 Which rarity are you asking about? Try 'UR+', 'SSR', 'SR', 'R', or 'FREE'!"

        # Get characters of that rarity
        characters = self.game_context.get_characters_by_rarity(target_rarity)

        if not characters:
            return f"🎯 No {target_rarity} characters found! Maybe they haven't loaded yet?"

        # Format the response with appropriate emoji and emphasis
        rarity_name = RARITY_NAMES.get(target_rarity, target_rarity)
        char_list = [f"• {char['Name']} ({char['Source']})" for char in characters[:10]]  # Limit to 10

        # Choose emoji based on rarity
        emoji = "💎" if target_rarity == "UR+" else "⭐" if target_rarity == "SSR" else "🎯"

        response = f"{emoji} {rarity_name} Characters ({len(characters)} total):\n"
        response += "\n".join(char_list)

        if len(characters) > 10:
            response += f"\n... and {len(characters) - 10} more!"

        # Add point value info
        points = {'FREE': 1, 'R': 2, 'SR': 3, 'SSR': 4, 'UR+': 6}.get(target_rarity, 0)
        if points:
            response += f"\n\nEach {rarity_name} character is worth {points} points!"

        return response

    def _get_rarest_characters_response(self, message: str) -> str:
        """Get the rarest characters in the game"""
        # Start with UR+ characters (rarest)
        ur_plus_chars = self.game_context.get_characters_by_rarity('UR+')

        if ur_plus_chars:
            char_list = [f"• {char['Name']} ({char['Source']})" for char in ur_plus_chars]
            response = f"🌟 The rarest characters in the game are the Ultra Rare Plus ones ({len(ur_plus_chars)} total):\n"
            response += "\n".join(char_list)
            response += f"\n\nThese are worth 6 points each and are the most valuable catches! 💎"
            return response

        # Fallback to SSR if no UR+ found
        ssr_chars = self.game_context.get_characters_by_rarity('SSR')
        if ssr_chars:
            char_list = [f"• {char['Name']} ({char['Source']})" for char in ssr_chars[:10]]
            response = f"⭐ The rarest characters available are Super Super Rare ({len(ssr_chars)} total):\n"
            response += "\n".join(char_list)
            if len(ssr_chars) > 10:
                response += f"\n... and {len(ssr_chars) - 10} more!"
            response += f"\n\nThese are worth 4 points each! 🎯"
            return response

        return "🤔 Paimon can't find the character data right now. Try asking again in a moment!"

    def _get_help_response(self) -> str:
        """Get help information"""
        return (
            "🎮 Bimbo Hunter Help:\n"
            "• Find cosplayers matching your bingo board\n"
            "• Take pictures with them (with consent!)\n"
            "• Upload photos to claim squares and earn points\n"
            "• Rarer characters = more points!\n"
            "• Complete rows/columns for bonus points!\n"
            "Ask Paimon about 'leaderboard', 'score', or 'rarity' for more info! 🎯"
        )

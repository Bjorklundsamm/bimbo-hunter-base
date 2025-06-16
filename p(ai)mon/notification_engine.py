"""
Notification Engine for Paimon Discord Bot
Determines when and what announcements to make
"""

import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from config import (
    RAPID_CLAIM_THRESHOLD, RAPID_CLAIM_WINDOW, RARE_CLAIM_THRESHOLD,
    ANNOUNCEMENT_COOLDOWN, DAILY_SUMMARY_HOUR, QUIET_HOURS_START, 
    QUIET_HOURS_END, PERSONALITY_RESPONSES, RARITY_NAMES
)


class NotificationEngine:
    """Determines what announcements to make based on game events"""
    
    def __init__(self, game_context):
        self.game_context = game_context
        self.last_announcements = {}
        
    def process_changes(self, changes: Dict) -> List[Dict]:
        """
        Process game changes and return list of announcements to make
        Each announcement has: type, message, images (optional)
        """
        announcements = []
        current_time = time.time()
        
        # Skip announcements during quiet hours
        if self._is_quiet_hours():
            return announcements
        
        # Process new claims
        for claim in changes['new_claims']:
            announcement = self._process_new_claim(claim, current_time)
            if announcement:
                announcements.append(announcement)
        
        # Process new players
        for new_player in changes['new_players']:
            announcement = self._process_new_player(new_player, current_time)
            if announcement:
                announcements.append(announcement)
        
        # Check for rapid claiming
        for user_id in set(claim['user_id'] for claim in changes['new_claims']):
            announcement = self._check_rapid_claiming(user_id, current_time)
            if announcement:
                announcements.append(announcement)
        
        # Check for daily summary
        if self._should_send_daily_summary():
            announcement = self._create_daily_summary()
            if announcement:
                announcements.append(announcement)
        
        # Check for inactive player encouragement
        announcement = self._check_inactive_players(current_time)
        if announcement:
            announcements.append(announcement)
        
        return announcements
    
    def _process_new_claim(self, claim: Dict, current_time: float) -> Optional[Dict]:
        """Process a single new claim and determine if it should be announced"""
        character = claim['character']
        rarity = character['rarity']
        display_name = claim['display_name']
        has_upload = claim.get('has_upload', False)
        is_upload_only = claim.get('is_upload_only', False)

        # Always announce UR+ claims (highest priority)
        if rarity == 'UR+':
            if is_upload_only:
                message = (f"🌟 LEGENDARY! {display_name} just uploaded proof of their "
                          f"{character['Name']} claim - that's Ultra Rare Plus! 💎")
            else:
                # Check if this is the player's first claim
                player_data = self.game_context.players.get(claim['user_id'], {})
                total_claims = len(player_data.get('marked_cells', set()))

                if total_claims == 1:  # First claim ever
                    message = (f"🚀 INCREDIBLE! {display_name} comes out swinging with "
                              f"{character['Name']} - an Ultra Rare Plus on their very first square! 💎")
                else:
                    message = (f"🌟 LEGENDARY! {display_name} just claimed "
                              f"{character['Name']} - an Ultra Rare Plus! 💎")

            return {
                'type': 'rare_claim',
                'message': message,
                'user_id': claim['user_id'],
                'rarity': rarity,
                'priority': 'highest'
            }

        # Always announce SSR claims
        elif rarity == 'SSR':
            if is_upload_only:
                message = (f"⭐ Amazing! {display_name} just uploaded proof of their "
                          f"{character['Name']} claim - that's Super Super Rare! ✨")
            else:
                # Check if this is the player's first claim
                player_data = self.game_context.players.get(claim['user_id'], {})
                total_claims = len(player_data.get('marked_cells', set()))

                if total_claims == 1:  # First claim ever
                    message = (f"Look who came out swinging! {display_name} claims "
                              f"{character['Name']} - a Super Super Rare on their very first square! 🔥")
                else:
                    message = (f"Incredible! {display_name} just claimed "
                              f"{character['Name']} - a Super Super Rare! ⭐")

            return {
                'type': 'rare_claim',
                'message': message,
                'user_id': claim['user_id'],
                'rarity': rarity,
                'priority': 'high'
            }

        # Announce SR claims if they have uploads (shows effort)
        elif rarity == 'SR' and has_upload:
            message = (f"Nice work! {display_name} just uploaded proof of their "
                      f"{character['Name']} claim - that's Super Rare! 🎯")

            return {
                'type': 'rare_claim',
                'message': message,
                'user_id': claim['user_id'],
                'rarity': rarity,
                'priority': 'medium'
            }

        return None
    
    def _process_new_player(self, new_player: Dict, current_time: float) -> Optional[Dict]:
        """Process a new player joining and determine if it should be announced"""
        # Only announce if they have more than just the FREE square
        if new_player['score'] > 1:
            message = f"Welcome to the hunt, {new_player['display_name']}! 🎯"
            return {
                'type': 'new_player',
                'message': message,
                'user_id': new_player['user_id']
            }
        return None
    
    def _check_rapid_claiming(self, user_id: int, current_time: float) -> Optional[Dict]:
        """Check if a player is claiming squares rapidly"""
        recent_claims = self.game_context.get_player_recent_activity(
            user_id, hours=RAPID_CLAIM_WINDOW/3600
        )
        
        if len(recent_claims) >= RAPID_CLAIM_THRESHOLD:
            player = self.game_context.players.get(user_id)
            if not player:
                return None
                
            display_name = player['display_name']
            
            # Check cooldown for this type of announcement for this player
            cooldown_key = f"rapid_claim_{user_id}"
            if (cooldown_key in self.last_announcements and 
                current_time - self.last_announcements[cooldown_key] < ANNOUNCEMENT_COOLDOWN):
                return None
            
            self.last_announcements[cooldown_key] = current_time
            
            message = f"{display_name} is on fire! That's {len(recent_claims)} squares in the last hour! 🔥"
            return {
                'type': 'rapid_claiming',
                'message': message,
                'user_id': user_id
            }
        
        return None
    
    def _should_send_daily_summary(self) -> bool:
        """Check if it's time to send the daily summary"""
        current_hour = datetime.now().hour
        return (current_hour == DAILY_SUMMARY_HOUR and 
                not self.game_context.daily_summary_sent)
    
    def _create_daily_summary(self) -> Optional[Dict]:
        """Create the daily summary announcement"""
        if self.game_context.daily_summary_sent:
            return None
            
        leaderboard = self.game_context.get_leaderboard()
        rarest_claims = self.game_context.get_rarest_recent_claims(hours=24)
        
        if not leaderboard:
            return None
        
        # Mark as sent
        self.game_context.daily_summary_sent = True
        
        # Create summary message
        top_player = leaderboard[0]
        message_parts = [
            "🌟 Daily Hunt Summary! 🌟",
            f"🏆 {top_player['display_name']} leads with {top_player['score']} points!"
        ]
        
        if len(leaderboard) > 1:
            second_player = leaderboard[1]
            message_parts.append(
                f"🥈 {second_player['display_name']} is close behind with {second_player['score']} points!"
            )
        
        if rarest_claims:
            rarest = rarest_claims[0]
            message_parts.append(
                f"🎯 Rarest catch today: {rarest['character']['Name']} "
                f"({RARITY_NAMES.get(rarest['character']['rarity'], rarest['character']['rarity'])}) "
                f"by {rarest['display_name']}!"
            )
        
        return {
            'type': 'daily_summary',
            'message': '\n'.join(message_parts)
        }
    
    def _check_inactive_players(self, current_time: float) -> Optional[Dict]:
        """Check for inactive players to encourage"""
        # Only send encouragement once per day per player
        current_date = datetime.now().date()
        
        for user_id, player in self.game_context.players.items():
            hours_inactive = (current_time - player['last_activity']) / 3600
            
            # Encourage players inactive for 12-36 hours
            if 12 <= hours_inactive <= 36 and player['score'] > 1:
                cooldown_key = f"encourage_{user_id}_{current_date}"
                
                if cooldown_key not in self.last_announcements:
                    self.last_announcements[cooldown_key] = current_time
                    
                    message = random.choice(PERSONALITY_RESPONSES['encouragement']).format(
                        name=player['display_name']
                    )
                    
                    return {
                        'type': 'encouragement',
                        'message': message,
                        'user_id': user_id
                    }
        
        return None
    
    def _is_quiet_hours(self) -> bool:
        """Check if it's currently quiet hours (no announcements)"""
        current_hour = datetime.now().hour
        
        if QUIET_HOURS_START < QUIET_HOURS_END:
            return QUIET_HOURS_START <= current_hour < QUIET_HOURS_END
        else:  # Quiet hours span midnight
            return current_hour >= QUIET_HOURS_START or current_hour < QUIET_HOURS_END

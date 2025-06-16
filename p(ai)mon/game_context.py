"""
Game Context Manager for Paimon Discord Bot
Tracks player progress and game state
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import GAME_API_BASE_URL, RARITY_POINTS


class GameContext:
    """Manages the current state of the bimbo hunter game"""

    def __init__(self):
        self.players = {}  # player_id -> player_data
        self.last_update = 0
        self.last_announcements = {}  # track when we last announced things
        self.daily_summary_sent = False
        self.last_daily_reset = datetime.now().date()
        self.all_characters = []  # Cache of all game characters
        self._load_characters()

    def _load_characters(self):
        """Load all characters from the API"""
        try:
            response = requests.get(f"{GAME_API_BASE_URL}/characters", timeout=10)
            if response.status_code == 200:
                self.all_characters = response.json()
                print(f"Loaded {len(self.all_characters)} characters")
            else:
                print(f"Failed to load characters: {response.status_code}")
        except Exception as e:
            print(f"Error loading characters: {e}")

    def get_characters_by_rarity(self, rarity: str) -> List[Dict]:
        """Get all characters of a specific rarity"""
        return [char for char in self.all_characters if char.get('rarity') == rarity]

    def update_context(self) -> Dict:
        """
        Update the game context with latest data from the API
        Returns a dict with changes detected
        """
        changes = {
            'new_claims': [],
            'new_players': [],
            'score_changes': [],
            'inactive_players': []
        }
        
        try:
            # Get current leaderboard
            response = requests.get(f"{GAME_API_BASE_URL}/leaderboard", timeout=10)
            if response.status_code != 200:
                return changes
                
            current_leaderboard = response.json()
            
            # Get detailed board data for all players
            admin_response = requests.get(f"{GAME_API_BASE_URL}/admin/boards", timeout=10)
            if admin_response.status_code != 200:
                return changes
                
            all_boards = admin_response.json()
            
            # Process each player
            current_time = time.time()
            
            for board_data in all_boards:
                user_id = board_data['user_id']
                display_name = board_data['display_name']
                
                # Get progress for this player
                progress_response = requests.get(
                    f"{GAME_API_BASE_URL}/users/{user_id}/boards/{board_data['id']}/progress",
                    timeout=10
                )
                
                if progress_response.status_code != 200:
                    continue
                    
                progress = progress_response.json()
                
                # Check if this is a new player
                if user_id not in self.players:
                    changes['new_players'].append({
                        'user_id': user_id,
                        'display_name': display_name,
                        'score': progress.get('score', 0)
                    })
                    
                    self.players[user_id] = {
                        'display_name': display_name,
                        'score': progress.get('score', 0),
                        'marked_cells': set(progress.get('marked_cells', [])),
                        'user_images': progress.get('user_images', {}),
                        'last_activity': current_time,
                        'recent_claims': [],
                        'board_data': board_data['board_data']
                    }
                    continue
                
                # Check for new claims and uploads
                old_marked = self.players[user_id]['marked_cells']
                new_marked = set(progress.get('marked_cells', []))
                new_claims = new_marked - old_marked

                # Also check for new uploads (user_images changes)
                old_user_images = self.players[user_id].get('user_images', {})
                new_user_images = progress.get('user_images', {})

                # Find newly uploaded images
                new_uploads = {}
                for cell_str, image_path in new_user_images.items():
                    if cell_str not in old_user_images or old_user_images[cell_str] != image_path:
                        new_uploads[cell_str] = image_path

                # Process new claims (including those with uploads)
                if new_claims or new_uploads:
                    # Handle new claims
                    for cell_index in new_claims:
                        if cell_index < len(board_data['board_data']):
                            character = board_data['board_data'][cell_index]
                            claim_data = {
                                'user_id': user_id,
                                'display_name': display_name,
                                'character': character,
                                'cell_index': cell_index,
                                'timestamp': current_time,
                                'has_upload': str(cell_index) in new_user_images
                            }
                            changes['new_claims'].append(claim_data)

                            # Add to recent claims (keep last 10)
                            self.players[user_id]['recent_claims'].append(claim_data)
                            self.players[user_id]['recent_claims'] = \
                                self.players[user_id]['recent_claims'][-10:]

                    # Handle uploads to existing claims
                    for cell_str, image_path in new_uploads.items():
                        try:
                            cell_index = int(cell_str)
                            if cell_index < len(board_data['board_data']) and cell_index in new_marked:
                                character = board_data['board_data'][cell_index]
                                # Only announce if this wasn't already processed as a new claim
                                if cell_index not in new_claims:
                                    claim_data = {
                                        'user_id': user_id,
                                        'display_name': display_name,
                                        'character': character,
                                        'cell_index': cell_index,
                                        'timestamp': current_time,
                                        'has_upload': True,
                                        'is_upload_only': True  # This is just an upload, not a new claim
                                    }
                                    changes['new_claims'].append(claim_data)
                        except (ValueError, IndexError):
                            continue

                    self.players[user_id]['last_activity'] = current_time
                
                # Check for score changes
                old_score = self.players[user_id]['score']
                new_score = progress.get('score', 0)
                if new_score != old_score:
                    changes['score_changes'].append({
                        'user_id': user_id,
                        'display_name': display_name,
                        'old_score': old_score,
                        'new_score': new_score,
                        'difference': new_score - old_score
                    })
                
                # Update player data
                self.players[user_id].update({
                    'score': new_score,
                    'marked_cells': new_marked,
                    'user_images': new_user_images,
                    'board_data': board_data['board_data']
                })
            
            # Check for inactive players
            inactive_threshold = current_time - 86400  # 24 hours
            for user_id, player in self.players.items():
                if (player['last_activity'] < inactive_threshold and 
                    player['score'] > 0):  # Only consider players who have played
                    changes['inactive_players'].append({
                        'user_id': user_id,
                        'display_name': player['display_name'],
                        'hours_inactive': (current_time - player['last_activity']) / 3600
                    })
            
            self.last_update = current_time
            
        except Exception as e:
            print(f"Error updating game context: {e}")
            
        return changes
    
    def get_leaderboard(self) -> List[Dict]:
        """Get current leaderboard sorted by score"""
        return sorted(
            [
                {
                    'display_name': player['display_name'],
                    'score': player['score'],
                    'user_id': user_id
                }
                for user_id, player in self.players.items()
            ],
            key=lambda x: x['score'],
            reverse=True
        )
    
    def get_player_recent_activity(self, user_id: int, hours: int = 1) -> List[Dict]:
        """Get a player's recent claims within the specified hours"""
        if user_id not in self.players:
            return []
            
        cutoff_time = time.time() - (hours * 3600)
        return [
            claim for claim in self.players[user_id]['recent_claims']
            if claim['timestamp'] > cutoff_time
        ]
    
    def get_rarest_recent_claims(self, hours: int = 24) -> List[Dict]:
        """Get the rarest claims from the last X hours"""
        cutoff_time = time.time() - (hours * 3600)
        recent_claims = []
        
        for player in self.players.values():
            for claim in player['recent_claims']:
                if claim['timestamp'] > cutoff_time:
                    recent_claims.append(claim)
        
        # Sort by rarity (UR+ first, then SSR, etc.)
        rarity_order = {'UR+': 0, 'SSR': 1, 'SR': 2, 'R': 3, 'FREE': 4}
        recent_claims.sort(
            key=lambda x: rarity_order.get(x['character']['rarity'], 5)
        )
        
        return recent_claims[:5]  # Top 5 rarest
    
    def should_reset_daily_tracking(self) -> bool:
        """Check if we should reset daily tracking (new day)"""
        current_date = datetime.now().date()
        if current_date != self.last_daily_reset:
            self.last_daily_reset = current_date
            self.daily_summary_sent = False
            return True
        return False

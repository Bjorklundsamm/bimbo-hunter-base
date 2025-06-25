"""
Context Manager for Paimon's agentic workflow
Handles storage and retrieval of context data and update queue
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from utils import setup_project_path, setup_paimon_logging

# Set up project path for imports
setup_project_path()

# Database connection function for Paimon
def get_db_connection():
    """Get database connection for Paimon (uses main project's database)"""
    import sqlite3
    import os

    # Database file is in the main project directory
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bhunter.db")

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None
from prompts import INITIAL_CONTEXT, format_user_for_context, UPDATE_TYPES

# Configure logging
logger = setup_paimon_logging(__name__)

class ContextManager:
    """Manages Paimon's context storage and update queue"""
    
    def __init__(self):
        """Initialize the context manager"""
        self._ensure_initial_context()
    
    def _ensure_initial_context(self):
        """Ensure there's an initial context in the database"""
        current_context = self.get_current_context()
        if not current_context:
            self.save_context(INITIAL_CONTEXT)
            logger.info("Initialized empty context in database")
    
    def get_current_context(self) -> Optional[str]:
        """
        Get the current context from the database
        
        Returns:
            str: Current context, or None if not found
        """
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT context_data FROM paimon_context ORDER BY updated_at DESC LIMIT 1"
            )
            result = cursor.fetchone()
            
            if result:
                return result[0]
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error getting current context: {e}")
            return None
        finally:
            conn.close()
    
    def save_context(self, context_data: str) -> bool:
        """
        Save updated context to the database
        
        Args:
            context_data (str): The context data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO paimon_context (context_data, updated_at) 
                VALUES (?, CURRENT_TIMESTAMP)
                """,
                (context_data,)
            )
            conn.commit()
            logger.info("Context saved successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error saving context: {e}")
            return False
        finally:
            conn.close()
    
    def add_update(self, update_type: str, update_data: Dict) -> bool:
        """
        Add an update to the processing queue
        
        Args:
            update_type (str): Type of update (from UPDATE_TYPES)
            update_data (dict): Data associated with the update
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO paimon_updates (update_type, update_data) 
                VALUES (?, ?)
                """,
                (update_type, json.dumps(update_data))
            )
            conn.commit()
            logger.info(f"Added update: {update_type}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error adding update: {e}")
            return False
        finally:
            conn.close()
    
    def get_pending_updates(self) -> List[Dict]:
        """
        Get all pending (unprocessed) updates
        
        Returns:
            list: List of pending updates
        """
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, update_type, update_data, created_at 
                FROM paimon_updates 
                WHERE processed = FALSE 
                ORDER BY created_at ASC
                """
            )
            results = cursor.fetchall()
            
            updates = []
            for row in results:
                updates.append({
                    'id': row[0],
                    'update_type': row[1],
                    'update_data': json.loads(row[2]),
                    'created_at': row[3]
                })
            
            return updates
            
        except sqlite3.Error as e:
            logger.error(f"Error getting pending updates: {e}")
            return []
        finally:
            conn.close()
    
    def mark_update_processed(self, update_id: int) -> bool:
        """
        Mark an update as processed
        
        Args:
            update_id (int): ID of the update to mark as processed
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE paimon_updates 
                SET processed = TRUE, processed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """,
                (update_id,)
            )
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error marking update as processed: {e}")
            return False
        finally:
            conn.close()
    
    def format_update_for_context(self, update_type: str, update_data: Dict) -> str:
        """
        Format an update into a human-readable string for context integration
        
        Args:
            update_type (str): Type of update
            update_data (dict): Update data
            
        Returns:
            str: Formatted update string
        """
        if update_type == UPDATE_TYPES['USER_REGISTERED']:
            display_name = update_data.get('display_name', 'Unknown')
            return f"{display_name} signed up and created an account."
        
        elif update_type == UPDATE_TYPES['BOARD_CREATED']:
            display_name = update_data.get('display_name', 'Unknown')
            return f"{display_name} generated their bingo board."
        
        elif update_type == UPDATE_TYPES['PROGRESS_UPDATED']:
            display_name = update_data.get('display_name', 'Unknown')
            old_score = update_data.get('old_score', 0)
            new_score = update_data.get('new_score', 0)
            new_claims = update_data.get('new_claims', [])
            
            if new_claims:
                claim_text = ", ".join([f"{char['Name']}({char['rarity']})" for char in new_claims])
                return f"{display_name} claimed new characters: {claim_text}. Score increased from {old_score} to {new_score} points."
            else:
                return f"{display_name} updated their progress. Score: {new_score} points."
        
        elif update_type == UPDATE_TYPES['PERIODIC_CHECK']:
            return "Periodic check completed - no significant changes detected."
        
        else:
            return f"Unknown update type: {update_type}"
    
    def get_current_game_state(self) -> Dict:
        """
        Get the current game state from the database
        
        Returns:
            dict: Current game state with users, boards, and progress
        """
        # Use direct database queries to avoid model import issues
        # from models import User, Board, Progress
        
        try:
            # Get data directly from database
            conn = get_db_connection()
            if not conn:
                return {'users': [], 'total_players': 0, 'active_players': 0}

            cursor = conn.cursor()

            # Get all users with their boards and progress
            cursor.execute("""
                SELECT
                    u.id, u.display_name, u.pin, u.created_at,
                    b.id as board_id, b.board_data,
                    p.marked_cells, p.score, p.user_images
                FROM users u
                LEFT JOIN boards b ON u.id = b.user_id
                LEFT JOIN progress p ON u.id = p.user_id AND b.id = p.board_id
            """)

            rows = cursor.fetchall()
            conn.close()

            users = []
            active_players = 0

            for row in rows:
                user = {
                    'id': row['id'],
                    'display_name': row['display_name'],
                    'pin': row['pin'],
                    'created_at': row['created_at']
                }

                board = None
                if row['board_id']:
                    board = {
                        'id': row['board_id'],
                        'board_data': json.loads(row['board_data']) if row['board_data'] else []
                    }

                progress = None
                if row['score'] is not None:
                    progress = {
                        'marked_cells': json.loads(row['marked_cells']) if row['marked_cells'] else [],
                        'score': row['score'],
                        'user_images': json.loads(row['user_images']) if row['user_images'] else {}
                    }

                    if progress['score'] > 0:
                        active_players += 1

                user_state = {
                    'user': user,
                    'board': board,
                    'progress': progress,
                    'formatted': format_user_for_context(user, board, progress)
                }

                users.append(user_state)

            return {
                'users': users,
                'total_players': len(users),
                'active_players': active_players
            }
            
        except Exception as e:
            logger.error(f"Error getting current game state: {e}")
            return {'users': [], 'total_players': 0, 'active_players': 0}

# Global instance
_context_manager = None

def get_context_manager() -> ContextManager:
    """Get the global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager

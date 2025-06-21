"""
Common utilities for Paimon Discord Bot
Provides reusable functions and path management
"""

import sys
import os
import logging
from typing import Optional

def setup_project_path():
    """
    Add the parent directory to the path for imports from main project.
    This is needed for importing from the main project's modules.
    """
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

def setup_paimon_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging for Paimon components with consistent formatting.
    
    Args:
        name (str): Logger name (usually __name__)
        level (int): Logging level (default: INFO)
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger

def safe_import(module_name: str, fallback_value=None):
    """
    Safely import a module with fallback handling.
    
    Args:
        module_name (str): Name of the module to import
        fallback_value: Value to return if import fails
        
    Returns:
        Imported module or fallback_value
    """
    try:
        return __import__(module_name)
    except ImportError as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to import {module_name}: {e}")
        return fallback_value

def format_discord_message(message: str, max_length: int = 2000) -> str:
    """
    Format a message for Discord, ensuring it doesn't exceed length limits.
    
    Args:
        message (str): Message to format
        max_length (int): Maximum message length (default: 2000)
        
    Returns:
        str: Formatted message
    """
    if len(message) <= max_length:
        return message
    
    # Truncate and add ellipsis
    truncated = message[:max_length - 3] + "..."
    return truncated

def get_rarity_emoji(rarity: str) -> str:
    """
    Get emoji representation for character rarity.
    
    Args:
        rarity (str): Character rarity
        
    Returns:
        str: Emoji string
    """
    rarity_emojis = {
        'FREE': '🆓',
        'R': '🔵',
        'SR': '🟣',
        'SSR': '🟠',
        'UR+': '🌟'
    }
    return rarity_emojis.get(rarity, '❓')

def get_rarity_color(rarity: str) -> int:
    """
    Get Discord embed color for character rarity.
    
    Args:
        rarity (str): Character rarity
        
    Returns:
        int: Color value for Discord embed
    """
    rarity_colors = {
        'FREE': 0x00ff00,    # Green
        'R': 0x0099ff,      # Blue
        'SR': 0x9900ff,     # Purple
        'SSR': 0xff6600,    # Orange
        'UR+': 0xffd700     # Gold
    }
    return rarity_colors.get(rarity, 0x808080)  # Gray default

def validate_environment_vars(*var_names) -> bool:
    """
    Validate that required environment variables are set.
    
    Args:
        *var_names: Variable names to check
        
    Returns:
        bool: True if all variables are set, False otherwise
    """
    missing_vars = []
    for var_name in var_names:
        if not os.getenv(var_name):
            missing_vars.append(var_name)
    
    if missing_vars:
        logger = logging.getLogger(__name__)
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst (list): List to chunk
        chunk_size (int): Size of each chunk
        
    Returns:
        list: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get_nested(data: dict, *keys, default=None):
    """
    Safely get nested dictionary values.
    
    Args:
        data (dict): Dictionary to search
        *keys: Nested keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

"""
Configuration module for the Bingo Hunter application.
Centralizes all configuration settings and constants.
"""

import logging
import os

# Database Configuration
DB_FILE = "bhunter.db"

# Server Configuration
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5000
DEBUG_MODE = False

# File Upload Configuration
UPLOAD_FOLDER = 'client/public/user-images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Image Processing Configuration
MAX_IMAGE_SIZE = (800, 800)  # Max dimensions for uploaded images
IMAGE_QUALITY = 85  # JPEG quality

# Admin Configuration
ADMIN_PIN = "cardsagainsthumanity"

# Rarity Points System
RARITY_POINTS = {
    'FREE': 1,
    'R': 2,
    'SR': 4,
    'SSR': 8,
    'UR+': 16
}

# Board Generation Configuration
BOARD_SIZE = 25  # 5x5 grid
FREE_SQUARE_INDEX = 12  # Center square (0-indexed)

# CORS Configuration
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']

# Logging Configuration
def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', mode='a')
        ]
    )

# File Utilities
def allowed_file(filename):
    """
    Check if a file has an allowed extension.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """Ensure the upload directory exists."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Environment Variables
def get_env_var(key, default=None):
    """
    Get environment variable with optional default.
    
    Args:
        key (str): Environment variable key
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default)

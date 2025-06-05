# app.py
from flask import Flask, jsonify, send_from_directory, request
import random
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import characters
import tools
import logging
from models import User, Board, Progress
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the database
init_db()

app = Flask(__name__, static_folder='resources')

# Configuration for file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'client/public/user-images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Enable CORS manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def hello_world():
    return 'Bimbo Hunter API is running'

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Return the list of all characters"""
    return jsonify(characters.characters)

@app.route('/api/generate-board', methods=['POST'])
def generate_board():
    """Generate a balanced bingo board from the provided characters"""
    # Get the characters from the request
    data = request.json
    chars_list = data.get('characters', characters.characters)

    # Generate a random seed
    seed = random.randint(1, 10000)

    # Generate a balanced board
    board = tools.generate_balanced_bingo_board(chars_list, seed)

    # Return the board as JSON
    return jsonify(board)

@app.route('/api/board', methods=['GET'])
def get_board():
    """Generate and return a bingo board (legacy endpoint)"""
    # Generate a random seed
    seed = random.randint(1, 10000)

    # Generate a balanced board
    board = tools.generate_balanced_bingo_board(characters.characters, seed)

    # Return the board as JSON
    return jsonify(board)

# User Authentication and Management Endpoints

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user with PIN"""
    data = request.json
    pin = data.get('pin')

    if not pin:
        return jsonify({'error': 'PIN is required'}), 400

    # Get user by PIN
    user = User.get_by_pin(pin)

    if user:
        return jsonify({'success': True, 'user': user})
    else:
        return jsonify({'error': 'Invalid PIN'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    pin = data.get('pin')
    display_name = data.get('display_name')

    if not pin or not display_name:
        return jsonify({'error': 'PIN and display name are required'}), 400

    # Create new user
    user = User.create(pin, display_name)

    if user:
        return jsonify({'success': True, 'user': user})
    else:
        return jsonify({'error': 'Display name already taken or failed to create user'}), 400

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.get_all()
    return jsonify(users)

# Board Management Endpoints

@app.route('/api/users/<int:user_id>/board', methods=['GET'])
def get_user_board(user_id):
    """Get a user's board"""
    board = Board.get_by_user(user_id)

    if board:
        return jsonify(board)
    else:
        # Return 404 if no board exists
        return jsonify({'error': 'No board found for this user'}), 404

@app.route('/api/users/<int:user_id>/board', methods=['POST'])
def create_user_board(user_id):
    """Create a new board for a user"""
    # Delete any existing boards for this user first
    Board.delete_by_user(user_id)

    # Generate a new board
    board_data = tools.generate_balanced_bingo_board(characters.characters, random.randint(1, 10000))
    new_board = Board.create(user_id, board_data)

    if new_board:
        # Initialize progress with FREE space marked
        free_index = next((i for i, char in enumerate(board_data) if char['rarity'] == 'FREE'), -1)
        if free_index != -1:
            marked_cells = [free_index]
            Progress.create_or_update(user_id, new_board['id'], marked_cells)

        return jsonify(new_board)
    else:
        return jsonify({'error': 'Failed to create board'}), 500

# Board access by display name
@app.route('/api/boards/<display_name>', methods=['GET'])
def get_board_by_display_name(display_name):
    """Get a user's board by their display name"""
    # Get user by display name
    user = User.get_by_display_name(display_name)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get the user's board
    board = Board.get_by_user(user['id'])

    if board:
        # Also include user info for the response
        response_data = {
            'board': board,
            'user': user
        }
        return jsonify(response_data)
    else:
        return jsonify({'error': 'No board found for this user'}), 404

@app.route('/api/boards/<display_name>/progress', methods=['GET'])
def get_board_progress_by_display_name(display_name):
    """Get a user's board progress by their display name"""
    # Get user by display name
    user = User.get_by_display_name(display_name)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get the user's board
    board = Board.get_by_user(user['id'])

    if not board:
        return jsonify({'error': 'No board found for this user'}), 404

    # Get progress
    progress = Progress.get_by_user_board(user['id'], board['id'])

    if progress:
        return jsonify(progress)
    else:
        # Initialize empty progress
        new_progress = Progress.create_or_update(user['id'], board['id'], [], 0)
        return jsonify(new_progress)

# Progress Tracking Endpoints

@app.route('/api/users/<int:user_id>/boards/<int:board_id>/progress', methods=['GET'])
def get_progress(user_id, board_id):
    """Get a user's progress on a board"""
    progress = Progress.get_by_user_board(user_id, board_id)

    if progress:
        return jsonify(progress)
    else:
        # Initialize empty progress
        new_progress = Progress.create_or_update(user_id, board_id, [], 0)
        return jsonify(new_progress)

@app.route('/api/users/<int:user_id>/boards/<int:board_id>/progress', methods=['POST'])
def update_progress(user_id, board_id):
    """Update a user's progress on a board"""
    data = request.json
    marked_cells = data.get('marked_cells', [])
    user_images = data.get('user_images', {})
    score = data.get('score', 0)

    # Update progress
    progress = Progress.create_or_update(user_id, board_id, marked_cells, score, user_images)

    if progress:
        return jsonify(progress)
    else:
        return jsonify({'error': 'Failed to update progress'}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the leaderboard"""
    leaderboard = Progress.get_leaderboard()
    return jsonify(leaderboard)

# File Upload Endpoints

@app.route('/api/users/<int:user_id>/boards/<int:board_id>/upload/<int:square_index>', methods=['POST'])
def upload_square_image(user_id, board_id, square_index):
    """Upload an image for a specific square"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        # Create directory structure if it doesn't exist
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), str(board_id))
        os.makedirs(user_dir, exist_ok=True)

        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{square_index}.{file_extension}"
        filepath = os.path.join(user_dir, filename)

        try:
            # Save and process the image
            file.save(filepath)

            # Resize image for optimal performance
            with Image.open(filepath) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Resize to max 800px on longest side while maintaining aspect ratio
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=85)

            # Return the relative path for frontend use
            relative_path = f"/user-images/{user_id}/{board_id}/{filename}"
            return jsonify({'success': True, 'image_path': relative_path})

        except Exception as e:
            logger.error(f"Error processing uploaded image: {e}")
            return jsonify({'error': 'Failed to process image'}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/resources/<path:path>')
def serve_resources(path):
    """Serve static resources"""
    # Serve the file from the resources directory
    return send_from_directory('resources', path)

if __name__ == '__main__':
    app.run(debug=True)

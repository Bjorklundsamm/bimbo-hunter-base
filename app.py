# app.py
from flask import Flask, jsonify, send_from_directory, request, send_file
import random
import os
from PIL import Image
import characters
import tools
from models import User, Board, Progress
from database import init_db
from config import (
    setup_logging, allowed_file, ensure_upload_dir,
    UPLOAD_FOLDER, MAX_FILE_SIZE, ADMIN_PIN,
    DEFAULT_HOST, DEFAULT_PORT, DEBUG_MODE,
    MAX_IMAGE_SIZE, IMAGE_QUALITY, CORS_ORIGINS
)
from db_utils import get_db_connection



# Configure logging
setup_logging()
logger = __import__('logging').getLogger(__name__)

# Initialize the database
init_db()

app = Flask(__name__, static_folder='client/build', static_url_path='')
app = Flask(__name__, static_folder='client/build', static_url_path='')

# Configuration for file uploads
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
ensure_upload_dir()



# Enable CORS manually
@app.after_request
def after_request(response):
    # Use configured origins in production, allow all in development
    origin = '*' if DEBUG_MODE else ','.join(CORS_ORIGINS)
    response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Root route is handled by the React app serving route at the bottom
# Root route is handled by the React app serving route at the bottom

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

    # Check for admin PIN
    if pin == ADMIN_PIN:
        admin_user = {
            'id': -1,
            'pin': pin,
            'display_name': 'Administrator',
            'is_admin': True,
            'created_at': None,
            'last_login': None
        }
        return jsonify({'success': True, 'user': admin_user})

    # Get user by PIN
    user = User.get_by_pin(pin)

    if user:
        user['is_admin'] = False
        user['is_admin'] = False
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
            # Calculate score for FREE square (1 point)
            score = 1
            Progress.create_or_update(user_id, new_board['id'], marked_cells, score)



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
        # Initialize progress with FREE space marked
        board_data = board['board_data']
        free_index = next((i for i, char in enumerate(board_data) if char['rarity'] == 'FREE'), -1)
        if free_index != -1:
            marked_cells = [free_index]
            score = 1  # FREE square is worth 1 point
            new_progress = Progress.create_or_update(user['id'], board['id'], marked_cells, score)
        else:
            # Fallback if no FREE square found
            new_progress = Progress.create_or_update(user['id'], board['id'], [], 0)
        # Initialize progress with FREE space marked
        board_data = board['board_data']
        free_index = next((i for i, char in enumerate(board_data) if char['rarity'] == 'FREE'), -1)
        if free_index != -1:
            marked_cells = [free_index]
            score = 1  # FREE square is worth 1 point
            new_progress = Progress.create_or_update(user['id'], board['id'], marked_cells, score)
        else:
            # Fallback if no FREE square found
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
        # Initialize progress with FREE space marked
        board = Board.get_by_id(board_id)
        if board:
            board_data = board['board_data']
            free_index = next((i for i, char in enumerate(board_data) if char['rarity'] == 'FREE'), -1)
            if free_index != -1:
                marked_cells = [free_index]
                score = 1  # FREE square is worth 1 point
                new_progress = Progress.create_or_update(user_id, board_id, marked_cells, score)
            else:
                # Fallback if no FREE square found
                new_progress = Progress.create_or_update(user_id, board_id, [], 0)
        else:
            # Fallback if board not found
            new_progress = Progress.create_or_update(user_id, board_id, [], 0)
        # Initialize progress with FREE space marked
        board = Board.get_by_id(board_id)
        if board:
            board_data = board['board_data']
            free_index = next((i for i, char in enumerate(board_data) if char['rarity'] == 'FREE'), -1)
            if free_index != -1:
                marked_cells = [free_index]
                score = 1  # FREE square is worth 1 point
                new_progress = Progress.create_or_update(user_id, board_id, marked_cells, score)
            else:
                # Fallback if no FREE square found
                new_progress = Progress.create_or_update(user_id, board_id, [], 0)
        else:
            # Fallback if board not found
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

@app.route('/api/group-points', methods=['GET'])
def get_group_points():
    """Get the total group points (sum of all players' scores)"""
    total_points = Progress.get_total_group_points()
    return jsonify({'total_points': total_points})

# Admin Endpoints

@app.route('/api/admin/restart-server', methods=['POST'])
def admin_restart_server():
    """Restart the server (admin only)"""
    import os
    import signal

    try:
        # This will restart the server by exiting the current process
        # The process manager (like systemd, supervisor, or manual restart) should restart it
        logger.info("Admin requested server restart")
        # Note: os.execv doesn't return, so the return statement after it is unreachable
        # We'll use a different approach for graceful restart
        os.kill(os.getpid(), signal.SIGTERM)
        return jsonify({'success': True, 'message': 'Server restarting...'})
    except Exception as e:
        logger.error(f"Error restarting server: {e}")
        return jsonify({'error': 'Failed to restart server'}), 500

@app.route('/api/admin/delete-all-boards', methods=['DELETE'])
def admin_delete_all_boards():
    """Delete all boards and progress data (admin only)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete all progress first (due to foreign key constraints)
            cursor.execute("DELETE FROM progress")
            progress_deleted = cursor.rowcount

            # Delete all boards
            cursor.execute("DELETE FROM boards")
            boards_deleted = cursor.rowcount

            conn.commit()

        logger.info(f"Admin deleted all boards: {boards_deleted} boards, {progress_deleted} progress records")
        return jsonify({
            'success': True,
            'message': f'Deleted {boards_deleted} boards and {progress_deleted} progress records'
        })

    except Exception as e:
        logger.error(f"Error deleting all boards: {e}")
        return jsonify({'error': 'Failed to delete all boards'}), 500

@app.route('/api/admin/delete-all-players', methods=['DELETE'])
def admin_delete_all_players():
    """Delete all players and their data (admin only)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete all progress first
            cursor.execute("DELETE FROM progress")
            progress_deleted = cursor.rowcount

            # Delete all boards
            cursor.execute("DELETE FROM boards")
            boards_deleted = cursor.rowcount

            # Delete all users
            cursor.execute("DELETE FROM users")
            users_deleted = cursor.rowcount

            conn.commit()

        logger.info(f"Admin deleted all players: {users_deleted} users, {boards_deleted} boards, {progress_deleted} progress records")
        return jsonify({
            'success': True,
            'message': f'Deleted {users_deleted} players, {boards_deleted} boards, and {progress_deleted} progress records'
        })

    except Exception as e:
        logger.error(f"Error deleting all players: {e}")
        return jsonify({'error': 'Failed to delete all players'}), 500

@app.route('/api/admin/delete-player/<int:user_id>', methods=['DELETE'])
def admin_delete_player(user_id):
    """Delete a specific player and their data (admin only)"""
    try:
        # Get user info first for logging
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'Player not found'}), 404

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete progress for this user
            cursor.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
            progress_deleted = cursor.rowcount

            # Delete boards for this user
            cursor.execute("DELETE FROM boards WHERE user_id = ?", (user_id,))
            boards_deleted = cursor.rowcount

            # Delete the user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            user_deleted = cursor.rowcount

            conn.commit()

        if user_deleted > 0:
            logger.info(f"Admin deleted player '{user['display_name']}' (ID: {user_id})")
            return jsonify({
                'success': True,
                'message': f"Deleted player '{user['display_name']}' with {boards_deleted} boards and {progress_deleted} progress records"
            })
        else:
            return jsonify({'error': 'Failed to delete player'}), 500

    except Exception as e:
        logger.error(f"Error deleting player {user_id}: {e}")
        return jsonify({'error': 'Failed to delete player'}), 500

@app.route('/api/admin/delete-board/<int:user_id>', methods=['DELETE'])
def admin_delete_board(user_id):
    """Delete a specific player's board (admin only)"""
    try:
        # Get user info first for logging
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'Player not found'}), 404

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete progress for this user
            cursor.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
            progress_deleted = cursor.rowcount

            # Delete boards for this user
            cursor.execute("DELETE FROM boards WHERE user_id = ?", (user_id,))
            boards_deleted = cursor.rowcount

            conn.commit()

        logger.info(f"Admin deleted board for player '{user['display_name']}' (ID: {user_id})")
        return jsonify({
            'success': True,
            'message': f"Deleted {boards_deleted} boards and {progress_deleted} progress records for '{user['display_name']}'"
        })

    except Exception as e:
        logger.error(f"Error deleting board for user {user_id}: {e}")
        return jsonify({'error': 'Failed to delete board'}), 500

@app.route('/api/admin/update-display-name/<int:user_id>', methods=['PUT'])
def admin_update_display_name(user_id):
    """Update a player's display name (admin only)"""
    try:
        data = request.json
        new_display_name = data.get('display_name')

        if not new_display_name:
            return jsonify({'error': 'Display name is required'}), 400

        # Get user info first
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'Player not found'}), 404

        # Update the display name
        success = User.update_display_name(user_id, new_display_name)

        if success:
            logger.info(f"Admin updated display name for user {user_id} from '{user['display_name']}' to '{new_display_name}'")
            return jsonify({
                'success': True,
                'message': f"Updated display name from '{user['display_name']}' to '{new_display_name}'"
            })
        else:
            return jsonify({'error': 'Failed to update display name or name already taken'}), 400

    except Exception as e:
        logger.error(f"Error updating display name for user {user_id}: {e}")
        return jsonify({'error': 'Failed to update display name'}), 500

@app.route('/api/admin/boards', methods=['GET'])
def admin_get_all_boards():
    """Get all boards with user info (admin only)"""
    try:
        boards = Board.get_all_with_users()
        return jsonify(boards)

    except Exception as e:
        logger.error(f"Error getting all boards: {e}")
        return jsonify({'error': 'Failed to get boards'}), 500

@app.route('/api/admin/boards/<int:user_id>/progress', methods=['PUT'])
def admin_update_board_progress(user_id):
    """Update a player's board progress (admin only)"""
    try:
        data = request.json
        marked_cells = data.get('marked_cells', [])
        user_images = data.get('user_images', {})
        score = data.get('score', 0)

        # Get the user's board
        board = Board.get_by_user(user_id)
        if not board:
            return jsonify({'error': 'No board found for this user'}), 404

        # Update progress
        progress = Progress.create_or_update(user_id, board['id'], marked_cells, score, user_images)

        if progress:
            user = User.get_by_id(user_id)
            logger.info(f"Admin updated board progress for '{user['display_name'] if user else 'Unknown'}' (ID: {user_id})")
            return jsonify(progress)
        else:
            return jsonify({'error': 'Failed to update progress'}), 500

    except Exception as e:
        logger.error(f"Error updating board progress for user {user_id}: {e}")
        return jsonify({'error': 'Failed to update board progress'}), 500

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

                # Resize to max dimensions while maintaining aspect ratio
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=IMAGE_QUALITY)





            # Return the relative path for frontend use
            relative_path = f"/user-images/{user_id}/{board_id}/{filename}"
            return jsonify({'success': True, 'image_path': relative_path})

        except Exception as e:
            logger.error(f"Error processing uploaded image: {e}")
            return jsonify({'error': 'Failed to process image'}), 500

    return jsonify({'error': 'Invalid file type'}), 400



# Production build serving routes
@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files from React build"""
    return send_from_directory('client/build/static', path)

@app.route('/user-images/<path:path>')
def serve_user_images(path):
    """Serve user uploaded images"""
    return send_from_directory('client/public/user-images', path)

@app.route('/thumbnails/<path:path>')
def serve_thumbnails(path):
    """Serve thumbnail images from build"""
    return send_from_directory('client/build/thumbnails', path)

@app.route('/Portraits/<path:path>')
def serve_portraits(path):
    """Serve portrait images from build"""
    return send_from_directory('client/build/Portraits', path)

@app.route('/frames/<path:path>')
def serve_frames(path):
    """Serve frame images from build"""
    return send_from_directory('client/build/frames', path)

@app.route('/How To/<path:path>')
def serve_how_to(path):
    """Serve how-to images from build"""
    return send_from_directory('client/build/How To', path)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app for all non-API routes"""
    # If it's an API route, let Flask handle it normally
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404

    # For all other routes, serve the React app
    try:
        return send_from_directory('client/build', 'index.html')
    except Exception as e:
        logger.error(f"Error serving React app: {e}")
        return jsonify({'error': 'Failed to serve application'}), 500

if __name__ == '__main__':
    print("Starting Bingo Hunter production server...")
    print("Build directory exists:", os.path.exists('client/build'))
    print("Index.html exists:", os.path.exists('client/build/index.html'))
    print(f"Server will be available at: http://localhost:{DEFAULT_PORT}")
    app.run(debug=DEBUG_MODE, host=DEFAULT_HOST, port=DEFAULT_PORT)

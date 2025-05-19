# app.py
from flask import Flask, jsonify, send_from_directory, request
import os
import random
import characters
import tools
import os.path

app = Flask(__name__, static_folder='resources')

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

@app.route('/resources/<path:path>')
def serve_resources(path):
    """Serve static resources"""
    # Serve the file from the resources directory
    return send_from_directory('resources', path)

if __name__ == '__main__':
    app.run(debug=True)

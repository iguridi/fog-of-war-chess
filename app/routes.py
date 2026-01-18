"""Flask routes for the chess game."""
from flask import Blueprint, render_template, jsonify, request
from app.game import Game

main = Blueprint('main', __name__)

game = None


def get_game():
    """Get or create the game instance."""
    global game
    if game is None:
        game = Game()
    return game


@main.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')


@main.route('/api/state')
def get_state():
    """Get the current game state with fog-of-war applied."""
    g = get_game()
    return jsonify(g.get_visible_state())


@main.route('/api/move', methods=['POST'])
def make_move():
    """Make a move and get AI response."""
    g = get_game()
    data = request.get_json()
    from_pos = tuple(data['from'])
    to_pos = tuple(data['to'])
    promotion = data.get('promotion')

    result = g.make_player_move(from_pos, to_pos, promotion)
    return jsonify(result)


@main.route('/api/new-game', methods=['POST'])
def new_game():
    """Start a new game."""
    global game
    game = Game()
    return jsonify(game.get_visible_state())

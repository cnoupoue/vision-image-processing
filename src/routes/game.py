from flask import Blueprint, jsonify
from game.engine import game_instance

game_bp = Blueprint('game_bp', __name__)

@game_bp.route('/state')
def get_game_state():
    return jsonify(game_instance.get_state())

@game_bp.route('/roll')
def roll_dice():
    result = game_instance.roll_dice()
    return jsonify({'roll': result, 'state': game_instance.get_state()})
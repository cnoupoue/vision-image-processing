from flask import Blueprint, jsonify
from game.engine import game_instance

game_bp = Blueprint('game_bp', __name__)

@game_bp.route('/state')
def get_game_state():
    return jsonify(game_instance.get_state())

@game_bp.route('/next-turn')
def next_turn():
    # On appelle la méthode du moteur qui change de joueur
    game_instance.next_turn()
    return jsonify({'state': game_instance.get_state()})

@game_bp.route('/buy')
def buy_property():
    # On appelle la méthode d'achat du moteur
    success, msg = game_instance.buy_current_property()
    return jsonify({
        'success': success,
        'message': msg,
        'state': game_instance.get_state()
    })

@game_bp.route('/start')
def start_game():
    game_instance.start_game()
    return jsonify({'state': game_instance.get_state()})
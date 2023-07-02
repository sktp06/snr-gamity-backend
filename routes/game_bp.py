from flask import Blueprint
from controllers.gameController import GameController


class GameBlueprint:
    game_bp = Blueprint('game_bp', __name__, url_prefix='/game')
    game_bp.route('/stat', methods=['GET'])(GameController.get_game_statistics)
    game_bp.route('/data', methods=['GET'])(GameController.get_games)
    game_bp.route('/genre', methods=['GET'])(GameController.get_games_genre)
    game_bp.route('/search', methods=['POST'])(GameController.search)
    game_bp.route('/name', methods=['POST'])(GameController.query_name)
    game_bp.route('/summary', methods=['POST'])(GameController.query_summary)


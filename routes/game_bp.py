from flask import Blueprint
from controllers.gameController import GameController


class GameBlueprint:
    game_bp = Blueprint('game_bp', __name__, url_prefix='/game')
    game_bp.route('/name', methods=['POST'])(GameController.query_name)
    game_bp.route('/summary', methods=['POST'])(GameController.query_summary)


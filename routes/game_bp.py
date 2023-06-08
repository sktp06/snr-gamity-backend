from flask import Blueprint, current_app
from controllers.gameController import GameController


class GameBlueprint:
    game_bp = Blueprint('game_bp', __name__, url_prefix='/game')
    game_bp.route('/', methods=['POST'])(GameController.get_game_data)

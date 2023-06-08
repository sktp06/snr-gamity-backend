from flask import Blueprint
from controllers.authController import AuthController


class AuthBlueprint:
    auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
    auth_bp.route('/', methods=['POST'])(AuthController.auth)


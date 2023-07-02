import bcrypt
import jwt
import datetime
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy

from models.user import User

db = SQLAlchemy()


class AuthController:
    @staticmethod
    def auth():
        try:
            username = request.get_json()['username']
            password = request.get_json()['password']

            # Check if the username exists in the user table
            user = User.query.filter_by(username=username).first()

            if user:
                # User exists, perform user login authentication
                if bcrypt.checkpw(password.encode('utf-8'), bytes(user.password, 'utf-8')):
                    user_serialize = user.serialize
                    token = jwt.encode(
                        {'user': user_serialize, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                        'Bearer')
                    return jsonify({'user': user_serialize, 'token': token}), 200
                else:
                    return jsonify({'message': 'Invalid password'}), 401
            else:
                return jsonify({'message': 'Invalid username'}), 401

        except KeyError:
            return jsonify({'message': 'The request body requires username and password'}), 400

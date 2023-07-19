import bcrypt
import jwt
import datetime
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

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

    @staticmethod
    def register():
        try:
            username = request.get_json()['username']
            password = request.get_json()['password']

            if username is None or password is None:
                return jsonify({'message': 'The username and password cannot be null'}), 400

            # Check if the username already exists in the user table
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                return jsonify({'message': 'Username already exists'}), 400

            # Validate username and password format
            if not re.match(r'^[a-zA-Z0-9]+$', username):
                return jsonify({'message': 'Username should only contain alphanumeric characters'}), 400

            if not isinstance(password, str) or len(password) < 6:
                return jsonify({'message': 'Password should be a string with at least 6 characters'}), 400

            # Set the default role for the user
            default_role = 'user'

            # Create a new user
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user = User(username=username, password=hashed_password, role=default_role)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({'message': 'Registration successful'}), 201

        except KeyError:
            return jsonify({'message': 'The request body requires username and password'}), 400


import bcrypt
import jwt
import datetime
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy

from models.user import User
from models.admin import Admin

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
                # Check if the username exists in the admin table
                admin = Admin.query.filter_by(username=username).first()

                if admin:
                    # Admin exists, perform admin login authentication
                    if bcrypt.checkpw(password.encode('utf-8'), bytes(admin.password, 'utf-8')):
                        admin_serialize = admin.serialize
                        token = jwt.encode(
                            {'admin': admin_serialize, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                            'Bearer')
                        return jsonify({'admin': admin_serialize, 'token': token}), 200
                    else:
                        return jsonify({'message': 'Invalid password'}), 401
                else:
                    # User or admin does not exist, perform sign up as user
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    new_user = User(username=username, password=hashed_password, game_id=None, role='user')
                    db.session.add(new_user)
                    db.session.commit()

                    return jsonify({'message': 'User created successfully'}), 201

        except KeyError:
            return jsonify({'message': 'The request body requires username and password'}), 400

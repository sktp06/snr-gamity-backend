import json
import logging
import math
import os
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from gensim.models import Word2Vec
from passlib.handlers.bcrypt import bcrypt
from sklearn.metrics.pairwise import cosine_similarity
from spellchecker import SpellChecker
from sqlalchemy_utils.functions import database_exists, create_database

from models import Bookmark, User
from routes.auth_bp import AuthBlueprint
from routes.bookmark_bp import BookmarkBlueprint
from models.database import db
import pickle
import datetime

spell_checker = SpellChecker(language='en')

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})
app.config.from_object('config')

if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
    print('Creating a database')
    create_database(app.config["SQLALCHEMY_DATABASE_URI"])

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(AuthBlueprint.auth_bp)
app.register_blueprint(BookmarkBlueprint.bookmark_bp)


@app.route('/game/data', methods=['GET'])
def get_games():
    with open('assets/parsed_data.pkl', 'rb') as file:
        games = pickle.load(file)
    results = pd.DataFrame(games)

    return results.to_json(orient='records')


@app.route('/game/stat', methods=['GET'])
def get_game_statistics():
    parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
    total_games = len(parsed_data)

    genre_counts = parsed_data['genres'].explode().value_counts().to_dict()
    total_genres = len(genre_counts)

    # Get the modification time of the clean_data.py file
    clean_data_file = os.path.join(os.path.dirname(__file__), 'utils/game_time_data.py')
    modification_time = os.path.getmtime(clean_data_file)
    update_date = datetime.datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d')

    game_information = {
        'update_date': update_date,
        'total_games': total_games,
        'total_genres': total_genres,
        'genre_counts': genre_counts
    }

    return jsonify({'content': game_information}), 200


@app.route('/bookmarks/', methods=['POST'])
def getBookmarkByUserId():
    userId = request.json['userId']
    bookmarks = Bookmark.query.filter_by(user_id=userId).all()
    if not bookmarks:
        return jsonify({'message': 'The bookmark list is empty'}), 404

    games = []
    parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
    for b in bookmarks:
        temp = parsed_data[parsed_data['id'] == b.game_id].to_dict('records')[0]
        games.append({'id': temp['id'],
                      'name': temp['name'],
                      'cover': temp['cover'],
                      'release_dates': temp['release_dates'],
                      'unclean_summary': temp['unclean_summary'],
                      'genres': temp['genres'],
                      'main_story': temp['main_story'],
                      'main_extra': temp['main_extra'],
                      'completionist': temp['completionist'],
                      'websites': temp['websites'],
                      'aggregated_rating': temp['aggregated_rating'] if not math.isnan(
                          temp['aggregated_rating']) else 0,
                      'rating': temp['rating'] if not math.isnan(temp['rating']) else 0,
                      })
    return jsonify({'games': games}), 200


@app.route('/bookmarks/add', methods=['POST'])
def addBookmark():
    try:
        userId = request.json['userId']
        gameId = request.json['gameId']
        bookmark = Bookmark(userId, gameId)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'message': 'The bookmark has been added successfully'}), 200
    except:
        return jsonify({'message': 'Failed to add, maybe you already have this game in the list.'}), 400


@app.route('/auth/register', methods=['POST'])
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
            return jsonify({'message': 'Username should only contain alphanumeric characters(A-Z, a-z, 0-9)'}), 400

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


# @app.route('/game/name', methods=['POST'])
# def query_name():
#     query = request.args.get('query')
#     spell_corr = [spell_checker.correction(w) for w in query.split()]
#     parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
#     results = parsed_data[parsed_data['name'].str.contains(query, case=False)]
#     return results.to_json(orient='records')
#
#
# @app.route('/game/summary', methods=['POST'])
# def query_summary():
#     query = request.args.get('query')
#     spell_corr = [spell_checker.correction(w) for w in query.split()]
#     parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
#     results = parsed_data[parsed_data['summary'].str.contains(query, case=False)]
#     return results.to_json(orient='records')


# @app.route('/game/search', methods=['POST'])
# def search():
#     query = request.args.get('query')
#     spell_corr = [spell_checker.correction(w) for w in query.split()]
#     parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
#     results = parsed_data[
#         parsed_data['name'].str.contains(query, case=False) | parsed_data['summary'].str.contains(query, case=False)]
#
#     return results.to_json(orient='records')


# @app.route('/correction', methods=['GET'])
# def correction():
#     query = request.args['query']
#     spell_corr = [spell_checker.correction(w) for w in query.split()]
#     if spell_corr[0] == None:
#         return 'No correction'
#     return jsonify(' '.join(spell_corr))

@app.route('/bookmarks/recommend', methods=['POST'])
def recommendGames():
    try:
        userId = request.json['userId']
        user_bookmarks = Bookmark.query.filter_by(user_id=userId).all()
        if not user_bookmarks:
            return jsonify({'message': 'No bookmarks found for this user'}), 404

        parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

        # Load or train Word2Vec model on game descriptions
        descriptions = parsed_data['unclean_summary'].tolist()
        model = Word2Vec(sentences=descriptions, vector_size=100, window=5, min_count=1, sg=0)

        # Extract genres for user's bookmarked games
        user_genres = set()
        for b in user_bookmarks:
            temp = parsed_data[parsed_data['id'] == b.game_id].to_dict('records')[0]
            user_genres.update(temp['genres'])

        # Find games with similar genres and high aggregated_rating to recommend
        recommended_games = []
        for idx, game in parsed_data.iterrows():
            if len(recommended_games) >= 10:
                break

            if game['id'] not in [b.game_id for b in user_bookmarks]:
                common_genres = user_genres.intersection(game['genres'])
                if common_genres and not math.isnan(game['aggregated_rating']):
                    # Calculate similarity score based on word embeddings
                    similarity_score = model.wv.n_similarity(descriptions, game['unclean_summary'].split())

                    recommended_games.append({
                        'id': game['id'],
                        'name': game['name'],
                        'cover': game['cover'],
                        'genres': game['genres'],
                        'aggregated_rating': game['aggregated_rating'],
                        'rating': game['rating'] if not math.isnan(game['rating']) else 0,
                        'common_genres': list(common_genres),
                        'word_similarity_score': similarity_score
                    })

        recommended_games.sort(key=lambda x: (x['aggregated_rating'], x['rating'], x['word_similarity_score']),
                               reverse=True)
        recommended_games = recommended_games[:20]  # Keep only the top 20 recommendations

        return jsonify({'recommended_games': recommended_games}), 200
    except:
        return jsonify({'message': 'Failed to recommend games'}), 400


if __name__ == '__main__':
    app.run(debug=False)

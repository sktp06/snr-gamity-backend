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

logging.basicConfig(level=logging.DEBUG)
@app.route('/bookmarks/recommend', methods=['POST'])
def recommendGamesByBookmarks():
    try:
        userId = request.json['userId']
        logging.debug("User ID: %s", userId)  # Debugging

        bookmarks = Bookmark.query.filter_by(user_id=userId).all()
        logging.debug("Bookmarks: %s", bookmarks)  # Debugging

        if not bookmarks:
            return jsonify({'message': 'The bookmark list is empty'}), 404

        # Load parsed game data
        logging.debug("Loading parsed data...")  # Debugging
        parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
        logging.debug("Parsed data loaded successfully.")  # Debugging

        # Extract unclean summaries and game IDs from bookmarks
        bookmarked_game_ids = [b.game_id for b in bookmarks]
        logging.debug("Bookmarked game IDs: %s", bookmarked_game_ids)  # Debugging

        unclean_summaries = [parsed_data[parsed_data['id'] == game_id]['unclean_summary'].values[0] for game_id in
                             bookmarked_game_ids]
        logging.debug("Unclean summaries: %s", unclean_summaries)
        # Train Word2Vec model
        vector_size = 300
        word2vec_model = Word2Vec(sentences=[summary.split() for summary in unclean_summaries],
                                  vector_size=vector_size, window=5, min_count=2, workers=-1)

        # Define a function to get the vector representation of a game summary
        def get_game_vector(unclean_summary):
            words = unclean_summary.split()
            vector_sum = np.zeros(word2vec_model.vector_size)
            count = 0
            for word in words:
                if word in word2vec_model.wv:
                    vector_sum += word2vec_model.wv[word]
                    count += 1
            if count > 0:
                return vector_sum / count
            return vector_sum

        # Calculate similarity scores using Word2Vec vectors
        target_word2vec_vectors = [get_game_vector(summary) for summary in unclean_summaries]
        word2vec_similarity_scores = cosine_similarity(target_word2vec_vectors, target_word2vec_vectors).flatten()

        # Get recommended games based on similarity
        num_recommendations = 5
        sorted_indices = np.argsort(word2vec_similarity_scores)[::-1]
        recommended_indices = sorted_indices[1:num_recommendations + 1]
        recommended_game_ids = [bookmarked_game_ids[idx] for idx in recommended_indices]

        # Create a list of recommended game details
        recommended_games = []
        for game_id in recommended_game_ids:
            temp = parsed_data[parsed_data['id'] == game_id].to_dict('records')[0]
            recommended_games.append({
                'id': temp['id'],
                'name': temp['name'],
                'cover': temp['cover'],
                'release_dates': temp['release_dates'],
                'unclean_summary': temp['unclean_summary'],
                'genres': temp['genres'],
                'main_story': temp['main_story'],
                'main_extra': temp['main_extra'],
                'completionist': temp['completionist'],
                'websites': temp['websites'],
                'aggregated_rating': temp['aggregated_rating'] if not math.isnan(temp['aggregated_rating']) else 0,
                'rating': temp['rating'] if not math.isnan(temp['rating']) else 0,
            })

        return jsonify({'recommended_games': recommended_games}), 200
    except:
        # Handle exceptions and errors
        return jsonify({'message': 'Failed to recommend games'}), 400


if __name__ == '__main__':
    app.run(debug=False)

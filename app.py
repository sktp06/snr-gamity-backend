import ast
import json
import math
import os
import re
from datetime import datetime
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from passlib.handlers.bcrypt import bcrypt
from spellchecker import SpellChecker
from sqlalchemy import desc, or_
from sqlalchemy_utils.functions import database_exists, create_database

from models import Bookmark, User
from models.recommend import Recommend
from models.topGame import TopGame
from models.gamePlay import GamePlay
from models.upComingGame import UpcomingGame
from models.game import Game
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
    # Query the database to retrieve data from the TopGame table
    top_games = TopGame.query.all()

    # Create a list to store the top games
    games = []

    # Iterate over each game
    for game in top_games:
        # Convert the string representation of genres to a list of strings
        genres = ast.literal_eval(game.genres)

        # Convert the game to a dictionary
        game_dict = {
            "id": game.id,
            "cover": game.cover,
            "genres": genres,  # Assign the converted list
            "name": game.name,
            "summary": game.summary,
            "url": game.url,
            "websites": ast.literal_eval(game.websites),  # Convert websites to a list
            "main_story": game.main_story,
            "main_extra": game.main_extra,
            "completionist": game.completionist,
            "aggregated_rating": game.aggregated_rating,
            "aggregated_rating_count": game.aggregated_rating_count,
            "rating": game.rating,
            "rating_count": game.rating_count,
            "release_dates": game.release_dates,
            "storyline": game.storyline,
            "unclean_name": game.unclean_name,
            "unclean_summary": game.unclean_summary,
            "popularity": game.popularity
        }
        games.append(game_dict)

    # Return the list of games
    return jsonify({'content': games}), 200


@app.route('/game/stat', methods=['GET'])
def get_game_statistics():
    parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
    total_games = len(parsed_data)

    genre_counts = parsed_data['genres'].explode().value_counts().to_dict()
    total_genres = len(genre_counts)

    upcoming_data = pickle.load(open('assets/upcoming_games.pkl', 'rb'))
    total_upcoming_games = len(upcoming_data)

    # Get the modification time of the clean_data.py file
    clean_data_file = os.path.join(os.path.dirname(__file__), 'utils/game_time_data.py')
    modification_time = os.path.getmtime(clean_data_file)
    update_date = datetime.datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d')

    game_information = {
        'update_date': update_date,
        'total_games': total_games,
        'total_genres': total_genres,
        'genre_counts': genre_counts,
        'total_upcoming_games': total_upcoming_games,
    }

    return jsonify({'content': game_information}), 200


@app.route('/game/clean_data', methods=['GET'])
def get_clean_gameplay():
    gameplay = GamePlay.query.all()

    # Create a list to store the top games
    games = []

    # Iterate over each game
    for game in gameplay:
        # Convert the game to a dictionary
        game_dict = {
            "id": game.id,
            "cover": game.cover,
            "genres": ast.literal_eval(game.genres),  # Assign the converted list
            "name": game.name,
            "summary": game.summary,
            "url": game.url,
            "websites": ast.literal_eval(game.websites),  # Convert websites to a list
            "main_story": game.main_story,
            "main_extra": game.main_extra,
            "completionist": game.completionist,
            "aggregated_rating": game.aggregated_rating,
            "aggregated_rating_count": game.aggregated_rating_count,
            "rating": game.rating,
            "rating_count": game.rating_count,
            "release_dates": game.release_dates,
            "storyline": game.storyline,
            "unclean_name": game.unclean_name,
            "unclean_summary": game.unclean_summary,
            "popularity": game.popularity
        }
        games.append(game_dict)

    # Return the list of games
    return jsonify({'content': games}), 200


@app.route('/game/upcoming', methods=['GET'])
def get_upcoming():
    upcoming_games = UpcomingGame.query.all()

    # Create a list to store the top games
    games = []

    # Iterate over each game
    for game in upcoming_games:
        # Convert the string representation of genres to a list of strings
        genres = ast.literal_eval(game.genres)

        # Convert the game to a dictionary
        game_dict = {
            "id": game.id,
            "cover": game.cover,
            "genres": genres,  # Assign the converted list
            "name": game.name,
            "summary": game.summary,
            "url": game.url,
            "websites": ast.literal_eval(game.websites),  # Convert websites to a list
            "main_story": game.main_story,
            "main_extra": game.main_extra,
            "completionist": game.completionist,
            "aggregated_rating": game.aggregated_rating,
            "aggregated_rating_count": game.aggregated_rating_count,
            "rating": game.rating,
            "rating_count": game.rating_count,
            "release_dates": game.release_dates,
            "storyline": game.storyline,
            "unclean_name": game.unclean_name,
            "unclean_summary": game.unclean_summary,
            "popularity": game.popularity
        }
        games.append(game_dict)

    # Return the list of games
    return jsonify({'content': games}), 200


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
                      'unclean_name': temp['unclean_name'],
                      'url': temp['url'],
                      'cover': temp['cover'],
                      'release_dates': temp['release_dates'],
                      'unclean_summary': temp['unclean_summary'],
                      'genres': ast.literal_eval(temp['genres']),
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


@app.route('/bookmarks/recommend', methods=['POST'])
def recommendGames():
    try:
        userId = request.json['userId']
        bookmarks = Bookmark.query.filter_by(user_id=userId).all()

        if not bookmarks:
            return jsonify({'message': 'No bookmarks found for this user'}), 404

        # Query the recommendation table and order by composite_score in descending order
        recommended_games = (
            Recommend.query
            .filter(Recommend.game_id.in_([bookmark.game_id for bookmark in bookmarks]))
            .order_by(desc(Recommend.composite_score))
            .limit(10)
            .all()
        )

        # Load the parsed data as a dictionary
        parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

        # Create a list to store the recommended games
        matching_games = []

        for game in recommended_games:
            game_id = game.recommended_game_id

            # Check if the game is already in the bookmarks
            if any(bookmark.game_id == game_id for bookmark in bookmarks):
                continue  # Skip this game if it's in bookmarks

            filtered_data = parsed_data[parsed_data['id'] == game_id]

            if not filtered_data.empty:
                temp = filtered_data.to_dict('records')[0]
                matching_games.append({
                    'id': game_id,
                    'composite_score': game.composite_score,
                    'name': temp['name'],
                    'unclean_name': temp['unclean_name'],
                    'url': temp['url'],
                    'cover': temp['cover'],
                    'release_dates': temp['release_dates'],
                    'unclean_summary': temp['unclean_summary'],
                    'genres': ast.literal_eval(temp['genres']),
                    'main_story': temp['main_story'],
                    'main_extra': temp['main_extra'],
                    'completionist': temp['completionist'],
                    'websites': temp['websites'],
                    'aggregated_rating': (
                        temp['aggregated_rating'] if not math.isnan(temp['aggregated_rating']) else 0
                    ),
                    'rating': temp['rating'] if not math.isnan(temp['rating']) else 0,
                })

        return jsonify({'recommended_games': matching_games}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to generate recommendations', 'error': str(e)}), 500

@app.route('/game/search', methods=['POST'])
def search():
    query = request.json['query']
    corrected_query = " ".join([spell_checker.correction(word) for word in query.split()])

    # Perform a database query to search for games
    results = Game.query.filter(
        or_(
            Game.name.ilike(f'%{corrected_query}%'),
            Game.summary.ilike(f'%{corrected_query}%')
        )
    ).all()

    # Convert the query results to a list of dictionaries with genres and websites as lists
    games = []
    for game in results:
        game_dict = {
            "id": game.id,
            "cover": game.cover,
            "genres": ast.literal_eval(game.genres),  # Assign the converted list
            "name": game.name,
            "summary": game.summary,
            "url": game.url,
            "websites": ast.literal_eval(game.websites),  # Convert websites to a list
            "main_story": game.main_story,
            "main_extra": game.main_extra,
            "completionist": game.completionist,
            "aggregated_rating": game.aggregated_rating,
            "aggregated_rating_count": game.aggregated_rating_count,
            "rating": game.rating,
            "rating_count": game.rating_count,
            "release_dates": game.release_dates,
            "storyline": game.storyline,
            "unclean_name": game.unclean_name,
            "unclean_summary": game.unclean_summary,
            "popularity": game.popularity
        }
        games.append(game_dict)

    return jsonify({
        'query': query,
        'corrected_query': corrected_query,
        'content': games
    }), 200


if __name__ == '__main__':
    app.run(debug=False)

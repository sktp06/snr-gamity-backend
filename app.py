import math
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from passlib.handlers.bcrypt import bcrypt
from spellchecker import SpellChecker
from sqlalchemy_utils.functions import database_exists, create_database

from models import Bookmark, User
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
    with open('assets/limit_games.pkl', 'rb') as file:
        games = pickle.load(file)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(games)

    # Create an empty list to store the top games for each genre
    top_games_by_genre = []

    # Iterate over each genre
    for genre in df['genres'].explode().unique():
        # Filter the DataFrame for games with the current genre
        genre_df = df[df['genres'].apply(lambda x: genre in x)]

        # Sort by popularity score and rating score in descending order
        sorted_games = genre_df.sort_values(by=['popularity'], ascending=[False])

        # Append the top games for the current genre to the list
        top_games_by_genre.append(sorted_games)

    # Concatenate the list of DataFrames into a single DataFrame
    result_df = pd.concat(top_games_by_genre)

    # Drop duplicate games based on 'id'
    result_df = result_df.drop_duplicates(subset='id')

    # Convert the DataFrame to a JSON string with 'records' orientation
    json_result = result_df.to_json(orient='records')

    return json_result, 200

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


@app.route('/game/clean_data', methods=['GET'])
def get_clean_gameplay():
    with open('assets/clean_gameplay.pkl', 'rb') as file:
        games = pickle.load(file)
    results = pd.DataFrame(games)

    return results.to_json(orient='records')


@app.route('/game/upcoming', methods=['GET'])
def get_upcoming():
    with open('assets/parsed_data.pkl', 'rb') as file:
        games = pickle.load(file)
    results = pd.DataFrame(games)

    return results.to_json(orient='records')


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
#
#     # Apply spell correction to each word in the query
#     corrected_query_words = [spell_checker.correction(word) for word in query.split()]
#     corrected_query = ' '.join(corrected_query_words)
#
#     # Load the clean_gameplay data
#     with open('clean_gameplay.pkl', 'rb') as file:
#         clean_gameplay_data = pickle.load(file)
#
#     # Convert the data to a DataFrame
#     df = pd.DataFrame(clean_gameplay_data)
#
#     # Search in both 'name' and 'summary' columns
#     results = df[df['name'].str.contains(corrected_query, case=False) |
#                  df['summary'].str.contains(corrected_query, case=False)]
#
#     # Convert the DataFrame to a dictionary with 'records' orientation
#     results_dict = results.to_dict('records')
#
#     return jsonify({
#         'query': query,
#         'corrected_query': corrected_query,
#         'results': results_dict
#     }), 200


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
        bookmarks = Bookmark.query.filter_by(user_id=userId).all()

        if not bookmarks:
            return jsonify({'message': 'No bookmarks found for this user'}), 404

        # Load the pre-computed recommendations
        with open('assets/all_recommendations.pkl', 'rb') as file:
            all_recommendations = pickle.load(file)

        recommended_games_dict = {}  # Dictionary to store top recommendations for each bookmarked game

        for bookmark in bookmarks:
            game_id = bookmark.game_id
            recommended_for_game = all_recommendations.get(str(game_id), [])
            recommended_for_game.sort(key=lambda x: float(x['composite_score']), reverse=True)
            top_recommended_for_game = recommended_for_game[:10]  # Retrieve the top 10 recommendations

            recommended_games_dict[str(game_id)] = top_recommended_for_game

        # Load the parsed data as a dictionary
        parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

        matching_games = []

        for game_id, top_recommendations in recommended_games_dict.items():
            for recommended_game in top_recommendations:
                if recommended_game['id'] != int(
                        game_id):  # Check if the recommended game is not the same as the bookmarked game
                    filtered_data = parsed_data[parsed_data['id'] == recommended_game['id']]
                    if not filtered_data.empty:
                        temp = filtered_data.to_dict('records')[0]
                        matching_games.append({
                            'id': recommended_game['id'],
                            'composite_score': recommended_game['composite_score'],
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

        return jsonify({'recommended_games': matching_games}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to generate recommendations', 'error': str(e)}), 500


@app.route('/game/search', methods=['POST'])
def search():
    query = request.json['query']
    spell_corr = [spell_checker.correction(w) for w in query.split()]

    with open('assets/clean_gameplay.pkl', 'rb') as file:
        parsed_data = pickle.load(file)

    results = parsed_data[
        parsed_data['name'].str.contains(query, case=False) |
        parsed_data['summary'].str.contains(query, case=False)
        ]

    return jsonify({
        'query': query,
        'spell_corr': spell_corr,
        'results_name': results.to_dict('records')
    }), 200

@app.route('/game/insert_data', methods=['POST'])
def insert_data():
    try:
        # Read the CSV file and parse the data
        data = pd.read_csv('assets/parsed_data.csv')
        data = data.replace({np.nan: None})

        # Iterate through the rows of the DataFrame and insert them into the database
        for index, row in data.iterrows():
            game = Game(
                id=row['id'],
                aggregated_rating=row['aggregated_rating'],
                aggregated_rating_count=row['aggregated_rating_count'],
                cover=row['cover'],
                genres=row['genres'],
                name=row['name'],
                rating=row['rating'],
                rating_count=row['rating_count'],
                release_dates=row['release_dates'],
                summary=row['summary'],
                url=row['url'],
                websites=row['websites'],
                main_story=row['main_story'],
                main_extra=row['main_extra'],
                completionist=row['completionist'],
                storyline=row['storyline'],
                unclean_summary=row['unclean_summary'],
                popularity=row['popularity']
            )

            db.session.add(game)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': 'Data inserted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to insert data', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False)

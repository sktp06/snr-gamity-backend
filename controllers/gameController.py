import ast
import os
from datetime import datetime
import pandas as pd
from flask import jsonify, request
import pickle
from spellchecker import SpellChecker

from models.game import Game
from models.topGame import TopGame
from sqlalchemy import or_

spell_checker = SpellChecker(language='en')


class GameController:
    @staticmethod
    def get_games():
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

    @staticmethod
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

    @staticmethod
    def get_clean_gameplay():
        with open('clean_gameplay.pkl', 'rb') as file:
            games = pickle.load(file)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(games)

        # Convert the DataFrame to a dictionary with 'records' orientation
        game_dict = df.to_dict('records')

        return jsonify({'content': game_dict}), 200

    @staticmethod
    def get_upcoming():
        upcoming_games = TopGame.query.all()

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

    @staticmethod
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

        # Convert the query results to a list of dictionaries
        games = [game.serialize for game in results]

        return jsonify({
            'query': query,
            'corrected_query': corrected_query,
            'content': games
        }), 200






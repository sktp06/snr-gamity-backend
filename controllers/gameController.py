import ast
import os
from datetime import datetime
import pandas as pd
from flask import jsonify, request
import pickle
from spellchecker import SpellChecker

from models.game import Game
from models.gamePlay import GamePlay
from models.gameStat import GameStat
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

    @staticmethod
    def get_game_statistics():
        games_stat = GameStat.query.first()

        if games_stat:
            genre_count = ast.literal_eval(games_stat.genre_count)

            # Transform the genre_count structure
            formatted_genre_count = {}
            for genre, count in genre_count.items():
                formatted_genre = genre[2:-2]  # Remove the square brackets
                formatted_genre_count[formatted_genre] = count

            game_information = {
                "update_date": games_stat.update_date,
                "total_games": games_stat.total_games,
                "total_genres": games_stat.total_genres,
                "genre_counts": formatted_genre_count,  # Changed the key to "genre_counts"
                "total_upcoming_games": games_stat.total_upcoming_games
            }

            return jsonify({'content': game_information}), 200
        else:
            return jsonify({'content': 'No game statistics found'}), 404

    @staticmethod
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

    @staticmethod
    def get_upcoming():
        upcoming_games = TopGame.query.all()

        # Create a list to store the top games
        games = []

        # Iterate over each game
        for game in upcoming_games:

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







# gameControllers.py
from datetime import datetime

import pandas as pd
from flask import jsonify, request
import pickle
from spellchecker import SpellChecker

spell_checker = SpellChecker(language='en')


class GameController:
    @staticmethod
    def get_games():
        with open('parsed_data.pkl', 'rb') as file:
            games = pickle.load(file)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(games)

        # Convert the DataFrame to a dictionary with 'records' orientation
        game_dict = df.to_dict('records')

        return jsonify({'content': game_dict}), 200

    @staticmethod
    def query_name():
        query = request.args.get('query')
        spell_corr = [spell_checker.correction(w) for w in query.split()]
        parsed_data = pickle.load(open('../assets/parsed_data.pkl', 'rb'))
        results = parsed_data[parsed_data['name'].str.contains(query, case=False)]

        return jsonify({'query': query, 'spell_corr': spell_corr, 'content': results.to_dict('records')}), 200

    @staticmethod
    def query_summary():
        query = request.args.get('query')
        spell_corr = [spell_checker.correction(w) for w in query.split()]
        parsed_data = pickle.load(open('../assets/parsed_data.pkl', 'rb'))
        results = parsed_data[parsed_data['summary'].str.contains(query, case=False)]

        return jsonify({'query': query, 'spell_corr': spell_corr, 'content': results.to_dict('records')}), 200

    @staticmethod
    def search():
        query = request.args.get('query')
        spell_corr = [spell_checker.correction(w) for w in query.split()]
        parsed_data = pickle.load(open('../assets/parsed_data.pkl', 'rb'))
        results = parsed_data[parsed_data['name'].str.contains(query, case=False) | parsed_data['summary'].str.contains(query, case=False)]

        return jsonify({'query': query, 'spell_corr': spell_corr, 'results_name': results.to_dict('records')}), 200

    @staticmethod
    def get_game_statistics():
        parsed_data = pickle.load(open('../assets/parsed_data.pkl', 'rb'))
        total_games = len(parsed_data)

        genre_counts = parsed_data['genres'].explode().value_counts().to_dict()
        total_genres = len(genre_counts)

        update_date = datetime.now().strftime('%Y-%m-%d')

        game_information = {
            'update_date': update_date,
            'total_games': total_games,
            'total_genres': total_genres,  # Add total number of genres
            'genre_counts': genre_counts
        }

        return jsonify({'content': game_information}), 200


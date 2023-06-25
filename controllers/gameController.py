# gameControllers.py
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
    def get_games_genre():
        with open('../assets/parsed_data_genre.pkl', 'rb') as file:
            games_genre = pickle.load(file)
        df = pd.DataFrame(games_genre)
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



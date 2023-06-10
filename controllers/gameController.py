# gameControllers.py

from flask import jsonify, request
import pickle
from spellchecker import SpellChecker

spell_checker = SpellChecker(language='en')


class GameController:
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

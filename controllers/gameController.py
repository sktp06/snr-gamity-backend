import os
from datetime import datetime
import pandas as pd
from flask import jsonify, request
import pickle
from spellchecker import SpellChecker

from models import db
from models.game import Game

spell_checker = SpellChecker(language='en')


class GameController:
    @staticmethod
    def get_games():
        with open('assets/limit_games.pkl', 'rb') as file:
            games = pickle.load(file)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(games)

        # Create an empty dictionary to store the top games for each genre
        top_games_by_genre = {}

        # Iterate over each genre
        for genre in df['genres'].explode().unique():
            # Filter the DataFrame for games with the current genre
            genre_df = df[df['genres'].apply(lambda x: genre in x)]

            # Sort by popularity score and rating score in descending order
            sorted_games = genre_df.sort_values(by=['popularity'], ascending=[False])

            # Drop duplicate games within the genre based on some unique identifier, e.g., 'game_id'
            sorted_games = sorted_games.drop_duplicates(subset='id')

            # Convert the DataFrame to a dictionary with 'records' orientation
            game_dict = sorted_games.to_dict('records')

            # Add the games for the current genre to the dictionary
            top_games_by_genre[genre] = game_dict

        return jsonify({'content': top_games_by_genre}), 200

    @staticmethod
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
        with open('assets/upcoming_games.pkl', 'rb') as file:
            games = pickle.load(file)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(games)

        # Convert the DataFrame to a dictionary with 'records' orientation
        game_dict = df.to_dict('records')

        return jsonify({'content': game_dict}), 200


    # @staticmethod
    # def query_name():
    #     query = request.args.get('query')
    #     spell_corr = [spell_checker.correction(w) for w in query.split()]
    #     parsed_data = pickle.load(open('../assets/parsed_data.pkl', 'rb'))
    #     results = parsed_data[parsed_data['name'].str.contains(query, case=False)]
    #
    #     return jsonify({'query': query, 'spell_corr': spell_corr, 'content': results.to_dict('records')}), 200
    #
    # @staticmethod
    # def query_summary():
    #     query = request.args.get('query')
    #     spell_corr = [spell_checker.correction(w) for w in query.split()]
    #     parsed_data = pickle.load(open('../assets/parsed_data.pkl', 'rb'))
    #     results = parsed_data[parsed_data['summary'].str.contains(query, case=False)]
    #
    #     return jsonify({'query': query, 'spell_corr': spell_corr, 'content': results.to_dict('records')}), 200
    #
    @staticmethod
    def search():
        query = request.json['query']
        spell_corr = [spell_checker.correction(w) for w in query.split()]

        with open('../assets/parsed_data.pkl', 'rb') as file:
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

    @staticmethod
    def insert_data():
        try:
            # Read the CSV file and parse the data
            data = pd.read_csv('../assets/parsed_data.csv')

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






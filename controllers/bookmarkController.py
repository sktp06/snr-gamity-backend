import math
import pickle
import pandas as pd
from flask import jsonify, request
from models.bookmark import Bookmark
from models.database import db


class BookmarkController:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def removeBookmark():
        try:
            userId = request.json['userId']
            gameId = request.json['gameId']
            bookmark = Bookmark.query.filter_by(user_id=userId, game_id=gameId).first()
            # if not bookmark:
            #     return jsonify({'message': 'This bookmark does not exist'}), 404
            db.session.delete(bookmark)
            db.session.commit()
            return jsonify({'message': 'The bookmark has been deleted successfully'}), 200
        except:
            return jsonify({'message': 'Failed to remove from the list'}), 400

    @staticmethod
    def recommendGames():
        try:
            userId = request.json['userId']
            bookmarks = Bookmark.query.filter_by(user_id=userId).all()

            if not bookmarks:
                return jsonify({'message': 'No bookmarks found for this user'}), 404

            # Load the pre-computed recommendations
            with open('assets/all_recommendations055.pkl', 'rb') as file:
                all_recommendations = pickle.load(file)

            recommended_games = []

            for bookmark in bookmarks:
                game_id = bookmark.game_id
                recommended_for_game = all_recommendations.get(str(game_id), [])
                recommended_games.extend(recommended_for_game)

            # Load the parsed data as a dictionary
            parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

            # Create a dictionary to store unique games by ID
            unique_games = {}

            for recommended_game in recommended_games:
                game_id = recommended_game['id']

                # Check if the game is already in the bookmarks
                if any(bookmark.game_id == game_id for bookmark in bookmarks):
                    continue  # Skip this game if it's in bookmarks

                if game_id not in unique_games:
                    filtered_data = parsed_data[parsed_data['id'] == game_id]

                    if not filtered_data.empty:
                        temp = filtered_data.to_dict('records')[0]
                        unique_games[game_id] = {
                            'id': game_id,
                            'score': recommended_game['composite_score'],
                            'name': temp['name'],
                            'unclean_name': temp['unclean_name'],
                            'cover': temp['cover'],
                            'release_dates': temp['release_dates'],
                            'unclean_summary': temp['unclean_summary'],
                            'genres': temp['genres'],
                            'main_story': temp['main_story'],
                            'main_extra': temp['main_extra'],
                            'completionist': temp['completionist'],
                            'websites': temp['websites'],
                            'aggregated_rating': (
                                temp['aggregated_rating'] if not math.isnan(temp['aggregated_rating']) else 0
                            ),
                            'rating': temp['rating'] if not math.isnan(temp['rating']) else 0,
                        }

            # Extract the values (unique games) from the dictionary
            matching_games = list(unique_games.values())

            # Sort all recommended games by score
            matching_games.sort(key=lambda x: float(x['score']), reverse=True)

            # Take the top 10 games
            top_10_games = matching_games[:10]

            return jsonify({'recommended_games': top_10_games}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Failed to generate recommendations', 'error': str(e)}), 500

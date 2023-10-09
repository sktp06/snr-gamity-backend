import math
import pickle
import pandas as pd
from flask import jsonify, request
from sqlalchemy import desc

from models.bookmark import Bookmark
from models.database import db
from models.recommend import Recommend


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
                          'url': temp['url'],
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
                        'genres': temp['genres'],
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
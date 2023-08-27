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
            with open('assets/all_recommendations.pkl', 'rb') as file:
                all_recommendations = pickle.load(file)

            recommended_games = []

            for bookmark in bookmarks:
                game_id = bookmark.game_id
                try:
                    recommended_for_game = all_recommendations.get(str(game_id), [])
                    recommended_for_game.sort(key=lambda x: float(x['score']), reverse=True)
                    top_recommended = recommended_for_game[:10]
                except Exception as e:
                    return f"An exception occurred: {str(e)}"

                recommended_games.extend(top_recommended)

            # Sort all recommended games across bookmarks by score
            recommended_games.sort(key=lambda x: float(x['score']), reverse=True)
            top_recommended_across_bookmarks = recommended_games[:10]

            return jsonify({'recommended_games': top_recommended_across_bookmarks}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Failed to generate recommendations', 'error': str(e)}), 500


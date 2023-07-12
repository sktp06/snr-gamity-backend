import math
import pickle

from flask import jsonify, request
from models.bookmark import Bookmark
from models.database import db


class BookmarkController:
    @staticmethod
    def getBookmarkByUserId():
        try:
            userId = request.json['userId']
            bookmarks = Bookmark.query.filter_by(user_id=userId).all()
            if not bookmarks:
                return jsonify({'message': 'The bookmark for userId {} does not exist'.format(userId)}), 404

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
                              'aggregated_rating': temp['aggregated_rating'] if not math.isnan(temp['aggregated_rating']) else 0,
                              'rating': temp['rating'] if not math.isnan(temp['rating']) else 0,
                              })
            return jsonify({'games': games}), 200
        except:
            return jsonify({'message': 'The bookmark for userId {} does not exist'.format(userId)}), 404

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
            if not bookmark:
                return jsonify({'message': 'This bookmark does not exist'}), 404
            db.session.delete(bookmark)
            db.session.commit()
            return jsonify({'message': 'The bookmark has been deleted successfully'}), 200
        except:
            return jsonify({'message': 'Failed to remove from the list'}), 400

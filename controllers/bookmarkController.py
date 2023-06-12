from flask import jsonify, request
from models.bookmark import Bookmark
from flask_sqlalchemy import SQLAlchemy
import pickle
db = SQLAlchemy()
parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))


class BookmarkController:
    @staticmethod
    def getBookmarkByUserId():
        userId = request.get_json()['userId']
        try:
            bookmarks = db.session.query(Bookmark).filter_by(user=userId).all()
            bookmarks = Bookmark.serialize_list(bookmarks)
            if not len(bookmarks):
                raise Exception()
            games = []
            for b in bookmarks:
                games.append(parsed_data[parsed_data['gameId'] == b['gameId']].to_dict('records')[0])
            result = {'userId': userId, 'games': games}
            return jsonify(result)
        except:
            return jsonify({'message': 'The bookmark for userId {} does not exist'.format(userId)})

    @staticmethod
    def addBookmark():
        try:
            userId = request.get_json()['userId']
            gameId = request.get_json()['gameId']
            bookmark = Bookmark(userId, gameId)
            try:
                db.session.add(bookmark)
                db.session.commit()
            except:
                return jsonify({'message': 'Failed to add bookmark'}), 404
            return jsonify({'message': 'The bookmark has been added successfully'})
        except:
            return jsonify({'message': 'The request body requires userId and gameId'}), 400

    @staticmethod
    def removeBookmark():
        try:
            userId = request.get_json()['userId']
            gameId = request.get_json()['gameId']
            bookmark = db.session.query(Bookmark).filter_by(user=userId, gameId=gameId).first()
            try:
                db.session.delete(bookmark)
                db.session.commit()
            except:
                return jsonify({'message': 'This bookmark does not exist'}), 404
            return jsonify({'message': 'The bookmark has been deleted successfully'})
        except:
            return jsonify({'message': 'The request body requires userId and gameId'}), 400

import json
import math
import pickle
import re

import numpy as np
import pandas as pd
from flask import jsonify, request
from gensim.models import Word2Vec
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
            print(1)
            bookmarks = Bookmark.query.filter_by(user_id=userId).all()
            print(2)

            if not bookmarks:
                return jsonify({'message': 'No bookmarks found for this user'}), 404
            print(3)

            # Load the pre-trained recommender model
            with open('assets/recommend_model.pkl', 'rb') as model_file:
                recommender_model = pickle.load(model_file)
            print(4)

            recommended_games = []

            for bookmark in bookmarks:
                game_id = bookmark.game_id
                print(5)
                print(game_id)
                print(recommender_model)
                # Get recommendations from the pre-trained model using the game_id
                if game_id in recommender_model:
                    recommended_for_game = recommender_model[game_id]
                    recommended_games.extend(recommended_for_game)

            return jsonify({'recommended_games': recommended_games}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Failed to generate recommendations', 'error': str(e)}), 500


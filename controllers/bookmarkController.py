import json
import math
import pickle

import numpy as np
from flask import jsonify, request
from gensim.models import Word2Vec
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
            user_bookmarks = Bookmark.query.filter_by(user_id=userId).all()
            if not user_bookmarks:
                return jsonify({'message': 'No bookmarks found for this user'}), 404

            parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

            # Load or train Word2Vec model on game descriptions
            descriptions = parsed_data['unclean_summary'].tolist()
            model = Word2Vec(sentences=descriptions, vector_size=100, window=5, min_count=1, sg=0)

            # Extract genres for user's bookmarked games
            user_genres = set()
            for b in user_bookmarks:
                temp = parsed_data[parsed_data['id'] == b.game_id].to_dict('records')[0]
                user_genres.update(temp['genres'])

            # Find games with similar genres and high aggregated_rating to recommend
            recommended_games = []
            for idx, game in parsed_data.iterrows():
                if len(recommended_games) >= 10:
                    break

                if game['id'] not in [b.game_id for b in user_bookmarks]:
                    common_genres = user_genres.intersection(game['genres'])
                    if common_genres and not math.isnan(game['aggregated_rating']):
                        # Calculate similarity score based on word embeddings
                        similarity_score = model.wv.n_similarity(descriptions, game['unclean_summary'].split())

                        recommended_games.append({
                            'id': game['id'],
                            'name': game['name'],
                            'cover': game['cover'],
                            'genres': game['genres'],
                            'aggregated_rating': game['aggregated_rating'],
                            'rating': game['rating'] if not math.isnan(game['rating']) else 0,
                            'common_genres': list(common_genres),
                            'word_similarity_score': similarity_score
                        })

            recommended_games.sort(key=lambda x: (x['aggregated_rating'], x['rating'], x['word_similarity_score']),
                                   reverse=True)
            recommended_games = recommended_games[:20]  # Keep only the top 20 recommendations

            return jsonify({'recommended_games': recommended_games}), 200
        except:
            return jsonify({'message': 'Failed to recommend games'}), 400
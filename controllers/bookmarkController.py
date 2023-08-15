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
    def recommendGamesByBookmarks():
        try:
            userId = request.json['userId']

            bookmarks = Bookmark.query.filter_by(user_id=userId).all()

            if not bookmarks:
                return jsonify({'message': 'The bookmark list is empty'}), 404

            # Load parsed game data
            parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

            # Extract unclean summaries and game IDs from bookmarks
            bookmarked_game_ids = [b.game_id for b in bookmarks]
            unclean_summaries = [parsed_data[parsed_data['id'] == game_id]['unclean_summary'].values[0] for game_id in
                                 bookmarked_game_ids]

            # Train Word2Vec model
            vector_size = 300
            word2vec_model = Word2Vec(sentences=[summary.split() for summary in unclean_summaries],
                                      vector_size=vector_size, window=5, min_count=2, workers=-1)

            # Define a function to get the vector representation of a game summary
            def get_game_vector(unclean_summary):
                words = unclean_summary.split()
                vector_sum = np.zeros(word2vec_model.vector_size)
                count = 0
                for word in words:
                    if word in word2vec_model.wv:
                        vector_sum += word2vec_model.wv[word]
                        count += 1
                if count > 0:
                    return vector_sum / count
                return vector_sum

            # Calculate similarity scores using Word2Vec vectors
            target_word2vec_vectors = [get_game_vector(summary) for summary in unclean_summaries]
            word2vec_similarity_scores = cosine_similarity(target_word2vec_vectors, target_word2vec_vectors).flatten()

            # Get recommended games based on similarity
            num_recommendations = 5
            sorted_indices = np.argsort(word2vec_similarity_scores)[::-1]
            recommended_indices = sorted_indices[1:num_recommendations + 1]
            recommended_game_ids = [bookmarked_game_ids[idx] for idx in recommended_indices]

            # Create a list of recommended game details
            recommended_games = []
            for game_id in recommended_game_ids:
                temp = parsed_data[parsed_data['id'] == game_id].to_dict('records')[0]
                recommended_games.append({
                    'id': temp['id'],
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

            return jsonify({'recommended_games': recommended_games}), 200
        except:
            # Handle exceptions and errors
            return jsonify({'message': 'Failed to recommend games'}), 400


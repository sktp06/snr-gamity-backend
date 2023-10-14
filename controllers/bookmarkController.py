import ast
from flask import jsonify, request
from sqlalchemy import desc

from models.allGame import AllGame
from models.bookmark import Bookmark
from models.database import db
from models.recommend import Recommend


class BookmarkController:
    @staticmethod
    def getBookmarkByUserId():
        userId = request.json.get('userId')
        bookmarks = Bookmark.query.filter_by(user_id=userId).all()
        if not bookmarks:
            return jsonify({'message': 'The bookmark list is empty'}), 404

        games = []

        for bookmark in bookmarks:
            all_game = AllGame.query.get(bookmark.game_id)
            if all_game:
                game_data = {
                    "id": all_game.id,
                    "cover": all_game.cover,
                    "genres": ast.literal_eval(all_game.genres),  # Assign the converted list
                    "name": all_game.name,
                    "summary": all_game.summary,
                    "url": all_game.url,
                    "websites": ast.literal_eval(all_game.websites),  # Convert websites to a list
                    "main_story": all_game.main_story,
                    "main_extra": all_game.main_extra,
                    "completionist": all_game.completionist,
                    "aggregated_rating": all_game.aggregated_rating,
                    "aggregated_rating_count": all_game.aggregated_rating_count,
                    "rating": all_game.rating,
                    "rating_count": all_game.rating_count,
                    "release_dates": all_game.release_dates,
                    "storyline": all_game.storyline,
                    "unclean_name": all_game.unclean_name,
                    "unclean_summary": all_game.unclean_summary,
                    "popularity": all_game.popularity
                }
                games.append(game_data)

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

            # Create a list to store the recommended games
            matching_games = []

            for game in recommended_games:
                game_id = game.recommended_game_id

                # Check if the game is already in the bookmarks
                if any(bookmark.game_id == game_id for bookmark in bookmarks):
                    continue  # Skip this game if it's in bookmarks

                all_game = AllGame.query.get(game_id)

                if all_game:
                    matching_games.append({
                        "id": all_game.id,
                        "cover": all_game.cover,
                        "genres": ast.literal_eval(all_game.genres),
                        "name": all_game.name,
                        "summary": all_game.summary,
                        "url": all_game.url,
                        "websites": ast.literal_eval(all_game.websites),
                        "main_story": all_game.main_story,
                        "main_extra": all_game.main_extra,
                        "completionist": all_game.completionist,
                        "aggregated_rating": all_game.aggregated_rating,
                        "aggregated_rating_count": all_game.aggregated_rating_count,
                        "rating": all_game.rating,
                        "rating_count": all_game.rating_count,
                        "release_dates": all_game.release_dates,
                        "storyline": all_game.storyline,
                        "unclean_name": all_game.unclean_name,
                        "unclean_summary": all_game.unclean_summary,
                        "popularity": all_game.popularity,
                    })

            return jsonify({'recommended_games': matching_games}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Failed to generate recommendations', 'error': str(e)}), 500

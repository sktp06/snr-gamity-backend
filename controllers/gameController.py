from flask import current_app, jsonify
import pickle


class GameController:
    @staticmethod
    def get_game_data():
        with current_app.app_context():
            parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))

            # Convert the entire DataFrame to a dictionary
            game_dict = parsed_data.to_dict(orient='records')

        # Return the data as a JSON response
        return jsonify(game_dict)

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from spellchecker import SpellChecker
from sqlalchemy_utils.functions import database_exists, create_database

from models import Bookmark
from routes.auth_bp import AuthBlueprint
from routes.bookmark_bp import BookmarkBlueprint
from models.database import db
import pickle

spell_checker = SpellChecker(language='en')

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})
app.config.from_object('config')

if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
    print('Creating a database')
    create_database(app.config["SQLALCHEMY_DATABASE_URI"])

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(AuthBlueprint.auth_bp)
app.register_blueprint(BookmarkBlueprint.bookmark_bp)


@app.route('/game/name', methods=['POST'])
def query_name():
    query = request.args.get('query')
    spell_corr = [spell_checker.correction(w) for w in query.split()]
    parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
    results = parsed_data[parsed_data['name'].str.contains(query, case=False)]
    return results.to_json(orient='records')


@app.route('/game/summary', methods=['POST'])
def query_summary():
    query = request.args.get('query')
    spell_corr = [spell_checker.correction(w) for w in query.split()]
    parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
    results = parsed_data[parsed_data['summary'].str.contains(query, case=False)]
    return results.to_json(orient='records')


@app.route('/game/search', methods=['POST'])
def search():
    query = request.args.get('query')
    spell_corr = [spell_checker.correction(w) for w in query.split()]
    parsed_data = pickle.load(open('assets/parsed_data.pkl', 'rb'))
    results = parsed_data[
        parsed_data['name'].str.contains(query, case=False) | parsed_data['summary'].str.contains(query, case=False)]

    return results.to_json(orient='records')


@app.route('/correction', methods=['GET'])
def correction():
    query = request.args['query']
    spell_corr = [spell_checker.correction(w) for w in query.split()]
    if spell_corr[0] == None:
        return 'No correction'
    return jsonify(' '.join(spell_corr))


@app.route('/game/data', methods=['GET'])
def get_games():
    with open('assets/parsed_data.pkl', 'rb') as file:
        games = pickle.load(file)
    results = pd.DataFrame(games)

    return results.to_json(orient='records')


@app.route('/game/genre', methods=['GET'])
def get_games_genre():
    with open('assets/parsed_data_genre.pkl', 'rb') as file:
        games_genre = pickle.load(file)
    results = pd.DataFrame(games_genre)

    return results.to_json(orient='records')

    # @app.route('/bookmarks/add', methods=['POST'])
    # def add_bookmark():
    #     try:
    #         userId = request.get_json()['userId']
    #         gameId = request.get_json()['gameId']
    #         bookmark = Bookmark(userId, gameId)
    #         try:
    #             db.session.add(bookmark)
    #             db.session.commit()
    #             return jsonify({'message': 'The bookmark has been added successfully'})
    #         except:
    #             return jsonify({'message': 'Failed to add bookmark'}), 404
    #     except:
    #         return jsonify({'message': 'The request body requires userId and gameId'}), 400


if __name__ == '__main__':
    app.run(debug=False)

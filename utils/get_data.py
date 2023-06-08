import json
import requests
from datetime import datetime


class GameDataRetriever:
    def __init__(self):
        self.client_id = 'n0k0ipireherqqmh2fdrtxungi8p0w'
        self.access_token = '6gsrp3s1hxk3vle27abza942jhf4t1'
        self.url = 'https://api.igdb.com/v4/games/'
        self.params = {
            'fields': 'id,name,rating,rating_count,aggregated_rating,aggregated_rating_count,cover.url,genres,'
                      'genres.name,hypes,platforms,platforms.name,release_dates.date,summary,url,websites.category,'
                      'websites.url,storyline',
            'limit': 500
        }
        self.headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }

    def map_website_category(self, category_id):
        category_name = {
            1: 'Official',
            2: 'Wikia',
            3: 'Wikipedia',
            4: 'Facebook',
            5: 'Twitter',
            6: 'Twitch',
            8: 'Instagram',
            9: 'YouTube',
            10: 'iPhone',
            11: 'iPad',
            12: 'Android',
            13: 'Steam',
            14: 'Reddit',
            15: 'Itch',
            16: 'Epic Games',
            17: 'GOG',
            18: 'Discord',
            19: 'Homepage'
        }
        return category_name.get(category_id, '')

    def convert_unix_timestamp(self, timestamp):
        if timestamp is not None and timestamp > 0:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        return None

    def retrieve_game_data(self):
        offset = 0
        limit = 500
        all_games = []
        page = 1

        while True:
            self.params['offset'] = offset
            response = requests.get(self.url, headers=self.headers, params=self.params)

            if response.status_code == 200:
                data = response.json()

                if len(data) == 0:
                    break

                for game in data:
                    release_dates = game.get('release_dates')
                    if release_dates:
                        for date in release_dates:
                            if 'date' in date:
                                timestamp = date['date']
                                date['date'] = self.convert_unix_timestamp(timestamp)

                    websites = game.get('websites')
                    if websites:
                        for website in websites:
                            category_id = website.get('category')
                            category_name = self.map_website_category(category_id)
                            website['category_name'] = category_name

                all_games.extend(data)
                offset += limit
                print(f'Retrieved data for page {page}')
                page += 1
            else:
                print('Error:', response.status_code)
                break

        return all_games

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)

    def execute(self):
        all_games = self.retrieve_game_data()
        json_filename = 'games.json'
        self.save_to_json(all_games, json_filename)
        print(f'Successfully saved the data to {json_filename}')

retriever = GameDataRetriever()
retriever.execute()

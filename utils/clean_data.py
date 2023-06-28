import pandas as pd
import string
import pickle
import numpy as np


class CleanData:
    def get_data(self, path):
        df = pd.read_json(path, orient='records')
        df.drop(columns=['hypes', 'platforms', 'rating_count', 'aggregated_rating_count'], inplace=True)
        df['cover'] = df['cover'].apply(
            lambda x: x['url'].replace('t_thumb', 't_cover_big') if isinstance(x, dict) else '')
        df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

        # Clean release_dates field
        df['release_dates'] = df['release_dates'].apply(
            lambda x: [i['date'] for i in x] if isinstance(x, list) and all('date' in item for item in x) else [])
        df['release_dates'] = df['release_dates'].apply(lambda x: x[0] if len(x) > 0 else '')

        df['websites'] = df['websites'].apply(
            lambda x: [(i['url'], i['category_name']) for i in x] if isinstance(x, list) else [])

        # Cleaning game's name, summary, and storyline
        cleaned_name = df['name']
        cleaned_name = cleaned_name.str.lower()
        cleaned_name = cleaned_name.str.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
        df['name'] = cleaned_name

        cleaned_summary = df['summary']
        cleaned_summary = cleaned_summary.str.lower().fillna('')
        cleaned_summary = cleaned_summary.str.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
        df['summary'] = cleaned_summary

        cleaned_storyline = df['storyline']
        cleaned_storyline = cleaned_storyline.str.lower().fillna('')
        cleaned_storyline = cleaned_storyline.str.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
        df['storyline'] = cleaned_storyline

        # Save cleaned data to parsed_data.pkl
        with open('../assets/parsed_data.pkl', 'wb') as file:
            pickle.dump(df, file)

        genres = df['genres'].explode().unique()
        game_dict = {}

        for genre in genres:
            genre_df = df[df['genres'].apply(lambda x: genre in x)]
            game_dict[genre] = genre_df.to_dict('records')

        # Find the maximum length of game lists
        max_length = max(len(games) for games in game_dict.values())

        # Pad shorter lists with None to match the maximum length
        for genre, games in game_dict.items():
            game_dict[genre] = games + [None] * (max_length - len(games))

        # Save genre-specific data to parsed_data_genre.pkl
        with open('../assets/parsed_data_genre.pkl', 'wb') as file:
            pickle.dump(game_dict, file)

        return game_dict


cleaner = CleanData()
df = cleaner.get_data("../assets/games.json")

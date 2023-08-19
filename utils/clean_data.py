import pandas as pd
import string
import pickle
import re


class CleanData:
    # cleaned_data
    def get_data(self, path):
        df = pd.read_json(path, orient='records')
        df.drop(columns=['hypes', 'platforms'], inplace=True)
        df['cover'] = df['cover'].apply(lambda x: x['url'].replace('t_thumb', 't_cover_big') if isinstance(x, dict) else '')
        df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        # Clean release_dates field
        df['release_dates'] = df['release_dates'].apply(
            lambda x: [i['date'] for i in x] if isinstance(x, list) and all('date' in item for item in x) else [])
        df['release_dates'] = df['release_dates'].apply(lambda x: x[0] if len(x) > 0 else '')
        df['websites'] = df['websites'].apply(lambda x: [(i['url'], i['category_name']) for i in x] if isinstance(x, list) else [])
        df['unclean_summary'] = df['summary']

        # Cleaning game's name
        cleaned_name = df['name']
        cleaned_name = cleaned_name.str.lower()
        cleaned_name = cleaned_name.str.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
        df['name'] = cleaned_name

        # Cleaning summary
        cleaned_summary = df['summary']
        cleaned_summary = cleaned_summary.str.lower().fillna('')
        cleaned_summary = cleaned_summary.str.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
        df['summary'] = cleaned_summary

        # Cleaning storyline
        cleaned_storyline = df['storyline']
        cleaned_storyline = cleaned_storyline.str.lower().fillna('')
        cleaned_storyline = cleaned_storyline.str.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
        df['storyline'] = cleaned_storyline

        # Calculate popularity score
        df['popularity'] = df.apply(lambda row: self.calculate_popularity(row), axis=1)

        # Save cleaned data to pickle file
        # with open('../assets/parsed_data.pkl', 'wb') as file:
        #     pickle.dump(df, file)

        csv_filename = '../assets/parsed_data.csv'
        df.to_csv(csv_filename, index=False)

        return df

    def calculate_popularity(self, row):
        rating = row['rating'] if 'rating' in row else 0
        rating_count = row['rating_count'] if 'rating_count' in row else 0
        aggregated_rating = row['aggregated_rating'] if 'aggregated_rating' in row else 0
        aggregated_rating_count = row['aggregated_rating_count'] if 'aggregated_rating_count' in row else 0

        popularity = (rating * rating_count + aggregated_rating * aggregated_rating_count) / (rating_count + aggregated_rating_count) if (rating_count + aggregated_rating_count) > 0 else 0
        return popularity


cleaner = CleanData()  # Create an instance of the CleanData class
df = cleaner.get_data("../assets/games.json")  # Call the get_data method on the instance

import pandas as pd
import string
import pickle


class CleanData:
    # cleaned_data
    def get_data(self, path):
        df = pd.read_json(path, orient='records')
        df.drop(columns=['hypes', 'platforms'], inplace=True)
        df['cover'] = df['cover'].apply(
            lambda x: x['url'].replace('t_thumb', 't_cover_big') if isinstance(x, dict) else '')
        df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        # Clean release_dates field
        df['release_dates'] = df['release_dates'].apply(
            lambda x: [i['date'] for i in x] if isinstance(x, list) and all('date' in item for item in x) else [])
        df['release_dates'] = df['release_dates'].apply(lambda x: x[0] if len(x) > 0 else '')
        df['websites'] = df['websites'].apply(
            lambda x: [(i['url'], i['category_name']) for i in x] if isinstance(x, list) else [])
        df['unclean_name'] = df['name']
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
        df['popularity'].fillna(0.0, inplace=True)

        df['rating'].fillna(0.0, inplace=True)
        df['rating_count'].fillna(0.0, inplace=True)
        df['aggregated_rating'].fillna(0.0, inplace=True)
        df['aggregated_rating_count'].fillna(0.0, inplace=True)


        # Save cleaned data to pickle file
        with open('../assets/parsed_data.pkl', 'wb') as file:
            pickle.dump(df, file)

        csv_filename = 'parsed_data.csv'
        df.to_csv(csv_filename, index=False)

        return df

    def calculate_popularity(self, row):
        rating = row['rating'] if 'rating' in row else 0
        aggregated_rating = row['aggregated_rating'] if 'aggregated_rating' in row else 0

        release_date = row['release_dates']
        release_date_score = self.calculate_release_date_score(release_date)

        weight_rating = 0.3
        weight_aggregated_rating = 0.3
        weight_release_date = 0.4

        # Calculate the popularity score as a weighted sum
        popularity = rating/100 * weight_rating + release_date_score * weight_release_date + aggregated_rating/100 * weight_aggregated_rating
        return popularity

    def calculate_release_date_score(self, release_date):
        if release_date:
            # Convert release date to a datetime object
            release_date = pd.to_datetime(release_date, errors='coerce')
            if not pd.isna(release_date):
                # Calculate a score based on the difference between the release date and today
                today = pd.Timestamp.today()
                days_since_release = (today - release_date).days

                # Define the number of years for full score (e.g., 5 years)
                years_for_full_score = 5

                if days_since_release <= (365 * years_for_full_score):
                    # Give a full score of 1 to games released in the last 5 years
                    release_date_score = 1.0
                else:
                    years_since_release = days_since_release / 365
                    release_date_score = max(0.1, 1 - (years_since_release - years_for_full_score) / (
                                years_for_full_score * 2))

                    # Ensure the score is between 0 and 1
                    release_date_score = min(1, release_date_score)

                return release_date_score
        return 0

    def clean_data_gameplay(self):
        # Load the cleaned data from parsed_data.pkl
        with open('../assets/parsed_data.pkl', 'rb') as file:
            df = pickle.load(file)

        # Remove games where main_story, main_extra, and completionist are 0
        df = df[(df['main_story'] > 0) | (df['main_extra'] > 0) | (df['completionist'] > 0)]

        # Save the cleaned gameplay data to pickle file
        with open('../assets/clean_gameplay.pkl', 'wb') as file:
            pickle.dump(df, file)

        # Save the cleaned gameplay data to a JSON file
        with open('../assets/clean_gameplay.json', 'w') as file:
            df.to_json(file, orient='records')

        return df

    def select_top_games(self):
        # Load the cleaned data from parsed_data.pkl
        with open('../assets/parsed_data.pkl', 'rb') as file:
            df = pickle.load(file)

        # Sort by popularity score and rating score in descending order
        sorted_games = df.sort_values(by=['popularity'], ascending=[False])

        # Select the top 5000 games
        top_games = sorted_games.head(5000)

        # Save the top games to a new pickle file
        with open('../assets/limit_games.pkl', 'wb') as file:
            pickle.dump(top_games, file)

        return top_games

    def get_upcoming_games(self):
        # Load the cleaned data from parsed_data.pkl
        with open('../assets/parsed_data.pkl', 'rb') as file:
            df = pickle.load(file)

        # Get today's date
        today = pd.Timestamp.today()

        # Filter games with valid release dates and release dates in the future (upcoming games)
        upcoming_games = df[
            df['release_dates'].apply(lambda x: isinstance(x, str) and pd.to_datetime(x, errors='coerce') > today)]

        # Save the upcoming games to a new pickle file
        # with open('../assets/upcoming_games.pkl', 'wb') as file:
        #     pickle.dump(upcoming_games, file)

        # Save the cleaned gameplay data to a JSON file
        with open('../assets/upcoming_games.json', 'w') as file:
            df.to_json(file, orient='records')

        return upcoming_games


cleaner = CleanData()  # Create an instance of the CleanData class
# df = cleaner.get_data("../assets/games.json")
# cleaned_df = cleaner.clean_data_gameplay()
# top_games_df = cleaner.select_top_games()
upcoming_games_df = cleaner.get_upcoming_games()

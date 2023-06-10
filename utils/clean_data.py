import pandas as pd
from nltk import word_tokenize, PorterStemmer
import string
import pickle


class Clean_data:
    def get_data(self, path):
        df = pd.read_json(path, orient='records')
        df.drop(columns=['hypes', 'platforms', 'rating_count', 'aggregated_rating_count'], inplace=True)
        df['cover'] = df['cover'].apply(lambda x: x['url'] if isinstance(x, dict) else '')
        df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        df['release_dates'] = df['release_dates'].apply(lambda x: [i['date'] for i in x] if isinstance(x, list) and all('date' in item for item in x) else [])
        df['websites'] = df['websites'].apply(lambda x: [(i['url'], i['category_name']) for i in x] if isinstance(x, list) else [])

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

        # Save cleaned data to pickle file
        with open('../assets/parsed_data.pkl', 'wb') as file:
            pickle.dump(df, file)

        return df

    # def pre_process(s):
    #     ps = PorterStemmer()
    #     s = word_tokenize(s)
    #     s = [ps.stem(w) for w in s]
    #     s = ' '.join(s)
    #     s = s.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
    #     return s


cleaner = Clean_data()  # Create an instance of the CleanData class
df = cleaner.get_data("../assets/games.json")  # Call the get_data method on the instance

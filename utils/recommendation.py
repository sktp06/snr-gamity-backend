import json
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
from nltk.stem import PorterStemmer

# Load your data
df = pd.read_csv('assets/parsed_data.csv')
df['summary'] = df['summary'].fillna('')
df = df.drop_duplicates(subset='id')
df = df.loc[df['summary'].apply(lambda s: len(np.unique(s.split()))) >= 15].reset_index(drop=True)
# input_df = df['summary']
ps = PorterStemmer()
# input_df = input_df.apply(lambda x: ' '.join([ps.stem(w) for w in x.split()]))
df['summary'] = df['summary'].apply(lambda x: ' '.join([ps.stem(w) for w in x.split()]))

# Create a TfidfVectorizer and fit_transform your data
tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
tfidf_matrix = tfidf.fit_transform(df['summary'])

# Batch size for processing
batch_size = 1000

# Compute cosine similarity in batches
num_docs = tfidf_matrix.shape[0]
cosine_sim = np.zeros((num_docs, num_docs), dtype='uint8')

for i in range(0, num_docs, batch_size):
    start = i
    end = min(i + batch_size, num_docs)
    batch_cosine_sim = linear_kernel(tfidf_matrix[start:end, :], tfidf_matrix)
    batch_cosine_sim_uint8 = (batch_cosine_sim * 255).astype('uint8')
    cosine_sim[start:end, :] = batch_cosine_sim_uint8

print("Cosine similarity matrix computed successfully.")

# Create a Series with game indices
# indices = pd.Series(df.index, index=df['id']).drop_duplicates()


# with open('assets/cosine_sim.pkl', 'wb') as file:
#     pickle.dump(cosine_sim, file)

# Create a Series with game indices
indices = pd.Series(df.index, index=df['id']).drop_duplicates()

# Store a mapping between original IDs and indices
id_to_idx_mapping = {game_id: idx for game_id, idx in zip(df['id'], df.index)}


def calculate_release_date_score(release_date):
    current_year = datetime.now().year
    release_year = int(release_date.split('-')[0])
    max_score = 1.0  # Maximum score for games released in the current year
    min_score = 0.1  # Minimum score for games released in years before 2005

    if release_year == current_year:
        return round(max_score, 2)  # Round to two decimal places
    elif release_year >= 2015:
        years_since_release = current_year - release_year
        score = max_score - (years_since_release * 0.1)
        return max(round(min_score, 2), round(score, 2))  # Round to two decimal places
    else:
        return round(min_score, 2)  # Round to two decimal places
    # example current-year release2016 = 7*0.1 = 0.7 1-0.7 =0.3


def get_recommendations(id, cosine_sim=cosine_sim, num_recommend=11):
    try:
        original_id = id
        idx = indices[id]

        # Get the pairwise similarity scores of all games with that game
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the games based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        for idx, score in sim_scores[:num_recommend]:
            normalized_score = score / sim_scores[0][1]  # Normalize by dividing by the max similarity score
            # print(normalized_score)

            # Skip recommendations with a score of 1.0000
            if normalized_score == 1.0:
                continue

            recommended_id = int(df['id'].iloc[idx])
            recommended_name = df['name'].iloc[idx]
            popularity_score = df['popularity'].iloc[idx]
            release_date_str = df['release_dates'].iloc[idx]

            # Skip recommendations with invalid release date strings
            if not isinstance(release_date_str, str):
                continue

            release_date_score = calculate_release_date_score(release_date_str)
            normalized_popularity_score = popularity_score / 100

            score_weight = 0.0
            popularity_weight = 0.5
            release_date_weight = 0.5  # Weight for release date

            # Convert all float32 values to Python's float for JSON serialization
            composite_score = float(
                release_date_score * release_date_weight + normalized_popularity_score * popularity_weight + normalized_score * score_weight)

            recommendation = {
                "composite_score": composite_score,
                "score": float(normalized_score),  # Convert to float
                "popularity_score": float(normalized_popularity_score),  # Convert to float
                "release_date_score": float(release_date_score),  # Convert to float
                "id": recommended_id,
                "name": recommended_name,
                "released_date": release_date_str
            }
            recommendations.append(recommendation)

        # Sort recommendations based on the composite_score in descending order
        recommendations = sorted(recommendations, key=lambda x: x["composite_score"], reverse=True)

        # Organize recommendations by game ID
        output = {
            str(original_id): recommendations
        }

        # Write recommendations to a JSON file
        with open("recommendations.json", "w") as json_file:
            json.dump(output, json_file, indent=4)

    except Exception as e:
        return f"An exception occurred: {str(e)}"


# Example usage
get_recommendations(159449, num_recommend=101)


def get_all_recommendations(cosine_sim=cosine_sim, num_recommend=11):
    all_recommendations = {}  # Dictionary to store recommendations for all games

    total_games = len(df['id'])
    for idx, loop_game_id in enumerate(df['id']):  # Use a different variable name
        try:
            print(f"Generating recommendations for game {loop_game_id} ({idx + 1}/{total_games})")
            game_idx = id_to_idx_mapping[loop_game_id]  # Get the corresponding index from the mapping
            sim_scores = list(enumerate(cosine_sim[game_idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            max_score = sim_scores[0][1]

            recommendations = []
            for inner_idx, score in sim_scores[:num_recommend]:
                normalized_score = score / max_score

                # Skip recommendations with a score of 1.0000
                if normalized_score == 1.0:
                    continue

                recommended_id = int(df['id'].iloc[inner_idx])  # Use inner_idx to get the correct ID
                popularity_score = df['popularity'].iloc[inner_idx]  # Use inner_idx to get the correct popularity
                release_date_str = df['release_dates'].iloc[inner_idx]  # Use inner_idx to get the correct release date

                # Skip recommendations with invalid release date strings
                if not isinstance(release_date_str, str):
                    continue

                release_date_score = calculate_release_date_score(release_date_str)
                normalized_popularity_score = popularity_score / 100

                score_weight = 0.0
                popularity_weight = 0.5
                release_date_weight = 0.5  # Weight for release date

                # Convert all float32 values to Python's float for JSON serialization
                composite_score = float(
                    release_date_score * release_date_weight + normalized_popularity_score * popularity_weight + normalized_score * score_weight)

                recommendation = {
                    "composite_score": composite_score,
                    "id": recommended_id,  # Convert to int
                }
                recommendations.append(recommendation)

            # Sort recommendations based on the release_date_score in descending order
            recommendations = sorted(recommendations, key=lambda x: x["composite_score"], reverse=True)

            all_recommendations[str(loop_game_id)] = recommendations

        except Exception as e:
            print(f"An exception occurred for game {loop_game_id}: {str(e)}")

    # Write all recommendations to a JSON file
    with open("all_recommendations055.json", "w") as json_file:
        json.dump(all_recommendations, json_file, indent=4)

    # # Write all recommendations to a pickle file
    # with open("all_recommendations055.pkl", "wb") as pickle_file:
    #     pickle.dump(all_recommendations, pickle_file)


# Call the function to generate recommendations for all games
get_all_recommendations(num_recommend=11)

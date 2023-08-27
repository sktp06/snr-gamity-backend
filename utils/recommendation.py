import json

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
tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 1))
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
indices = pd.Series(df.index, index=df['id']).drop_duplicates()


# with open('assets/cosine_sim.pkl', 'wb') as file:
#     pickle.dump(cosine_sim, file)


def get_recommendations(id, cosine_sim=cosine_sim, num_recommend=11):
    try:
        idx = indices[id]
        # Get the pairwsie similarity scores of all games with that game
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the games based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the maximum similarity score
        max_score = sim_scores[0][1]

        recommendations = []
        for idx, score in sim_scores[:num_recommend]:
            normalized_score = score / max_score
            formatted_score = format(normalized_score, '.4f')  # Format the score to 4 decimal places

            # Skip recommendations with a score of 1.0000
            if formatted_score == "1.0000":
                continue

            recommendation = {
                "score": formatted_score,
                "id": idx  # Store the game ID instead of name
            }
            recommendations.append(recommendation)

        # Organize recommendations by game ID
        output = {
            str(id): recommendations
        }

        # Write recommendations to a JSON file
        with open("recommendations.json", "w") as json_file:
            json.dump(output, json_file, indent=4)

    except Exception as e:
        return f"An exception occurred: {str(e)}"

# Example usage
get_recommendations(8533, num_recommend=11)


def get_all_recommendations(cosine_sim=cosine_sim, num_recommend=11):
    all_recommendations = {}  # Dictionary to store recommendations for all games

    total_games = len(df['id'])
    for idx, game_id in enumerate(df['id']):
        try:
            print(f"Generating recommendations for game {game_id} ({idx+1}/{total_games})")
            idx = indices[game_id]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            max_score = sim_scores[0][1]

            recommendations = []
            for idx, score in sim_scores[:num_recommend]:
                normalized_score = score / max_score
                formatted_score = format(normalized_score, '.4f')

                # Skip recommendations with a score of 1.0000
                if formatted_score == "1.0000":
                    continue

                recommendation = {
                    "score": formatted_score,
                    "id": idx
                }
                recommendations.append(recommendation)

            all_recommendations[str(game_id)] = recommendations

        except Exception as e:
            print(f"An exception occurred for game {game_id}: {str(e)}")

    # Write all recommendations to a JSON file
    # with open("all_recommendations.json", "w") as json_file:
    #     json.dump(all_recommendations, json_file, indent=4)

    with open("all_recommendations.pkl", "wb") as pickle_file:
        pickle.dump(all_recommendations, pickle_file)

# Call the function to generate recommendations for all games
get_all_recommendations(num_recommend=11)


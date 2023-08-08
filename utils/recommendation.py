import json
import pickle
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

# Load parsed data from JSON file
with open('../assets/parsed_data.json', 'r') as f:
    games_data = json.load(f)

# Extract relevant features
game_names = [game['name'] for game in games_data]
summaries = [game['summary'] for game in games_data]

# Create a dictionary to map game titles to their indices
title_to_index = {game['name']: index for index, game in enumerate(games_data)}

# Train Word2Vec model
word2vec_model = Word2Vec(sentences=[(name + ' ' + summary).split() for name, summary in zip(game_names, summaries)],
                          vector_size=300, window=5, min_count=2, workers=-1)


# Function to get game vector using Word2Vec
def get_game_vector(title):
    words = (title + ' ' + summaries[title_to_index[title]]).split()
    vector_sum = np.zeros(word2vec_model.vector_size)
    count = 0
    for word in words:
        if word in word2vec_model.wv:
            vector_sum += word2vec_model.wv[word]
            count += 1
    if count > 0:
        return vector_sum / count
    return vector_sum


# Input the target game index
target_game_index = 72  # Replace with your desired target game index
target_game_title = game_names[target_game_index]

# Get Word2Vec vector for the target game
target_word2vec_vector = get_game_vector(target_game_title)

# Calculate similarity scores using Word2Vec vectors
word2vec_similarity_scores = cosine_similarity([target_word2vec_vector],
                                               [get_game_vector(title) for title in game_names]).flatten()

# Get recommended games
num_recommendations = 5
sorted_indices = np.argsort(word2vec_similarity_scores)[::-1]
recommended_indices = sorted_indices[1:num_recommendations + 1]
recommended_games = [game_names[idx] for idx in recommended_indices]

# Display recommended games
print(f"Recommended games for {target_game_index} {target_game_title} using Word Embeddings:")
for i, game_index in enumerate(recommended_indices):
    game = games_data[game_index]
    print(f"Game {i + 1}: id={game['id']}, title='{game['name']}'")

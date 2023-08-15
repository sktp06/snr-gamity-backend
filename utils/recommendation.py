import json
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

# Load parsed data from JSON file
with open('../assets/parsed_data.json', 'r') as f:
    games_data = json.load(f)

# Extract unclean summaries
unclean_summaries = [game['unclean_summary'] for game in games_data]

# Filter out None values
unclean_summaries = [summary for summary in unclean_summaries if summary is not None]

# Train Word2Vec model
word2vec_model = Word2Vec(sentences=[summary.split() for summary in unclean_summaries],
                          vector_size=300, window=5, min_count=2, workers=-1)

# Function to get game vector using Word2Vec
def get_game_vector(unclean_summary):
    words = unclean_summary.split()
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
target_game_unclean_summary = unclean_summaries[target_game_index]

# Calculate similarity scores using Word2Vec vectors and aggregated_rating
target_word2vec_vector = get_game_vector(target_game_unclean_summary)
target_aggregated_rating = games_data[target_game_index]['aggregated_rating']

similarity_scores = []
for unclean_summary in unclean_summaries:
    similarity_score = cosine_similarity([target_word2vec_vector], [get_game_vector(unclean_summary)])[0][0]
    similarity_scores.append(similarity_score)

# Get recommended games
num_recommendations = 10
sorted_indices = np.argsort(similarity_scores)[::-1]
recommended_indices = sorted_indices[1:num_recommendations + 1]

# Combine similarity scores and aggregated ratings for ranking
combined_scores = [(similarity_scores[i], games_data[recommended_indices[i]]['aggregated_rating']) for i in range(num_recommendations)]

# Sort recommended games by combined score (similarity + aggregated_rating)
combined_scores.sort(key=lambda x: (x[0], x[1]), reverse=True)
sorted_indices = [recommended_indices[i] for i, _ in combined_scores]

# Display recommended games and their combined scores
print(f"Recommended games for {target_game_index} {games_data[target_game_index]['name']} using Word Embeddings and Aggregated Rating:")

for i, game_index in enumerate(sorted_indices):
    game = games_data[game_index]
    similarity_score, aggregated_rating = combined_scores[i]
    print(f"Game {i + 1}: id={game['id']}, title='{game['name']}', Similarity Score={similarity_score:.4f}, Aggregated Rating={aggregated_rating:.4f}")

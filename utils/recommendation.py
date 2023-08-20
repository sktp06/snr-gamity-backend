import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle

# Load your data
df = pd.read_csv('assets/parsed_data.csv')
df['summary'] = df['summary'].fillna('')
df['name'] = df['name'].drop_duplicates()

# Create a TfidfVectorizer and fit_transform your data
tfidf = TfidfVectorizer(stop_words='english')
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

# Create a Series with movie indices
indices = pd.Series(df.index, index=df['id']).drop_duplicates()

with open('assets/cosine_sim.pkl', 'wb') as file:
    pickle.dump(cosine_sim, file)
def get_recommendations(id, cosine_sim=cosine_sim, num_recommend=10):
    try:
        idx = indices[id]
        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get the scores of the 10 most similar movies
        top_similar = sim_scores[1:num_recommend + 1]
        # Get the movie indices
        movie_indices = [i[0] for i in top_similar]
        # Return the top 10 most similar movies
        return df['name'].iloc[movie_indices]
    except Exception as e:
        return (f"An exception occurred: {str(e)}")


# print(get_recommendations(37258, num_recommend=10))

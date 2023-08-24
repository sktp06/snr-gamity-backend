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
input_df = df['summary']
ps = PorterStemmer()
input_df = input_df.apply(lambda x: ' '.join([ps.stem(w) for w in x.split()]))

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

with open('../assets/cosine_sim.pkl', 'wb') as file:
    pickle.dump(cosine_sim, file)


def get_recommendations(id, cosine_sim=cosine_sim, num_recommend=10, max_overlap_threshold=0.5):
    try:
        idx = indices[id]
        # Get the pairwsie similarity scores of all games with that game
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the games based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the most similar games
        top_similar = [x for x in sim_scores if x[1] > max_overlap_threshold ]

        # Get the maximum similarity score
        max_score = max(top_similar, key=lambda x: x[1])[1]

        # Print the most similar game names with similarity scores
        # for idx, score in top_similar:
        #     normalized_score = score / max_score
        #     print(f"Similarity Score: {normalized_score:.4f} - {df['name'].iloc[idx]}")
        for idx, score in top_similar[:num_recommend]:
            normalized_score = score / max_score
            print(f"Similarity Score: {normalized_score:.4f} - {df['name'].iloc[idx]}")

        game_indices = [i[0] for i in top_similar]

        # Return the most similar game names up to num_recommend
        return df['name'].iloc[game_indices]
    except Exception as e:
        return f"An exception occurred: {str(e)}"


# Example usage
print(get_recommendations(8533, num_recommend=10))

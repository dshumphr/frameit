import os
import pickle
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import random
import numpy as np

# Load the spaCy model
nlp = spacy.load("en_core_web_md")

# Define function to load tag vectors
def load_tag_vectors():
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    tag_vectors_file_path = os.path.join(data_dir, 'tag_vectors.pkl')
    
    with open(tag_vectors_file_path, 'rb') as file:
        tag_vectors = pickle.load(file)
    
    return tag_vectors

# Define function to process tags
def process_tags(user_prompt):
    tag_vectors = load_tag_vectors()
    # Assume tag_vectors is a dict with keys 'artists', 'styles', 'mediums', 'movements', and their respective vectors
    
    original_tags = [tag.strip() for tag in user_prompt.split(",")]
    if len(original_tags) < 1:
        return "Prompt too short, please consider adding more details."
    
    def find_similar_tags(tag_category, input_vector, top_n=2, score_threshold=0.7):
        # Extracting tags and their vectors for the specified category
        category_tags = list(tag_vectors[tag_category].keys())
        category_vectors = [tag_vectors[tag_category][tag] for tag in category_tags]

        # Calculate similarity scores between the input vector and all vectors in the category
        similarity_scores = cosine_similarity([input_vector], category_vectors)[0]

        # Filter scores and tags based on the threshold
        filtered_scores_indices = [i for i, score in enumerate(similarity_scores) if score > score_threshold]
        filtered_scores = [similarity_scores[i] for i in filtered_scores_indices]
        filtered_tags = [category_tags[i] for i in filtered_scores_indices]

        # Ensure there are enough scores above the threshold
        if len(filtered_scores) < 2*top_n:
            print(f"Not enough tags with similarity > {score_threshold} in category '{tag_category}'.")
            # Fallback or handle this case as needed
            # For demonstration, proceeding with available filtered scores
            top_indices = np.array(filtered_scores).argsort()[-len(filtered_scores):][::-1]
        else:
            # Determine the top 2*n indices from the filtered list, based on similarity scores
            top_indices = np.array(filtered_scores).argsort()[-2*top_n:][::-1]

        # Debug: Print the top 2*n (or available) filtered tags with their similarity scores
        print(f"Top {2*top_n} (or available) filtered similarity scores for category '{tag_category}':")
        for index in top_indices:
            print(f"{filtered_tags[index]}: {filtered_scores[index]}")

        # Return the top N similar tags based on the filtered list
        # Adjusting for cases where filtered tags are less than requested
        return_tags_count = min(top_n, len(filtered_tags))
        return [filtered_tags[i] for i in top_indices[:return_tags_count]]

    # Example optimization logic
    avg_vector = nlp(user_prompt).vector
    similar_artists = find_similar_tags('artists', avg_vector, top_n=2)
    similar_styles = find_similar_tags('styles', avg_vector, top_n=2)
    similar_mediums = find_similar_tags('mediums', avg_vector, top_n=2)
    similar_movements = find_similar_tags('movements', avg_vector, top_n=2)
    
    optimized_tags = set(original_tags + similar_artists + similar_styles + similar_mediums + similar_movements)
    optimized_prompt = ', '.join(list(optimized_tags))
    
    return optimized_prompt

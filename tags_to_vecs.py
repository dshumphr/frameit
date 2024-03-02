import spacy
import pickle

# Load spaCy model
nlp = spacy.load("en_core_web_md")

def read_tags_from_file(file_path):
    """Reads lines from a given file and returns them as a list of tags."""
    with open(file_path, 'r', encoding='utf-8') as file:
        tags = [line.strip() for line in file if line.strip()]
    return tags

# Paths to your tag files
artists_file_path = "data/artists.txt"
mediums_file_path = "data/mediums.txt"
styles_file_path = "data/styles.txt"
movements_file_path = "data/movements.txt"

# Read tags from each file
artists_tags = read_tags_from_file(artists_file_path)
mediums_tags = read_tags_from_file(mediums_file_path)
styles_tags = read_tags_from_file(styles_file_path)
movements_tags = read_tags_from_file(movements_file_path)

# Function to convert tags into vectors
def tags_to_vectors(tags):
    return {tag: nlp(tag).vector for tag in tags}

# Convert each category of tags into vectors
tag_vectors = {
    "artists": tags_to_vectors(artists_tags),
    "mediums": tags_to_vectors(mediums_tags),
    "styles": tags_to_vectors(styles_tags),
    "movements": tags_to_vectors(movements_tags),
}

# Pickle the tag vectors for later use
pickle_file_path = "data/tag_vectors.pkl"
with open(pickle_file_path, "wb") as file:
    pickle.dump(tag_vectors, file)

print(f"Tag vectors pickled to {pickle_file_path}")

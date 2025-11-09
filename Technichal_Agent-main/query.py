# query_embeddings.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_embeddings():
    with open("havells_parsed/havells_catalogue_with_embeddings.json", "r") as f:
        return json.load(f)

def search_cables(query, top_k=5):
    data = load_embeddings()
    query_embedding = model.encode(query)
    
    similarities = []
    for record in data["records"]:
        record_embedding = np.array(record["embedding"])
        similarity = cosine_similarity([query_embedding], [record_embedding])[0][0]
        similarities.append((similarity, record))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    return similarities[:top_k]

# Example queries
queries = [
    "1.5 sq mm cable with high current rating",
    "heavy duty cables for industrial use", 
    "10 sq mm cable with thick insulation",
    "lightweight cables under 100 kg per km"
]

for query in queries:
    print(f"\nQuery: '{query}'")
    results = search_cables(query)
    for score, record in results:
        area = record.get('conductor_nominal_area_mm2', 'N/A')
        current = record.get('current_rating_amps', 'N/A')
        print(f"  {area} sq mm, {current} amps (score: {score:.3f})")
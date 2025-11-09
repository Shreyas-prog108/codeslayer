# query_embeddings.py
import json
import numpy as np
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
    model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    model = None

def load_embeddings():
    """Load embeddings from file with error handling"""
    embeddings_path = Path(__file__).parent / "havells_parsed" / "havells_catalogue_with_embeddings.json"
    
    if not embeddings_path.exists():
        print(f"⚠️ Warning: Embeddings file not found at {embeddings_path}")
        return {"records": [], "total_records": 0}
    
    try:
        with open(embeddings_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading embeddings: {e}")
        return {"records": [], "total_records": 0}

def search_cables(query, top_k=5):
    """Search for cables using semantic similarity"""
    if not EMBEDDINGS_AVAILABLE or model is None:
        print("⚠️ sentence-transformers not available, returning empty results")
        return []
    
    data = load_embeddings()
    
    if not data.get("records"):
        print("⚠️ No embeddings data available")
        return []
    
    query_embedding = model.encode(query)
    
    similarities = []
    for record in data["records"]:
        if "embedding" not in record:
            continue
        record_embedding = np.array(record["embedding"])
        similarity = cosine_similarity([query_embedding], [record_embedding])[0][0]
        similarities.append((similarity, record))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    return similarities[:top_k]

# Only run examples if this file is executed directly
if __name__ == "__main__":
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
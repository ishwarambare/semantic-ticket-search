from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once when module is imported
# Downloads ~80MB on first run, cached locally after
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded ✓")

def generate_embedding(text: str) -> list[float]:
    """
    Convert text to 384-dimensional vector.
    
    Why we combine title + description:
    - Title alone misses context
    - Description alone might miss the key topic
    - Combined gives best semantic representation
    """
    # Normalize whitespace
    text = " ".join(text.split())
    
    embedding = model.encode(
        text,
        normalize_embeddings=True  # Unit length for cosine similarity
    )
    
    return embedding.tolist()

def generate_ticket_embedding(
    title: str, 
    description: str
) -> list[float]:
    """
    Generate embedding for a ticket.
    Combines title (weighted more) + description.
    """
    # Give title more weight by repeating it
    # Interview insight: "I weighted the title more 
    # because it's the most concise expression of 
    # the problem"
    combined_text = f"{title}. {title}. {description}"
    return generate_embedding(combined_text)

def compute_similarity(
    vec1: list[float], 
    vec2: list[float]
) -> float:
    """
    Compute cosine similarity between two vectors.
    Returns value between 0.0 and 1.0.
    We rarely call this directly — Pinecone does it 
    at scale. Useful for unit tests.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    # Cosine similarity = dot product of unit vectors
    # Since we normalize embeddings above, this 
    # simplifies to just dot product
    return float(np.dot(v1, v2))
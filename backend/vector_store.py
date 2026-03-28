from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone client (does NOT connect to index yet)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Lazy index connection — resolved on first use
_index = None

def _get_index():
    """
    Lazily connect to the Pinecone index.
    This avoids crashing at startup if the index
    hasn't been created yet.
    """
    global _index
    if _index is None:
        _index = pc.Index(PINECONE_INDEX_NAME)
    return _index

def ensure_index_exists():
    """
    Create the Pinecone index if it doesn't exist.
    Call this once during app startup or setup.
    Dimension=384 matches all-MiniLM-L6-v2 model.
    """
    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"Index '{PINECONE_INDEX_NAME}' created ✓")
    else:
        print(f"Pinecone index '{PINECONE_INDEX_NAME}' already exists ✓")

def upsert_ticket_vector(
    ticket_id: int,
    embedding: list[float],
    metadata: dict
) -> bool:
    """
    Store or update a ticket's vector in Pinecone.
    
    metadata is stored alongside the vector and 
    returned in search results — useful for basic 
    filtering without hitting PostgreSQL.
    
    Why 'upsert' not 'insert':
    If ticket is updated, we need to replace the old 
    vector. Upsert handles both insert and update.
    """
    try:
        _get_index().upsert(
            vectors=[{
                "id": str(ticket_id),  # Pinecone IDs must be strings
                "values": embedding,
                "metadata": {
                    "ticket_id": ticket_id,
                    "status": metadata.get("status", "open"),
                    "category": metadata.get("category", ""),
                    "has_solution": metadata.get(
                        "has_solution", False
                    ),
                }
            }]
        )
        return True
    except Exception as e:
        print(f"Pinecone upsert error: {e}")
        return False

def search_similar_tickets(
    query_embedding: list[float],
    top_k: int = 5,
    exclude_ticket_id: int = None,
    filter_status: str = None
) -> list[dict]:
    """
    Find similar tickets using vector similarity.
    
    Why top_k=5:
    - Too few: might miss a relevant resolved ticket
    - Too many: floods user with irrelevant results
    - 5 is the sweet spot for this use case
    
    exclude_ticket_id:
    When checking if a new ticket is duplicate, we 
    don't want it to match itself.
    
    filter_status:
    Can filter to only return 'resolved' tickets 
    when looking for solutions.
    """
    
    # Build metadata filter
    filter_dict = {}
    if filter_status:
        filter_dict["status"] = {"$eq": filter_status}
    
    query_params = {
        "vector": query_embedding,
        "top_k": top_k + 1,  # +1 in case we exclude one
        "include_metadata": True,
    }
    
    if filter_dict:
        query_params["filter"] = filter_dict
    
    results = _get_index().query(**query_params)
    
    similar = []
    for match in results["matches"]:
        ticket_id = int(match["id"])
        
        # Skip the ticket itself if searching for 
        # duplicates of an existing ticket
        if exclude_ticket_id and ticket_id == exclude_ticket_id:
            continue
            
        # Only include if similarity is meaningful
        # Below 0.65 = not similar enough to surface
        if match["score"] >= 0.65:
            similar.append({
                "ticket_id": ticket_id,
                "similarity_score": round(match["score"], 3),
                "metadata": match["metadata"]
            })
    
    return similar[:top_k]  # Return only top_k results

def delete_ticket_vector(ticket_id: int) -> bool:
    """Remove ticket vector when ticket is deleted."""
    try:
        _get_index().delete(ids=[str(ticket_id)])
        return True
    except Exception as e:
        print(f"Pinecone delete error: {e}")
        return False

def get_index_stats() -> dict:
    """
    Useful for debugging — see how many vectors 
    are stored and index health.
    """
    return _get_index().describe_index_stats()
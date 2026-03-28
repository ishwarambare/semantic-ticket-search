from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Ticket
from schemas import SearchResponse, SimilarTicket, TicketResponse
from embeddings import generate_embedding
from vector_store import search_similar_tickets

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/similar", response_model=SearchResponse)
async def find_similar_tickets(
    query: str = Query(..., min_length=5, 
                       description="Ticket description to search"),
    top_k: int = Query(5, ge=1, le=10),
    only_resolved: bool = Query(
        False, 
        description="Return only resolved tickets with solutions"
    ),
    db: Session = Depends(get_db)
):
    """
    Core endpoint — find similar tickets.
    
    Use cases:
    1. Before creating a ticket: "is this already reported?"
    2. Finding solutions: "how was this type of issue resolved?"
    3. Duplicate detection in the system
    
    Interview talking point:
    "I separated the search endpoint from the ticket 
    CRUD endpoints because search has different 
    concerns — it touches both Pinecone and PostgreSQL,
    has different caching requirements, and might 
    eventually need different rate limiting."
    """
    
    # Step 1: Generate embedding for the search query
    query_embedding = generate_embedding(query)
    
    # Step 2: Search Pinecone for similar vectors
    filter_status = "resolved" if only_resolved else None
    
    pinecone_results = search_similar_tickets(
        query_embedding=query_embedding,
        top_k=top_k,
        filter_status=filter_status
    )
    
    if not pinecone_results:
        return SearchResponse(
            query=query,
            similar_tickets=[],
            total_found=0
        )
    
    # Step 3: Fetch full ticket details from PostgreSQL
    # using the IDs returned from Pinecone
    ticket_ids = [r["ticket_id"] for r in pinecone_results]
    
    tickets_db = db.query(Ticket).filter(
        Ticket.id.in_(ticket_ids)
    ).all()
    
    # Create a map for easy lookup
    tickets_map = {t.id: t for t in tickets_db}
    
    # Step 4: Combine Pinecone scores with PG data
    similar_tickets = []
    for result in pinecone_results:
        ticket = tickets_map.get(result["ticket_id"])
        if ticket:
            similar_tickets.append(
                SimilarTicket(
                    ticket=TicketResponse.model_validate(ticket),
                    similarity_score=result["similarity_score"],
                    has_solution=ticket.solution is not None
                )
            )
    
    # Sort by similarity score (highest first)
    similar_tickets.sort(
        key=lambda x: x.similarity_score, 
        reverse=True
    )
    
    return SearchResponse(
        query=query,
        similar_tickets=similar_tickets,
        total_found=len(similar_tickets)
    )

@router.get("/check-duplicate")
async def check_if_duplicate(
    title: str = Query(...),
    description: str = Query(...),
    threshold: float = Query(
        0.85,
        description="Similarity threshold to consider duplicate"
    ),
    db: Session = Depends(get_db)
):
    """
    Check if a ticket is likely a duplicate 
    before creating it.
    
    Returns warning if very similar ticket exists.
    Threshold 0.85 = 85% similar = likely duplicate.
    """
    from embeddings import generate_ticket_embedding
    
    embedding = generate_ticket_embedding(title, description)
    results = search_similar_tickets(
        query_embedding=embedding,
        top_k=3
    )
    
    # Check if any result exceeds duplicate threshold
    duplicates = [
        r for r in results 
        if r["similarity_score"] >= threshold
    ]
    
    if duplicates:
        ticket_ids = [d["ticket_id"] for d in duplicates]
        tickets = db.query(Ticket).filter(
            Ticket.id.in_(ticket_ids)
        ).all()
        tickets_map = {t.id: t for t in tickets}
        
        return {
            "is_likely_duplicate": True,
            "message": "Similar tickets already exist",
            "similar_tickets": [
                {
                    "id": d["ticket_id"],
                    "title": tickets_map[d["ticket_id"]].title,
                    "similarity_score": d["similarity_score"],
                    "status": tickets_map[d["ticket_id"]].status
                }
                for d in duplicates
                if d["ticket_id"] in tickets_map
            ]
        }
    
    return {
        "is_likely_duplicate": False,
        "message": "No duplicate found. Safe to create."
    }
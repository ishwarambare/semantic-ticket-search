from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Ticket
from schemas import TicketCreate, TicketUpdate, TicketResponse
from embeddings import generate_ticket_embedding
from vector_store import upsert_ticket_vector, delete_ticket_vector

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new ticket.
    
    Flow:
    1. Save ticket to PostgreSQL
    2. Generate embedding
    3. Store vector in Pinecone
    
    Why save to PostgreSQL first:
    We need the auto-generated ticket ID to use 
    as the vector ID in Pinecone. IDs must match.
    """
    # Step 1: Save to PostgreSQL
    ticket = Ticket(**ticket_data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Step 2: Generate embedding
    embedding = generate_ticket_embedding(
        ticket.title, 
        ticket.description
    )
    
    # Step 3: Store in Pinecone
    upsert_ticket_vector(
        ticket_id=ticket.id,
        embedding=embedding,
        metadata={
            "status": ticket.status.value,
            "category": ticket.category or "",
            "has_solution": False
        }
    )
    
    return ticket

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=404, 
            detail=f"Ticket {ticket_id} not found"
        )
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: Session = Depends(get_db)
):
    """
    Update ticket — also updates Pinecone metadata.
    
    Important: when a ticket is resolved with a 
    solution, we update Pinecone metadata so it 
    appears in solution searches.
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Update PostgreSQL
    update_dict = update_data.model_dump(exclude_none=True)
    for key, value in update_dict.items():
        setattr(ticket, key, value)
    
    db.commit()
    db.refresh(ticket)
    
    # Re-generate embedding if content changed
    # (status updates don't need new embedding)
    embedding = generate_ticket_embedding(
        ticket.title,
        ticket.description
    )
    
    # Update Pinecone metadata
    upsert_ticket_vector(
        ticket_id=ticket.id,
        embedding=embedding,
        metadata={
            "status": ticket.status.value,
            "category": ticket.category or "",
            "has_solution": ticket.solution is not None
        }
    )
    
    return ticket

@router.get("/", response_model=list[TicketResponse])
async def list_tickets(
    status: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    return query.order_by(
        Ticket.created_at.desc()
    ).limit(limit).all()
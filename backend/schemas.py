from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import TicketStatus, TicketPriority

# ── Request schemas (what client sends) ──────────────

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.medium
    category: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    solution: Optional[str] = None
    priority: Optional[TicketPriority] = None

# ── Response schemas (what server returns) ───────────

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    solution: Optional[str]
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2

class SimilarTicket(BaseModel):
    """Returned in similarity search results"""
    ticket: TicketResponse
    similarity_score: float  # 0.0 to 1.0
    has_solution: bool

class SearchResponse(BaseModel):
    query: str
    similar_tickets: list[SimilarTicket]
    total_found: int
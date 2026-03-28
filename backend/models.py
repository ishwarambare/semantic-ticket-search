from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        Enum(TicketStatus),
        default=TicketStatus.open,
        nullable=False
    )
    priority = Column(
        Enum(TicketPriority),
        default=TicketPriority.medium,
        nullable=False
    )
    # Solution added when ticket is resolved
    solution = Column(Text, nullable=True)

    # Category helps with filtering
    category = Column(String(100), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<Ticket {self.id}: {self.title}>"
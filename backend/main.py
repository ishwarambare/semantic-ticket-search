from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import tickets, search
from vector_store import get_index_stats, ensure_index_exists

# Create all PostgreSQL tables
Base.metadata.create_all(bind=engine)

# Create Pinecone index if it doesn't exist
ensure_index_exists()

app = FastAPI(
    title="Semantic Ticket Search",
    description="""
    AI-powered ticket search using vector embeddings.
    
    Features:
    - Create tickets (automatically embedded)
    - Find semantically similar tickets
    - Detect potential duplicates
    - Find solutions from resolved tickets
    """,
    version="1.0.0"
)

# CORS for ReactJS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(tickets.router)
app.include_router(search.router)

@app.get("/")
async def root():
    return {
        "message": "Semantic Ticket Search API",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Good practice for Docker/Kubernetes deployments.
    """
    stats = get_index_stats()
    return {
        "status": "healthy",
        "vector_count": stats.get(
            "total_vector_count", 0
        ),
        "database": "connected"
    }
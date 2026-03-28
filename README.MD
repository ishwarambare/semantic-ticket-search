# Semantic Ticket Search System

AI-powered support ticket search using vector 
embeddings and semantic similarity.

## Features
- Find similar tickets instantly using AI
- Detect potential duplicates before creation  
- Surface solutions from resolved tickets
- Real-time similarity scoring (0-100%)

## Architecture
New Ticket → HuggingFace Embeddings → Pinecone Search
→ PostgreSQL Fetch → Ranked Results

## Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy
- **AI:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB:** Pinecone (similarity search)
- **Database:** PostgreSQL (ticket storage)
- **Frontend:** ReactJS

## Quick Start
pip install -r requirements.txt
uvicorn main:app --reload
python seed_data.py

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /tickets/ | Create ticket |
| GET | /search/similar | Find similar tickets |
| GET | /search/check-duplicate | Duplicate detection |
| GET | /health | System health |
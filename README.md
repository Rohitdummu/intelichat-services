# IntelliChat

IntelliChat is an enterprise AI knowledge assistant that ingests PDF documents, stores their content and embeddings in PostgreSQL + pgvector, and answers questions using a retrieval-augmented generation (RAG) workflow.

## Features

- Secure user registration and authentication with JWT
- PDF upload and document metadata storage
- Text extraction and chunking for long documents
- pgvector-based similarity search for relevant document chunks
- RAG chat workflow with optional OpenAI integration
- Conversation history and ownership enforcement
- FastAPI OpenAPI docs with Swagger and ReDoc

## Architecture

```mermaid
flowchart LR
    A[React + TypeScript] --> B[FastAPI REST API]
    B --> C[(PostgreSQL + pgvector)]
    B --> D[OpenAI API]
    E[Uploaded PDF] --> F[Text Extraction]
    F --> G[Chunking]
    G --> H[Embedding Service]
    H --> C
    I[User Question] --> J[Question Embedding]
    J --> K[Similarity Search]
    K --> L[Relevant Chunks]
    L --> M[LLM Prompt]
    M --> D
    D --> N[Final Answer + Sources]
```

## Stack

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 17
- pgvector 0.8
- Pydantic + pydantic-settings
- JWT via PyJWT
- OpenAI Python SDK
- React + TypeScript frontend (prepared in frontend/)

## Project Structure

```text
backend/
  app/
    ai/
    api/
      routes/
    core/
    models/
    schemas/
    services/
    database.py
    main.py
  tests/
  .env
  .env.example
  main.py
  requirements.txt
frontend/
  src/
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure PostgreSQL and pgvector.
4. Create a .env file based on .env.example.

## PostgreSQL Setup

Create a database named intellichat and enable the pgvector extension if needed:

```sql
CREATE DATABASE intellichat;
\c intellichat
CREATE EXTENSION IF NOT EXISTS vector;
```

## pgvector Setup

The project stores embeddings in a VECTOR(1536) column. It is compatible with the existing database schema and the pgvector extension installed in PostgreSQL.

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/intellichat
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
OPENAI_API_KEY=
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=800
CHUNK_OVERLAP=120
TOP_K=5
MAX_UPLOAD_SIZE_MB=10
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The API docs are available at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Running the Frontend

The frontend foundation is prepped in the frontend/ folder.

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

FastAPI automatically exposes OpenAPI schema at:
- /docs
- /redoc

## RAG Workflow

```text
Document
  -> Text extraction
  -> Chunking
  -> Embedding
  -> pgvector
  -> Similarity search
  -> Context
  -> LLM
  -> Answer + Sources
```

## Authentication

The backend uses JWT bearer tokens. A user must register and log in before accessing protected routes. Passwords are hashed and tokens are validated server-side.

## Testing

```bash
cd backend
pytest
```

## Future Improvements

- Add Alembic migrations for schema evolution
- Add document indexing and OCR for more file types
- Add explicit rate limiting and audit logging
- Add background job processing for PDF uploads and embeddings

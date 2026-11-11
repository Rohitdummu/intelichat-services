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
- PostgreSQL 16 with pgvector
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
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_CHAT_DEPLOYMENT=your-chat-deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=800
CHUNK_OVERLAP=120
TOP_K=5
MAX_UPLOAD_SIZE_MB=10
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

For Azure embeddings, use the resource-level OpenAI endpoint (`https://<resource-name>.openai.azure.com/`), not a Foundry project endpoint ending in `/api/projects/<project-name>`. The embedding deployment must be a deployed embedding model, such as `text-embedding-3-small`.

## Docker Compose

Copy `.env.example` to `.env`, set a strong `SECRET_KEY`, and configure the required AI credentials if using a live model. Then build and start the API and PostgreSQL:

```bash
docker compose up --build
```

Compose uses the `pg_db` service name for the API's database connection, so the host machine's `localhost` database URL in `.env` is overridden inside the API container. The PostgreSQL password default is for local development only; set `POSTGRES_PASSWORD` in `.env` before using this setup beyond a local machine. If it contains URL-reserved characters, set `DATABASE_URL_PASSWORD` to its URL-encoded form as well. The API is available at `http://localhost:8000/docs`.

## Kubernetes

Build and publish the same Docker image, then configure the Deployment with container port `8000` and these probes:

- Startup/liveness: `GET /api/v1/health`
- Readiness: `GET /api/v1/health/database`

Provide `DATABASE_URL` using the cluster DNS name of your PostgreSQL Service. For example: `postgresql+psycopg://<user>:<password>@<postgres-service>.<namespace>.svc.cluster.local:5432/intelichat` (URL-encode reserved characters in credentials). Supply database credentials, `SECRET_KEY`, and AI credentials through Kubernetes Secrets rather than putting secrets in an image or ConfigMap. Keep the database in a persistent volume and make sure it has the pgvector extension enabled. The image runs as non-root UID `10001`; the API listens on `0.0.0.0:8000`, so expose it with a Kubernetes Service targeting port `8000`.

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

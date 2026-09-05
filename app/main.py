from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, conversations, documents, health
from app.core.config import get_settings
from app.database import ensure_schema, engine

settings = get_settings()
ensure_schema()

app = FastAPI(
    title="IntelliChat API",
    description="Enterprise AI knowledge assistant backend with document ingestion, vector search, and conversational RAG.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "IntelliChat API is running"}

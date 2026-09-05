from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=settings.environment == "development", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def _ensure_pgvector_extension() -> None:
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    except Exception:
        pass


def ensure_schema() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        if "users" in existing_tables:
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "created_at" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()"))
        if "documents" in existing_tables:
            document_columns = {column["name"] for column in inspector.get_columns("documents")}
            if "user_id" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN user_id INTEGER"))
            if "updated_at" not in document_columns:
                pass
        if "document_chunks" in existing_tables:
            chunk_columns = {column["name"] for column in inspector.get_columns("document_chunks")}
            if "chunk_index" not in chunk_columns:
                connection.execute(text("ALTER TABLE document_chunks ADD COLUMN chunk_index INTEGER DEFAULT 0 NOT NULL"))
            if "embedding" not in chunk_columns:
                connection.execute(text("ALTER TABLE document_chunks ADD COLUMN embedding VECTOR(1536)"))
            if "created_at" not in chunk_columns:
                connection.execute(text("ALTER TABLE document_chunks ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL"))
        if "conversations" not in existing_tables:
            connection.execute(text("CREATE TABLE IF NOT EXISTS conversations (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, title VARCHAR(255) NOT NULL DEFAULT 'New conversation', created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL, updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL)"))
        if "messages" not in existing_tables:
            connection.execute(text("CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, conversation_id INTEGER NOT NULL, role VARCHAR(20) NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL)"))

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "IntelliChat"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/intellichat"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 5
    max_upload_size_mb: int = 10

    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    embedding_dimension: int = 1536
    use_mock_ai: bool = True

    environment: Literal["development", "production", "testing"] = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()

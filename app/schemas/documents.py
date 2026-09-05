from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    content_length: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentRead(BaseModel):
    id: int
    user_id: int
    filename: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentChunkRead(BaseModel):
    id: int
    document_id: int
    content: str
    chunk_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListItem(BaseModel):
    id: int
    filename: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkingConfig(BaseModel):
    chunk_size: int = Field(default=800, ge=50)
    chunk_overlap: int = Field(default=120, ge=0)

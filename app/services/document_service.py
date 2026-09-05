from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Document, DocumentChunk


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def validate_upload(self, file: UploadFile) -> None:
        if not file.filename:
            raise ValueError("A filename is required.")

        if not file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")

        max_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        if size > max_bytes:
            raise ValueError(f"File exceeds the maximum allowed size of {self.settings.max_upload_size_mb} MB.")

    def extract_text_from_pdf(self, file: UploadFile) -> str:
        try:
            import pypdf
        except ImportError as exc:
            raise RuntimeError("PDF support requires the pypdf package.") from exc

        file.file.seek(0)
        reader = pypdf.PdfReader(file.file)
        text_parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        return "\n\n".join(text_parts).strip()

    def chunk_text(self, text: str) -> list[str]:
        if not text:
            return []

        chunk_size = self.settings.chunk_size
        overlap = self.settings.chunk_overlap
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            if end == len(text):
                break
            start = max(0, end - overlap)
        return chunks

    def create_document(self, user_id: int, filename: str, content: str) -> Document:
        document = Document(user_id=user_id, filename=filename, content=content, created_at=datetime.utcnow())
        self.db.add(document)
        self.db.flush()
        return document

    def create_chunks_for_document(self, document_id: int, chunks: list[str]) -> list[DocumentChunk]:
        created: list[DocumentChunk] = []
        for index, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document_id,
                content=chunk_text,
                chunk_index=index,
                embedding=None,
                created_at=datetime.utcnow(),
            )
            self.db.add(chunk)
            created.append(chunk)
        self.db.flush()
        return created

    def list_documents_for_user(self, user_id: int) -> list[Document]:
        return self.db.scalars(select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())).all()

    def get_document_for_user(self, document_id: int, user_id: int) -> Document | None:
        return self.db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user_id))

    def delete_document_for_user(self, document_id: int, user_id: int) -> bool:
        document = self.get_document_for_user(document_id, user_id)
        if not document:
            return False
        self.db.delete(document)
        self.db.commit()
        return True

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models import Document
from app.schemas.documents import DocumentListItem, DocumentRead, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload a PDF document")
def upload_document(
    file: UploadFile,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    try:
        service.validate_upload(file)
        extracted_text = service.extract_text_from_pdf(file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    document = service.create_document(current_user.id, file.filename or "untitled.pdf", extracted_text)
    chunks = service.chunk_text(extracted_text)
    service.create_chunks_for_document(document.id, chunks)
    db.commit()
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        content_length=len(extracted_text),
        created_at=document.created_at,
    )


@router.get("", response_model=list[DocumentListItem], summary="List documents for the current user")
def list_documents(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    documents = DocumentService(db).list_documents_for_user(current_user.id)
    return documents


@router.get("/{document_id}", response_model=DocumentRead, summary="Get a document by ID")
def get_document(document_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    document = DocumentService(db).get_document_for_user(document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete("/{document_id}", summary="Delete a document")
def delete_document(document_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = DocumentService(db).delete_document_for_user(document_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.rag import RAGService
from app.core.dependencies import get_current_user, get_db
from app.models import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, summary="Ask a question against uploaded documents")
def chat_with_documents(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty.")

    conversation = None
    if payload.conversation_id is not None:
        conversation = db.get(Conversation, payload.conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id, title=payload.message[:60] or "New conversation")
        db.add(conversation)
        db.flush()

    rag = RAGService(db)
    answer, chunks = rag.answer_question(current_user.id, payload.message, top_k=5)

    message = Message(conversation_id=conversation.id, role="user", content=payload.message)
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=answer)
    db.add_all([message, assistant_message])
    conversation.updated_at = __import__("datetime").datetime.utcnow()
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message=answer,
        sources=[{
            "document_id": chunk.document_id,
            "filename": chunk.document.filename,
            "chunk_id": chunk.id,
            "similarity": round(float(chunk.embedding[0]) if chunk.embedding else 0.0, 6),
        } for chunk in chunks],
    )

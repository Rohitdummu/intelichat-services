from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models import Conversation, Message
from app.schemas.conversation import ConversationCreate, ConversationRead, MessageRead

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationRead, summary="Create a conversation")
def create_conversation(
    payload: ConversationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    title = payload.title or "New conversation"
    conversation = Conversation(user_id=current_user.id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("", response_model=list[ConversationRead], summary="List conversations for the current user")
def list_conversations(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc())).all()


@router.get("/{conversation_id}", response_model=dict, summary="Get a conversation and its messages")
def get_conversation(conversation_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = db.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.asc())).all()
    return {"conversation": conversation, "messages": [MessageRead.model_validate(message) for message in messages]}


@router.delete("/{conversation_id}", summary="Delete a conversation")
def delete_conversation(conversation_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"status": "deleted", "conversation_id": conversation_id}

"""
Conversation and History Endpoints
Manage chat sessions and message threads for the authenticated user.
"""
from typing import List
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.exceptions import EntityNotFoundException
from app.db.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ConversationCreate, ConversationOut, MessageOut
from app.api.deps import get_current_user

router = APIRouter()


@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new empty chat conversation session."""
    conv = Conversation(
        user_id=current_user.id,
        title=conv_in.title or "New Conversation"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationOut.model_validate(conv)


@router.get("", response_model=List[ConversationOut])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all conversation sessions belonging to the user."""
    convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(desc(Conversation.updated_at)).all()

    results = []
    for c in convs:
        count = db.query(Message).filter(Message.conversation_id == c.id).count()
        out = ConversationOut(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=count
        )
        results.append(out)

    return results


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_conversation_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all message history for a conversation."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise EntityNotFoundException("Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conv.id
    ).order_by(Message.created_at).all()

    return [MessageOut.model_validate(m) for m in messages]


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a conversation and all its messages."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise EntityNotFoundException("Conversation not found")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully."}

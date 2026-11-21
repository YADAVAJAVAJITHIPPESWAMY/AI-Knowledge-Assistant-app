"""
Chat and RAG Query Endpoints
Supports both synchronous grounded Q&A and Server-Sent Events (SSE) streaming with citations.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.db.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatQueryRequest, ChatResponse
from app.rag.pipeline import rag_pipeline
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
def chat_query(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes a RAG query over user documents.
    Grounded strictly in retrieved context passages with exact citations.
    """
    # 1. Resolve or create conversation
    conv = None
    if request.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conv:
        # Create new conversation with title derived from user query
        title = request.query[:45] + ("..." if len(request.query) > 45 else "")
        conv = Conversation(user_id=current_user.id, title=title)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Fetch past conversation turns for conversational context
    past_messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at).all()
    history = [{"role": m.role, "content": m.content} for m in past_messages]

    # 3. Save user's question
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=request.query,
        citations=[]
    )
    db.add(user_msg)
    db.commit()

    # 4. Run RAG Pipeline
    response = rag_pipeline.query(
        db=db,
        user_id=current_user.id,
        query_text=request.query,
        conversation_id=conv.id,
        document_ids=request.document_ids,
        chat_history=history
    )

    # 5. Persist assistant response with citations
    citations_data = [c.model_dump(mode="json") for c in response.citations]
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=response.answer,
        citations=citations_data
    )
    db.add(assistant_msg)
    db.commit()

    return response


@router.post("/stream")
def chat_stream(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streams RAG response tokens via Server-Sent Events (SSE).
    Sends citation metadata first, followed by incremental text chunks.
    """
    conv = None
    if request.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conv:
        title = request.query[:45] + ("..." if len(request.query) > 45 else "")
        conv = Conversation(user_id=current_user.id, title=title)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Save user message
    user_msg = Message(conversation_id=conv.id, role="user", content=request.query, citations=[])
    db.add(user_msg)
    db.commit()

    # Fetch past history
    past_messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at).all()
    history = [{"role": m.role, "content": m.content} for m in past_messages]

    return StreamingResponse(
        rag_pipeline.stream_query(
            db=db,
            user_id=current_user.id,
            query_text=request.query,
            conversation_id=conv.id,
            document_ids=request.document_ids,
            chat_history=history
        ),
        media_type="text/event-stream"
    )

"""
Chat and RAG Pydantic Schemas
"""
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CitationItem(BaseModel):
    citation_number: int
    document_id: UUID
    document_name: str
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_id: UUID
    excerpt: str
    similarity_score: float = 0.0


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[UUID] = None
    document_ids: Optional[List[UUID]] = None  # None = search all user documents


class ChatResponse(BaseModel):
    conversation_id: UUID
    query: str
    answer: str
    citations: List[CitationItem] = []
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationOut(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    citations: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

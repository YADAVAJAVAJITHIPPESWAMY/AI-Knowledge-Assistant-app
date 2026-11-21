"""
Document Pydantic Schemas
"""
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    processing_status: str
    page_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStatusOut(BaseModel):
    id: UUID
    filename: str
    processing_status: str
    page_count: int
    error_message: Optional[str] = None
    chunk_count: int = 0


class DocumentChunkOut(BaseModel):
    id: UUID
    chunk_index: int
    chunk_text: str
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section_title: Optional[str] = None
    token_count: int
    chunk_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class DocumentDetailOut(DocumentOut):
    chunks: List[DocumentChunkOut] = []


class DocumentContentOut(BaseModel):
    id: UUID
    filename: str
    file_type: str
    page_count: int
    content: str
    chunks: List[DocumentChunkOut] = []

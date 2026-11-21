"""
Document Chunk Model
Stores chunked text passages, embeddings (1536 dimensions for text-embedding-3-small),
page/slide/section references, and JSON metadata.
"""
import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from app.db.base import Base
from app.models.user import GUID

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None


class EmbeddingVector(TypeDecorator):
    """
    Type decorator that stores 1536-dimensional vectors using pgvector.Vector on PostgreSQL,
    or JSON-serialized list on SQLite/fallback databases.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR and Vector is not None:
            return dialect.type_descriptor(Vector(1536))
        return dialect.type_descriptor(JSON)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR and Vector is not None:
            return value
        # Fallback: store as JSON string or array
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(EmbeddingVector(), nullable=True)
    page_number = Column(Integer, nullable=True)
    slide_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    token_count = Column(Integer, default=0, nullable=False)
    # Using 'chunk_metadata' attribute mapped to 'metadata' column name to avoid DeclarativeBase collision
    chunk_metadata = Column("metadata", JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    user = relationship("User", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk doc={self.document_id} idx={self.chunk_index} page={self.page_number}>"

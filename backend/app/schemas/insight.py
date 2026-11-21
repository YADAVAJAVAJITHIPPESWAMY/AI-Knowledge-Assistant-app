"""
Knowledge Insights Pydantic Schemas
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    document_id: UUID
    focus_topic: Optional[str] = None


class CompareRequest(BaseModel):
    document_ids: List[UUID] = Field(..., min_length=2, max_length=5)
    aspect: Optional[str] = None


class KeyConceptsRequest(BaseModel):
    document_id: UUID
    max_concepts: int = Field(default=8, ge=3, le=20)


class StudyNotesRequest(BaseModel):
    document_id: UUID
    format: str = "bullet_points"  # bullet_points, flashcards, outline


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer_index: int
    explanation: str


class QuizResponse(BaseModel):
    document_id: UUID
    document_name: str
    quiz: List[QuizQuestion]


class InsightResponse(BaseModel):
    title: str
    document_ids: List[UUID]
    result: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

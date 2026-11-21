"""
Knowledge Insights API Endpoints
Provides Summarization, Multi-Document Comparison, Key Concepts, and Revision Quizzes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.insight import (
    SummarizeRequest,
    CompareRequest,
    KeyConceptsRequest,
    InsightResponse,
    QuizResponse
)
from app.services.insights_service import insights_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/summarize", response_model=InsightResponse)
def summarize_document(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Summarizes a selected user document with structured key takeaways."""
    return insights_service.summarize_document(
        db=db,
        user_id=current_user.id,
        document_id=request.document_id
    )


@router.post("/compare", response_model=InsightResponse)
def compare_documents(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compares 2 to 5 user documents, identifying common themes and differences."""
    return insights_service.compare_documents(
        db=db,
        user_id=current_user.id,
        document_ids=request.document_ids
    )


@router.post("/key-concepts", response_model=InsightResponse)
def extract_key_concepts(
    request: KeyConceptsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extracts fundamental concepts and definitions from a document."""
    return insights_service.extract_key_concepts(
        db=db,
        user_id=current_user.id,
        document_id=request.document_id,
        max_concepts=request.max_concepts
    )


@router.post("/quiz", response_model=QuizResponse)
def generate_revision_quiz(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates 5 multiple-choice revision questions grounded in the document."""
    return insights_service.generate_quiz(
        db=db,
        user_id=current_user.id,
        document_id=request.document_id
    )

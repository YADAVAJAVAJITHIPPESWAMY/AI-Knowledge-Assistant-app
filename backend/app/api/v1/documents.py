"""
Document Management API Endpoints
Upload, List, Detail, Preview Content, Status, Reprocess, and Delete.
Strictly isolated to documents owned by the authenticated user.
"""
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.exceptions import EntityNotFoundException, ForbiddenException
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.schemas.document import (
    DocumentOut,
    DocumentDetailOut,
    DocumentStatusOut,
    DocumentContentOut,
    DocumentChunkOut
)
from app.services.document_service import document_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/upload", response_model=DocumentOut, status_code=201)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a document (PDF, Word, PPTX, TXT, MD) up to 20MB.
    Saves file to object storage and begins asynchronous ingestion.
    """
    doc = document_service.upload_document(db=db, user_id=current_user.id, file=file)

    # Trigger background ingestion
    # Try Celery if active, otherwise trigger via FastAPI background_tasks for reliable execution
    try:
        from app.workers.tasks import process_document_task
        process_document_task.delay(str(doc.id))
    except Exception:
        # Fallback to in-process background worker
        background_tasks.add_task(document_service.process_document, db, doc.id)

    return DocumentOut.model_validate(doc)


@router.get("", response_model=List[DocumentOut])
def list_documents(
    query: Optional[str] = Query(None, description="Search by filename"),
    file_type: Optional[str] = Query(None, description="Filter by extension"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all documents belonging to the authenticated user."""
    filters = [Document.user_id == current_user.id]
    if query:
        filters.append(Document.filename.ilike(f"%{query.strip()}%"))
    if file_type:
        filters.append(Document.file_type == file_type.lower().strip())

    docs = db.query(Document).filter(*filters).order_by(desc(Document.created_at)).all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves document metadata and its chunks."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise EntityNotFoundException("Document not found")

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index).all()
    chunk_outs = [DocumentChunkOut.model_validate(c) for c in chunks]

    return DocumentDetailOut(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        processing_status=doc.processing_status,
        page_count=doc.page_count,
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunks=chunk_outs
    )


@router.get("/{document_id}/status", response_model=DocumentStatusOut)
def get_document_status(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Polls processing status of an uploaded document."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise EntityNotFoundException("Document not found")

    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
    return DocumentStatusOut(
        id=doc.id,
        filename=doc.filename,
        processing_status=doc.processing_status,
        page_count=doc.page_count,
        error_message=doc.error_message,
        chunk_count=chunk_count
    )


@router.get("/{document_id}/content", response_model=DocumentContentOut)
def get_document_content(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the full extracted text and chunk breakdown for previewing in the UI."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise EntityNotFoundException("Document not found")

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index).all()
    full_content = "\n\n".join(c.chunk_text for c in chunks)
    chunk_outs = [DocumentChunkOut.model_validate(c) for c in chunks]

    return DocumentContentOut(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        page_count=doc.page_count,
        content=full_content,
        chunks=chunk_outs
    )


@router.post("/{document_id}/reprocess", response_model=DocumentOut)
def reprocess_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retries processing on a failed document."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise EntityNotFoundException("Document not found")

    background_tasks.add_task(document_service.process_document, db, doc.id)
    doc.processing_status = "processing"
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.delete("/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently deletes document, storage files, chunks, and vector embeddings."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise EntityNotFoundException("Document not found")

    document_service.delete_document(db, doc)
    return {"message": f"Document '{doc.filename}' deleted successfully."}

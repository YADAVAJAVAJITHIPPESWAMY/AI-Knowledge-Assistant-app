"""
Celery Document Ingestion Tasks
"""
import uuid
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.document_service import document_service


@celery_app.task(name="app.workers.tasks.process_document_task", bind=True, max_retries=2)
def process_document_task(self, document_id_str: str):
    """
    Background worker task to extract, chunk, and embed uploaded documents.
    """
    doc_id = uuid.UUID(document_id_str)
    db = SessionLocal()
    try:
        doc = document_service.process_document(db, doc_id)
        return {
            "status": doc.processing_status,
            "document_id": str(doc.id),
            "pages": doc.page_count
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()

"""
Document Processing & Ingestion Service
Orchestrates file upload validation, secure storage, text extraction,
token-based chunking, embedding generation, and status management.
"""
import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import BadRequestException, EntityNotFoundException, FileValidationException
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.parsers import get_parser_for_file
from app.services.storage import storage_service
from app.services.chunking import chunking_service
from app.services.embedding_service import embedding_service


ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "pptx", "ppt", "txt", "md", "markdown"}


class DocumentService:
    def validate_file(self, file: UploadFile) -> str:
        """Validates filename extension and size restrictions."""
        if not file.filename or "." not in file.filename:
            raise FileValidationException("File must have a valid extension.")

        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise FileValidationException(
                f"Unsupported format '.{ext}'. Supported formats: PDF, DOCX, DOC, PPTX, PPT, TXT, MD"
            )
        return ext

    def upload_document(
        self,
        db: Session,
        user_id: uuid.UUID,
        file: UploadFile
    ) -> Document:
        """
        Validates, saves file to storage, and registers initial Document record.
        """
        ext = self.validate_file(file)

        # Read binary content
        content = file.file.read()
        file_size = len(content)

        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise BadRequestException(f"File exceeds maximum allowed size of 20MB ({file_size / (1024*1024):.1f}MB)")

        # Save to storage (MinIO or local)
        storage_path, checksum = storage_service.save_file(content, str(user_id), file.filename)

        # Create database record
        doc = Document(
            user_id=user_id,
            filename=file.filename,
            file_type=ext,
            file_size=file_size,
            storage_path=storage_path,
            checksum=checksum,
            processing_status="uploaded",
            page_count=0
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def process_document(self, db: Session, document_id: uuid.UUID) -> Document:
        """
        Ingestion pipeline:
        1. Fetch document & mark 'processing'
        2. Read file from storage
        3. Extract text & pages via parser
        4. Chunk text with overlap
        5. Generate 1536-dim embeddings
        6. Persist chunks in database
        7. Mark 'indexed'
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise EntityNotFoundException("Document not found")

        doc.processing_status = "processing"
        doc.error_message = None
        db.commit()

        try:
            # 1. Read file
            file_bytes = storage_service.get_file(doc.storage_path)
            if not file_bytes:
                raise ValueError("Could not read document file from storage.")

            # 2. Parse document
            parser = get_parser_for_file(doc.filename)
            parsed_doc = parser.parse(file_bytes, doc.filename)

            # 3. Chunk text
            chunks = chunking_service.chunk_document(parsed_doc)
            if not chunks:
                raise ValueError("No extractable readable text found in document.")

            # 4. Generate embeddings
            chunk_texts = [c.chunk_text for c in chunks]
            embeddings = embedding_service.get_embeddings(chunk_texts)

            # 5. Clear any prior chunks (for re-processing)
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

            # 6. Store chunks
            for idx, c in enumerate(chunks):
                emb = embeddings[idx] if idx < len(embeddings) else None
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    user_id=doc.user_id,
                    chunk_index=c.chunk_index,
                    chunk_text=c.chunk_text,
                    embedding=emb,
                    page_number=c.page_number,
                    slide_number=c.slide_number,
                    section_title=c.section_title,
                    token_count=c.token_count,
                    chunk_metadata=c.metadata
                )
                db.add(db_chunk)

            # 7. Update document status
            doc.processing_status = "indexed"
            doc.page_count = parsed_doc.total_pages
            doc.error_message = None
            db.commit()
            db.refresh(doc)
            return doc

        except Exception as e:
            db.rollback()
            doc.processing_status = "failed"
            doc.error_message = str(e)
            db.commit()
            db.refresh(doc)
            return doc

    def delete_document(self, db: Session, document: Document) -> bool:
        """Permanently deletes document, file from storage, chunks, and embeddings."""
        # 1. Remove stored file
        storage_service.delete_file(document.storage_path)

        # 2. Delete database record (cascades to chunks)
        db.delete(document)
        db.commit()
        return True


document_service = DocumentService()

"""
RAG Pipeline & Citation Accuracy Tests
Verifies grounding, source citations [1], [2], and passage metadata.
"""
import io
from app.services.document_service import document_service
from app.rag.pipeline import rag_pipeline
from fastapi import UploadFile


def test_rag_query_with_citations(client, test_user, test_user_token, db):
    # Upload and index learning materials
    notes = (
        "# System Architecture\n\n"
        "Database sharding partitions data across nodes to enable horizontal scaling.\n\n"
        "In contrast, caching stores hot data in Redis to prevent repeated disk queries."
    ).encode("utf-8")

    upload = UploadFile(filename="architecture.md", file=io.BytesIO(notes))
    doc = document_service.upload_document(db, test_user.id, upload)
    document_service.process_document(db, doc.id)

    # Perform chat query
    res = client.post(
        "/api/chat/query",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "query": "What is database sharding?",
            "document_ids": [str(doc.id)]
        }
    )
    assert res.status_code == 200
    data = res.json()

    assert "conversation_id" in data
    assert "answer" in data
    assert len(data["citations"]) >= 1

    citation = data["citations"][0]
    assert citation["document_name"] == "architecture.md"
    assert "sharding" in citation["excerpt"].lower()
    assert citation["citation_number"] == 1


def test_rag_query_no_relevant_docs(client, test_user_token):
    res = client.post(
        "/api/chat/query",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "query": "What is quantum entanglement in superconductors?"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "insufficient evidence" in data["answer"].lower()

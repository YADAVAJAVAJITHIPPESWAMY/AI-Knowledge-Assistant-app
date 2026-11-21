"""
Document Management Integration Tests
Tests file upload, validation, retrieval, preview, and deletion.
"""
import io


def test_upload_valid_markdown_document(client, test_user_token):
    content = b"# System Design Notes\n\nDatabase sharding divides a database into smaller, faster pieces called shards."
    res = client.post(
        "/api/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": ("system_design.md", io.BytesIO(content), "text/markdown")}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "system_design.md"
    assert data["file_type"] == "md"
    assert data["processing_status"] in ["uploaded", "processing", "indexed"]


def test_upload_invalid_extension(client, test_user_token):
    content = b"malicious executable or unknown format"
    res = client.post(
        "/api/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": ("program.exe", io.BytesIO(content), "application/octet-stream")}
    )
    assert res.status_code == 422
    assert "Unsupported format" in res.json()["detail"]


def test_list_documents(client, test_user_token):
    # Upload sample doc
    content = b"Microservices architecture separates concerns into discrete, loosely-coupled services."
    client.post(
        "/api/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": ("microservices.txt", io.BytesIO(content), "text/plain")}
    )

    res = client.get(
        "/api/documents",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 1
    assert any(d["filename"] == "microservices.txt" for d in docs)


def test_get_document_status_and_content(client, test_user, test_user_token, db):
    from app.services.document_service import document_service
    from fastapi import UploadFile

    # Directly create and process document
    file_bytes = b"# Caching Strategies\n\nRedis and Memcached are distributed in-memory data stores."
    upload = UploadFile(filename="caching.md", file=io.BytesIO(file_bytes))
    doc = document_service.upload_document(db, test_user.id, upload)
    document_service.process_document(db, doc.id)

    # Check status endpoint
    status_res = client.get(
        f"/api/documents/{doc.id}/status",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["processing_status"] == "indexed"
    assert status_res.json()["chunk_count"] >= 1

    # Check content endpoint
    content_res = client.get(
        f"/api/documents/{doc.id}/content",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert content_res.status_code == 200
    assert "Caching Strategies" in content_res.json()["content"]


def test_delete_document(client, test_user, test_user_token, db):
    from app.services.document_service import document_service
    from fastapi import UploadFile

    file_bytes = b"Temporary note to be deleted."
    upload = UploadFile(filename="temp.txt", file=io.BytesIO(file_bytes))
    doc = document_service.upload_document(db, test_user.id, upload)

    del_res = client.delete(
        f"/api/documents/{doc.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert del_res.status_code == 200

    # Ensure document no longer exists
    get_res = client.get(
        f"/api/documents/{doc.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert get_res.status_code == 404

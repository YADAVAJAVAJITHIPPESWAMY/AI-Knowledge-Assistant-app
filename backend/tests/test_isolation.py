"""
User-Data Isolation & Security Tests
Verifies that User B can NEVER access, search, retrieve, or delete User A's documents or chunks.
"""
import io
from app.services.document_service import document_service
from fastapi import UploadFile


def test_per_user_document_isolation(client, test_user, test_user_token, user2, user2_token, db):
    # 1. User A (test_user) uploads a secret document
    secret_text = b"Secret Strategy: User A confidential project codename Apollo."
    upload = UploadFile(filename="secret_apollo.txt", file=io.BytesIO(secret_text))
    doc_a = document_service.upload_document(db, test_user.id, upload)
    document_service.process_document(db, doc_a.id)

    # 2. User B lists documents -> should NOT see User A's document
    res_b_list = client.get(
        "/api/documents",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert res_b_list.status_code == 200
    b_docs = res_b_list.json()
    assert not any(d["id"] == str(doc_a.id) for d in b_docs)

    # 3. User B attempts direct access to User A's document -> 404 Not Found
    res_b_get = client.get(
        f"/api/documents/{doc_a.id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert res_b_get.status_code == 404

    # 4. User B attempts to delete User A's document -> 404 Not Found
    res_b_del = client.delete(
        f"/api/documents/{doc_a.id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert res_b_del.status_code == 404

    # 5. User B asks RAG query about "codename Apollo" -> must NOT retrieve User A's secret
    res_b_query = client.post(
        "/api/chat/query",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={"query": "What is project Apollo?"}
    )
    assert res_b_query.status_code == 200
    answer_data = res_b_query.json()
    assert len(answer_data["citations"]) == 0
    assert "insufficient evidence" in answer_data["answer"].lower()

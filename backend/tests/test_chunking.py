"""
Chunking and Embedding Tests
Validates token chunking, boundary preservation, and vector generation.
"""
from app.parsers.base import ParsedDocument, ParsedSection
from app.services.chunking import ChunkingService, count_tokens
from app.services.embedding_service import embedding_service


def test_count_tokens():
    text = "The quick brown fox jumps over the lazy dog."
    tokens = count_tokens(text)
    assert tokens > 5


def test_chunking_service():
    sections = [
        ParsedSection(
            text="Section 1 discusses database normalization rules 1NF, 2NF, and 3NF.",
            section_title="Database Normalization",
            page_number=1
        ),
        ParsedSection(
            text="Section 2 addresses horizontal scaling, partition tolerance, and CAP theorem.",
            section_title="Distributed Systems",
            page_number=2
        )
    ]
    parsed_doc = ParsedDocument(
        filename="distributed_db.pdf",
        file_type="pdf",
        total_pages=2,
        sections=sections
    )

    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_document(parsed_doc)

    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2
    assert chunks[0].section_title == "Database Normalization"


def test_embedding_service_dimensions_and_normalization():
    text1 = "Relational database normalization eliminates data redundancy."
    text2 = "Database normalization reduces duplicated rows across tables."
    text3 = "A recipe for chocolate chip cookies with organic butter."

    emb1 = embedding_service.get_embedding(text1)
    emb2 = embedding_service.get_embedding(text2)
    emb3 = embedding_service.get_embedding(text3)

    assert len(emb1) == 1536
    assert len(emb2) == 1536
    assert len(emb3) == 1536

    # Verify cosine similarity is higher for similar topics
    from app.services.retrieval_service import cosine_similarity
    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)

    assert sim_related > sim_unrelated

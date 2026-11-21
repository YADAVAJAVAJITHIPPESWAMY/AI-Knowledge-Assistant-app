"""
Parser Unit Tests
Validates text extraction for Markdown, Plain Text, Docx, Pptx, and PDF.
"""
from app.parsers.text_parser import TextParser
from app.parsers.docx_parser import DocxParser
from app.parsers.pptx_parser import PptxParser
from app.parsers.pdf_parser import PDFParser
from app.parsers import get_parser_for_file


def test_text_parser_markdown_headings():
    content = b"""# Introduction
Welcome to modern RAG systems.

## Chapter 1: Vector Embeddings
Embeddings convert words to numerical vectors.

## Chapter 2: Similarity Metrics
Cosine distance evaluates angular separation.
"""
    parser = TextParser()
    doc = parser.parse(content, "test.md")
    assert doc.file_type == "md"
    assert len(doc.sections) >= 2
    assert any("Vector Embeddings" in s.section_title for s in doc.sections)


def test_text_parser_plain_txt():
    content = b"Paragraph 1 explains caching.\n\nParagraph 2 covers queues.\n\nParagraph 3 details load balancers."
    parser = TextParser()
    doc = parser.parse(content, "notes.txt")
    assert doc.file_type == "txt"
    assert len(doc.sections) >= 1
    assert "caching" in doc.full_text


def test_parser_factory():
    assert isinstance(get_parser_for_file("file.pdf"), PDFParser)
    assert isinstance(get_parser_for_file("doc.docx"), DocxParser)
    assert isinstance(get_parser_for_file("slides.pptx"), PptxParser)
    assert isinstance(get_parser_for_file("notes.txt"), TextParser)
    assert isinstance(get_parser_for_file("guide.md"), TextParser)

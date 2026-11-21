"""
Citation Builder and Passage Extractor
Parses bracketed citations like [1], [2] in LLM output and maps them to chunk metadata.
"""
import re
from typing import List, Tuple, Dict, Any
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.schemas.chat import CitationItem


class CitationBuilder:
    @staticmethod
    def build_citations(
        scored_chunks: List[Tuple[DocumentChunk, Document, float]],
        response_text: str = ""
    ) -> List[CitationItem]:
        """
        Creates structured CitationItem objects for retrieved passages.
        If response_text is provided, includes passages referenced by [N].
        """
        citations: List[CitationItem] = []

        for idx, (chunk, doc, score) in enumerate(scored_chunks):
            citation_num = idx + 1

            # Extract clean excerpt (first 250 characters of chunk)
            excerpt = chunk.chunk_text.strip()
            if len(excerpt) > 280:
                excerpt = excerpt[:277] + "..."

            citation = CitationItem(
                citation_number=citation_num,
                document_id=doc.id,
                document_name=doc.filename,
                page_number=chunk.page_number,
                slide_number=chunk.slide_number,
                section_title=chunk.section_title or f"Section {chunk.chunk_index + 1}",
                chunk_id=chunk.id,
                excerpt=excerpt,
                similarity_score=round(score, 3)
            )
            citations.append(citation)

        return citations

    @staticmethod
    def format_context_for_prompt(scored_chunks: List[Tuple[DocumentChunk, Document, float]]) -> str:
        """
        Formats retrieved chunks into clear, tagged blocks for the LLM prompt.
        """
        if not scored_chunks:
            return "No relevant documents found."

        parts = []
        for idx, (chunk, doc, score) in enumerate(scored_chunks):
            passage_num = idx + 1
            meta_parts = [f"Document: {doc.filename}"]
            if chunk.page_number:
                meta_parts.append(f"Page: {chunk.page_number}")
            if chunk.slide_number:
                meta_parts.append(f"Slide: {chunk.slide_number}")
            if chunk.section_title:
                meta_parts.append(f"Section: {chunk.section_title}")

            header = f"[Passage {passage_num}] (" + " | ".join(meta_parts) + ")"
            parts.append(f"{header}\n{chunk.chunk_text}\n")

        return "\n".join(parts)


citation_builder = CitationBuilder()

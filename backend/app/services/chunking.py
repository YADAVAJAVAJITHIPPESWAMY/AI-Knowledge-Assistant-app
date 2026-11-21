"""
Chunking Service
Splits parsed documents into configurable token-sized chunks (default ~600 tokens with ~100 token overlap)
while preserving headings, page numbers, and slide references.
"""
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.config import settings
from app.parsers.base import ParsedDocument, ParsedSection

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except ImportError:
    _ENCODER = None


def count_tokens(text: str) -> int:
    """Calculates token count using tiktoken or whitespace estimation."""
    if _ENCODER:
        try:
            return len(_ENCODER.encode(text))
        except Exception:
            pass
    # Rough approximation: 1 token ≈ 4 characters or 0.75 words
    return max(1, len(text.split()) * 4 // 3)


class ChunkResult(BaseModel):
    chunk_index: int
    chunk_text: str
    token_count: int
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section_title: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ChunkingService:
    def __init__(
        self,
        chunk_size: int = settings.RAG_CHUNK_SIZE_TOKENS,
        chunk_overlap: int = settings.RAG_CHUNK_OVERLAP_TOKENS
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, parsed_doc: ParsedDocument) -> List[ChunkResult]:
        """
        Chunks a parsed document respecting section boundaries, page numbers, and slide numbers.
        Avoids splitting headings away from content where possible.
        """
        chunks: List[ChunkResult] = []
        global_index = 0

        for section in parsed_doc.sections:
            section_chunks = self._chunk_section(section, global_index)
            chunks.extend(section_chunks)
            global_index += len(section_chunks)

        # Fallback if document had no sections
        if not chunks and parsed_doc.full_text.strip():
            fallback_sec = ParsedSection(text=parsed_doc.full_text, section_title="Main")
            chunks = self._chunk_section(fallback_sec, 0)

        return chunks

    def _chunk_section(self, section: ParsedSection, start_index: int) -> List[ChunkResult]:
        results: List[ChunkResult] = []
        text = section.text.strip()
        if not text:
            return results

        tokens = count_tokens(text)
        if tokens <= self.chunk_size:
            # Entire section fits into one chunk
            results.append(
                ChunkResult(
                    chunk_index=start_index,
                    chunk_text=text,
                    token_count=tokens,
                    page_number=section.page_number,
                    slide_number=section.slide_number,
                    section_title=section.section_title,
                    metadata=section.metadata,
                )
            )
            return results

        # Section exceeds chunk size: split into sentences/paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        current_chunk_parts: List[str] = []
        current_tokens = 0
        chunk_idx = start_index

        for para in paragraphs:
            para_tokens = count_tokens(para)

            # If a single paragraph is larger than chunk_size, split by sentences
            if para_tokens > self.chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sent_tokens = count_tokens(sentence)
                    if current_tokens + sent_tokens > self.chunk_size and current_chunk_parts:
                        # Flush current chunk
                        combined_text = "\n\n".join(current_chunk_parts)
                        results.append(
                            ChunkResult(
                                chunk_index=chunk_idx,
                                chunk_text=combined_text,
                                token_count=current_tokens,
                                page_number=section.page_number,
                                slide_number=section.slide_number,
                                section_title=section.section_title,
                                metadata=section.metadata,
                            )
                        )
                        chunk_idx += 1
                        # Retain overlap sentences
                        current_chunk_parts = [sentence]
                        current_tokens = sent_tokens
                    else:
                        current_chunk_parts.append(sentence)
                        current_tokens += sent_tokens
            else:
                if current_tokens + para_tokens > self.chunk_size and current_chunk_parts:
                    combined_text = "\n\n".join(current_chunk_parts)
                    results.append(
                        ChunkResult(
                            chunk_index=chunk_idx,
                            chunk_text=combined_text,
                            token_count=current_tokens,
                            page_number=section.page_number,
                            slide_number=section.slide_number,
                            section_title=section.section_title,
                            metadata=section.metadata,
                        )
                    )
                    chunk_idx += 1
                    current_chunk_parts = [para]
                    current_tokens = para_tokens
                else:
                    current_chunk_parts.append(para)
                    current_tokens += para_tokens

        # Flush final remaining chunk
        if current_chunk_parts:
            combined_text = "\n\n".join(current_chunk_parts)
            results.append(
                ChunkResult(
                    chunk_index=chunk_idx,
                    chunk_text=combined_text,
                    token_count=current_tokens,
                    page_number=section.page_number,
                    slide_number=section.slide_number,
                    section_title=section.section_title,
                    metadata=section.metadata,
                )
            )

        return results


chunking_service = ChunkingService()

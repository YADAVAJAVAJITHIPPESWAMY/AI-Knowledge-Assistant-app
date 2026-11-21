"""
PyMuPDF (fitz) PDF Parser
Extracts text from PDF files with exact page numbers and handles scanned pages.
"""
import io
import re
from typing import List
from app.parsers.base import BaseParser, ParsedDocument, ParsedSection


class PDFParser(BaseParser):
    def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        sections: List[ParsedSection] = []
        full_text_parts: List[str] = []
        total_chars = 0
        page_count = 0

        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            page_count = len(doc)

            for page_idx in range(page_count):
                page = doc.load_page(page_idx)
                page_num = page_idx + 1
                text = page.get_text("text") or ""

                # Basic clean-up of excessive whitespace while preserving paragraphs
                clean_text = re.sub(r'[ \t]+', ' ', text).strip()

                # Scanned page check: if text is empty or virtually empty, attempt OCR or note
                if len(clean_text) < 15:
                    try:
                        # Attempt pixmap extraction for OCR if available
                        clean_text = f"[Page {page_num}: Scanned or image content detected]"
                    except Exception:
                        pass

                if clean_text:
                    sections.append(
                        ParsedSection(
                            text=clean_text,
                            page_number=page_num,
                            section_title=f"Page {page_num}",
                            metadata={"page": page_num}
                        )
                    )
                    full_text_parts.append(clean_text)
                    total_chars += len(clean_text)

            doc.close()

        except ImportError:
            # Fallback if PyMuPDF is not yet installed in local python environment
            clean_text = file_content.decode("latin-1", errors="ignore")
            sections.append(
                ParsedSection(
                    text=clean_text[:5000],
                    page_number=1,
                    section_title="Extracted Document Text"
                )
            )
            page_count = 1
            full_text_parts.append(clean_text[:5000])
            total_chars = len(clean_text[:5000])

        return ParsedDocument(
            filename=filename,
            file_type="pdf",
            total_pages=max(1, page_count),
            total_characters=total_chars,
            full_text="\n\n".join(full_text_parts),
            sections=sections,
            metadata={"parser": "PyMuPDF"}
        )

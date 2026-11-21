"""
python-docx Word Document Parser
Extracts headings, paragraphs, and tables while preserving section structure.
"""
import io
import re
from typing import List
from app.parsers.base import BaseParser, ParsedDocument, ParsedSection


class DocxParser(BaseParser):
    def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        sections: List[ParsedSection] = []
        full_text_parts: List[str] = []
        total_chars = 0

        try:
            import docx
            doc = docx.Document(io.BytesIO(file_content))
            current_heading = "General"
            current_section_paras: List[str] = []

            def flush_section():
                nonlocal current_section_paras, total_chars
                if current_section_paras:
                    section_text = "\n".join(current_section_paras).strip()
                    if section_text:
                        sections.append(
                            ParsedSection(
                                text=section_text,
                                section_title=current_heading,
                                metadata={"section": current_heading}
                            )
                        )
                        full_text_parts.append(section_text)
                        total_chars += len(section_text)
                    current_section_paras = []

            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue

                style_name = paragraph.style.name.lower() if paragraph.style else ""
                # Check if paragraph is a heading
                if "heading" in style_name:
                    flush_section()
                    current_heading = text
                else:
                    current_section_paras.append(text)

            # Process tables if present
            for table in doc.tables:
                table_lines = []
                for row in table.rows:
                    row_cells = [c.text.strip() for c in row.cells]
                    row_str = " | ".join(row_cells)
                    if row_str.strip():
                        table_lines.append(row_str)
                if table_lines:
                    current_section_paras.append("\nTable Data:\n" + "\n".join(table_lines))

            flush_section()

        except ImportError:
            # Fallback
            text = file_content.decode("utf-8", errors="ignore")
            sections.append(ParsedSection(text=text, section_title="Main Content"))
            full_text_parts.append(text)
            total_chars = len(text)

        # In Word documents, approximate page count (approx 400 words / 2500 chars per page)
        estimated_pages = max(1, total_chars // 2000 + (1 if total_chars % 2000 > 0 else 0))

        return ParsedDocument(
            filename=filename,
            file_type="docx",
            total_pages=estimated_pages,
            total_characters=total_chars,
            full_text="\n\n".join(full_text_parts),
            sections=sections,
            metadata={"parser": "python-docx"}
        )

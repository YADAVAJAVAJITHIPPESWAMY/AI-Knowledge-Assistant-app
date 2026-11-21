"""
Plain Text & Markdown Parser
Handles .txt and .md documents with encoding auto-detection and heading identification.
"""
import re
from typing import List
from app.parsers.base import BaseParser, ParsedDocument, ParsedSection


class TextParser(BaseParser):
    def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        # Detect encoding safely
        text = ""
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if not text:
            text = file_content.decode("utf-8", errors="replace")

        # Determine file type
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        file_type = "md" if ext in ["md", "markdown"] else "txt"

        sections: List[ParsedSection] = []
        full_text_parts: List[str] = []
        total_chars = 0

        if file_type == "md":
            # Split by Markdown headers (# Header)
            header_pattern = re.compile(r'^(#{1,6}\s+.+)$', re.MULTILINE)
            splits = header_pattern.split(text)

            current_title = "Introduction"
            if splits and splits[0].strip():
                # Content before the first heading
                intro = splits[0].strip()
                sections.append(ParsedSection(text=intro, section_title=current_title))
                full_text_parts.append(intro)
                total_chars += len(intro)

            # Iterate pairs of (heading, body)
            idx = 1
            while idx < len(splits):
                heading_raw = splits[idx].strip()
                heading_clean = re.sub(r'^#+\s*', '', heading_raw).strip()
                body = splits[idx + 1].strip() if idx + 1 < len(splits) else ""

                combined = f"{heading_raw}\n{body}" if body else heading_raw
                sections.append(
                    ParsedSection(
                        text=combined,
                        section_title=heading_clean or "Section",
                        metadata={"heading": heading_clean}
                    )
                )
                full_text_parts.append(combined)
                total_chars += len(combined)
                idx += 2
        else:
            # Plain text file: split into paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [text.strip()] if text.strip() else ["Empty document"]

            # Group every 3 paragraphs as a section
            chunk_paras = []
            for i, p in enumerate(paragraphs):
                chunk_paras.append(p)
                if len(chunk_paras) >= 3 or i == len(paragraphs) - 1:
                    sec_text = "\n\n".join(chunk_paras)
                    sections.append(
                        ParsedSection(
                            text=sec_text,
                            section_title=f"Section {len(sections) + 1}",
                            page_number=len(sections) + 1
                        )
                    )
                    full_text_parts.append(sec_text)
                    total_chars += len(sec_text)
                    chunk_paras = []

        estimated_pages = max(1, total_chars // 2000 + (1 if total_chars % 2000 > 0 else 0))

        return ParsedDocument(
            filename=filename,
            file_type=file_type,
            total_pages=estimated_pages,
            total_characters=total_chars,
            full_text="\n\n".join(full_text_parts),
            sections=sections,
            metadata={"parser": "TextParser", "format": file_type}
        )

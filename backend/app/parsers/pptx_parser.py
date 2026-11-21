"""
python-pptx PowerPoint Presentation Parser
Extracts slides and retains slide numbers and titles.
"""
import io
from typing import List
from app.parsers.base import BaseParser, ParsedDocument, ParsedSection


class PptxParser(BaseParser):
    def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        sections: List[ParsedSection] = []
        full_text_parts: List[str] = []
        total_chars = 0
        slide_count = 0

        try:
            import pptx
            prs = pptx.Presentation(io.BytesIO(file_content))
            slide_count = len(prs.slides)

            for idx, slide in enumerate(prs.slides):
                slide_num = idx + 1
                slide_title = f"Slide {slide_num}"
                slide_text_lines: List[str] = []

                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            line = paragraph.text.strip()
                            if line:
                                slide_text_lines.append(line)

                    # Extract text from tables if present in slide
                    elif shape.has_table:
                        for row in shape.table.rows:
                            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if row_cells:
                                slide_text_lines.append(" | ".join(row_cells))

                if slide_text_lines:
                    # Often the first line of the slide is its title
                    slide_title = slide_text_lines[0][:80]
                    body_text = "\n".join(slide_text_lines)

                    sections.append(
                        ParsedSection(
                            text=body_text,
                            slide_number=slide_num,
                            section_title=slide_title,
                            metadata={"slide": slide_num, "title": slide_title}
                        )
                    )
                    full_text_parts.append(f"[Slide {slide_num}: {slide_title}]\n" + body_text)
                    total_chars += len(body_text)

        except ImportError:
            text = file_content.decode("utf-8", errors="ignore")
            sections.append(ParsedSection(text=text, slide_number=1, section_title="Presentation Content"))
            full_text_parts.append(text)
            total_chars = len(text)
            slide_count = 1

        return ParsedDocument(
            filename=filename,
            file_type="pptx",
            total_pages=max(1, slide_count),
            total_characters=total_chars,
            full_text="\n\n".join(full_text_parts),
            sections=sections,
            metadata={"parser": "python-pptx", "slide_count": slide_count}
        )

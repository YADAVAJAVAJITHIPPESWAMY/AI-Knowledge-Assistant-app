"""
Parser Factory and Registry
Maps file extensions to appropriate parser implementations.
"""
from typing import Dict, Type
from app.core.exceptions import FileValidationException
from app.parsers.base import BaseParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DocxParser
from app.parsers.pptx_parser import PptxParser
from app.parsers.text_parser import TextParser

_PARSER_MAP: Dict[str, Type[BaseParser]] = {
    "pdf": PDFParser,
    "docx": DocxParser,
    "doc": DocxParser,   # Handled or fallback
    "pptx": PptxParser,
    "ppt": PptxParser,   # Handled or fallback
    "txt": TextParser,
    "md": TextParser,
    "markdown": TextParser,
}


def get_parser_for_file(filename: str) -> BaseParser:
    """Returns the appropriate parser instance for the given filename."""
    if "." not in filename:
        raise FileValidationException("File has no extension")
    ext = filename.rsplit(".", 1)[-1].lower()
    parser_cls = _PARSER_MAP.get(ext)
    if not parser_cls:
        raise FileValidationException(f"Unsupported file format: .{ext}")
    return parser_cls()

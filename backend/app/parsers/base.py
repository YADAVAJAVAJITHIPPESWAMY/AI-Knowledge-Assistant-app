"""
Base Parser Interface and Data Structures
Defines uniform contract for all document format extractors.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ParsedSection(BaseModel):
    text: str
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section_title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    filename: str
    file_type: str
    total_pages: int = 1
    total_characters: int = 0
    full_text: str = ""
    sections: List[ParsedSection] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        """
        Parses raw binary content into structured ParsedDocument with sections,
        preserving page numbers, slide numbers, and section titles.
        """
        pass

"""
File containing Pydantic models for representing the structured content extracted from PDFs, including sections, figures, tables, and metadata about the parsing process. These models are used to standardize the output of different PDF parsers and facilitate downstream processing and analysis of the extracted content.
"""

# Import external libraries
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParserType(str, Enum):
    """
    Types of PDF parsers. Currently only 'docling' supported, but extendable in future.
    """

    DOCLING: str = "docling"


class PaperSection(BaseModel):
    """
    Represents a section of paper with title, content, and hierarchy level.
    """

    section_title: str = Field(..., description="Section title")
    section_content: str = Field(..., description="Section content")
    level: int = Field(default=1, description="Section hierarchy level (e.g., 1 for main sections, 2 for subsections)")


class PaperFigure(BaseModel):
    """
    Represents a figure in a paper, including its caption and identifier.
    """

    figure_id: str = Field(..., description="Unique identifier for the figure")
    figure_caption: str = Field(..., description="Caption describing the figure")


class PaperTable(BaseModel):
    """
    Represents a table in a paper, including its caption and identifier.
    """

    table_id: str = Field(..., description="Unique identifier for the table")
    table_caption: str = Field(..., description="Caption describing the table")
    table_content: str = Field(..., description="Table content extracted as text/markdown")


class PdfContent(BaseModel):
    """
    Represents content extracted from a PDF, including sections, figures, tables, raw text, references, and metadata about parser used.
    """

    paper_sections: List[PaperSection] = Field(
        default_factory=list,
        description="List of sections extracted from paper",
    )
    paper_figures: List[PaperFigure] = Field(
        default_factory=list,
        description="List of figures extracted from paper",
    )
    paper_tables: List[PaperTable] = Field(
        default_factory=list,
        description="List of tables extracted from paper",
    )
    raw_text: str = Field(..., description="Full raw text extracted from PDF")

    references: List[str] = Field(
        default_factory=list,
        description="List of references extracted from paper",
    )

    parser_used: ParserType = Field(..., description="Type of parser used for extraction")

    # Parser metadata
    page_count: Optional[int] = Field(
        None,
        description="Number of pages in the PDF",
    )
    file_size_bytes: Optional[int] = Field(
        None,
        description="Size of the PDF file in bytes",
    )
    parse_duration_seconds: Optional[float] = Field(
        None,
        description="Time taken to parse the PDF in seconds",
    )
    additional_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the parsing process",
    )

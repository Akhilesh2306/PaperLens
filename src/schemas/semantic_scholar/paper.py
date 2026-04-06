"""
File for paper Pydantic schemas. These schemas will be used for data validation and serialization when working with paper data from Semantic Scholar API and when storing/retrieving papers from the database.
"""

# Import external libraries
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

"""
SemanticScholarPaper → Parses raw Semantic Scholar API JSON (camelCase, nested objects)
PaperCreate          → Flattened, snake_case, matches ORM columns, used for DB insertion
PaperResponse        → PaperCreate + id + timestamps, used for API responses
"""


class SemanticScholarPaper(BaseModel):
    """
    Schema for Semantic Scholar API response data.
    Simplified version with only core metadata fields, can be extended with additional fields.
    """

    semantic_scholar_id: str = Field(..., alias="paperId", description="Semantic Scholar paper ID")
    title: str = Field(..., description="Paper title", max_length=200)
    abstract: Optional[str] = Field(None, description="Paper abstract")
    publication_date: Optional[str] = Field(None, alias="publicationDate", description="Publication date")
    year: Optional[int] = Field(None, description="Publication year")
    venue: Optional[str] = Field(None, description="Publication venue")
    authors: Optional[list[dict[str, Any]]] = Field(None, description="List of authors")
    fields_of_study: Optional[list[str]] = Field(None, alias="fieldsOfStudy", description="List of fields of study")
    url: Optional[str] = Field(None, description="URL to paper on Semantic Scholar")
    is_open_access: Optional[bool] = Field(None, alias="isOpenAccess", description="Whether the paper is open access")
    pdf_url: Optional[dict[str, str]] = Field(None, alias="openAccessPdf", description="URL to PDF if available")
    reference_count: Optional[int] = Field(None, alias="referenceCount", description="Number of references")
    citation_count: Optional[int] = Field(None, alias="citationCount", description="Number of citations")
    # doi: Optional[str] = Field(None, description="DOI of the paper")
    tldr: Optional[dict[str, str]] = Field(None, description="TLDR summary of the paper if available")

    # Helps to instantiate using either the alias (camelCase) or the field name (snake_case)
    model_config = ConfigDict(populate_by_name=True)


class PaperBase(BaseModel):
    """
    Base schema for paper data. This is what will be passed to the repository layer for creating/updating papers in the database. Extendable with additional fields if needed.
    """

    semantic_scholar_id: str = Field(..., description="Semantic Scholar paper ID")
    title: str = Field(..., description="Paper title", max_length=200)
    abstract: Optional[str] = Field(None, description="Paper abstract")
    publication_date: Optional[str] = Field(None, description="Publication date")
    year: Optional[int] = Field(None, description="Publication year")
    venue: Optional[str] = Field(None, description="Publication venue")
    authors: Optional[list[dict[str, Any]]] = Field(None, description="List of authors")
    fields_of_study: Optional[list[str]] = Field(None, description="List of fields of study")
    url: Optional[str] = Field(None, description="URL to paper on Semantic Scholar")
    is_open_access: Optional[bool] = Field(None, description="Whether the paper is open access")
    pdf_url: Optional[str] = Field(None, description="URL to PDF if available")
    reference_count: Optional[int] = Field(None, description="Number of references")
    citation_count: Optional[int] = Field(None, description="Number of citations")
    doi: Optional[str] = Field(None, description="DOI of the paper")
    tldr: Optional[str] = Field(None, description="TLDR summary of the paper if available")


class PaperCreate(PaperBase):
    """
    Schema for creating a paper in the database.
    Inherits all fields from PaperBase and can be extended with additional fields if needed.
    """

    # Parsed PDF content (optional - added when PDF is processed)
    raw_text: Optional[str] = Field(None, description="Full raw text extracted from PDF")
    sections: Optional[list[dict[str, Any]]] = Field(None, description="List of sections with titles and content")

    # Parser and PDF processing metadata (optional)
    parser_used: Optional[str] = Field(None, description="Which parser was used")
    parser_metadata: Optional[dict[str, Any]] = Field(None, description="Additional parser metadata")

    pdf_processed: Optional[bool] = Field(None, description="Whether PDF was successfully processed")
    pdf_processing_date: Optional[datetime] = Field(None, description="When PDF was processed")


class PaperResponse(PaperCreate):
    """
    Schema for returning a paper from the database.
    Inherits all fields from PaperCreate and can be extended with additional fields if needed.
    """

    id: UUID = Field(..., description="Unique identifier for the paper in the database")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="When the paper record was created in the database")
    updated_at: Optional[datetime] = Field(None, description="When the paper record was last updated in the database")

    # Allows instantiation using field names (snake_case) or aliases (camelCase)
    model_config = ConfigDict(from_attributes=True)

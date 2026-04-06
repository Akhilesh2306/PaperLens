"""
File for paper model. This is the main model that will be used to declare columns for papers table in PostgreSQL database.
"""

# Import external libraries
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

# Import internal modules
from src.db.interfaces.postgresql import Base


class Paper(Base):
    """
    Model for the papers table in PostgreSQL database.
    """

    __tablename__ = "papers"

    # Core Semantic Scholar paper metadata
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    semantic_scholar_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    publication_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    authors: Mapped[Optional[list[dict[str, str]]]] = mapped_column(JSON, nullable=True)
    fields_of_study: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_open_access: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Additional Semantic Scholar metadata fields
    reference_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    citation_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tldr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Parsed PDF content
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sections: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)

    # PDF processing metadata
    parser_used: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parser_metadata: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)

    pdf_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pdf_processing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

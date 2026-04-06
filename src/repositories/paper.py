"""
File for Paper repository implementation. This is the data access layer - all database queries related to Paper entities go through here. It takes AsyncSession and provides methods for CRUD operations and specific queries related to paper processing status.
"""

# Import external libraries
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Import internal modules
from src.models.paper import Paper
from src.schemas.semantic_scholar.paper import PaperCreate


class PaperRepository:
    """
    Repository class for managing Paper entities in database.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, paper: PaperCreate) -> Paper:
        """
        Create a new Paper record in the database.

        :param paper: PaperCreate schema instance containing paper data
        :return: The created Paper instance
        """
        # TODO: Add check for existing paper with same semantic_scholar_id to prevent duplicates

        # Create new Paper instance
        new_paper = Paper(**paper.model_dump())

        # Add to session and commit
        self.session.add(new_paper)
        await self.session.commit()

        # Refresh to get the generated ID and return
        await self.session.refresh(new_paper)

        return new_paper

    async def get_by_s2_id(self, semantic_scholar_id: str) -> Optional[Paper]:
        """
        Get a Paper by its semantic_scholar_id. This is the unique identifier from Semantic Scholar API.

        :param semantic_scholar_id: The Semantic Scholar paper ID to search for
        :return: The Paper instance if found, otherwise None
        """
        # TODO: Add caching layer here to reduce database load for frequently accessed papers

        # Query database for paper with semantic_scholar_id
        result = await self.session.execute(select(Paper).where(Paper.semantic_scholar_id == semantic_scholar_id))

        # Return the paper if found, otherwise None
        return result.scalar_one_or_none()

    async def get_by_id(self, paper_id: UUID) -> Optional[Paper]:
        """
        Get a Paper by its internal UUID ID.

        :param paper_id: The internal UUID of the paper to search for
        :return: The Paper instance if found, otherwise None
        """
        # TODO: Add caching layer here to reduce database load for frequently accessed papers

        # Query database for paper with given ID
        result = await self.session.execute(select(Paper).where(Paper.id == paper_id))

        # Return the paper if found, otherwise None
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Paper]:
        """
        Get all papers from database.

        :param limit: Number of papers to return (for pagination)
        :param offset: Number of papers to skip (for pagination)

        :return: Paginated list of all Paper instances in the database
        """
        # TODO: Add filtering options here (e.g. by year, venue, open access status) to allow more flexible queries
        # TODO: Add caching layer here to reduce database load for frequently accessed papers

        # Query database for all papers with pagination
        result = await self.session.execute(select(Paper).order_by(Paper.created_at.desc()).limit(limit).offset(offset))

        # Return list of papers
        return result.scalars().all()

    async def get_processed_papers(self, limit: int = 100, offset: int = 0) -> list[Paper]:
        """
        Get papers that have been successfully processed with PDF content.

        :param limit: Number of papers to return (for pagination)
        :param offset: Number of papers to skip (for pagination)

        :return: List of processed Paper instances
        """
        # TODO: Add filtering options here (e.g. by year, venue, open access status) to allow more flexible queries.

        # Query database for processed papers with pagination
        result = await self.session.execute(
            select(Paper)
            .where(Paper.pdf_processed == True)
            .order_by(Paper.pdf_processing_date.desc())
            .limit(limit)
            .offset(offset)
        )

        # Return list of processed papers
        return result.scalars().all()

    async def get_unprocessed_papers(self, limit: int = 100, offset: int = 0) -> list[Paper]:
        """
        Get papers that haven't been processed for PDF content yet.

        :param limit: Number of papers to return (for pagination)
        :param offset: Number of papers to skip (for pagination)

        :return: List of unprocessed Paper instances
        """
        # TODO: Add filtering options here (e.g. by year, venue, open access status) to allow more flexible queries.

        # Query database for unprocessed papers with pagination
        result = await self.session.execute(
            select(Paper)
            .where(Paper.pdf_processed == False)
            .order_by(Paper.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        # Return list of unprocessed papers
        return result.scalars().all()

    async def get_count(self) -> int:
        """
        Get total count of papers in the database.

        :return: Total number of papers in the database
        """
        # TODO: Add caching layer here to reduce database load for frequently accessed count (e.g. total count of papers doesn't change often, so can be cached for a period of time)

        # Query database for paper count
        result = await self.session.execute(select(func.count(Paper.id)))

        # Return the count (scalar) or 0
        return result.scalar() or 0

    async def get_processing_stats(self) -> dict:
        """
        Get PDF processing stats for papers in database.

        :return: Dictionary with relevant stats
        """
        # TODO: Add more stats here (e.g. average processing time, distribution of processing times, etc.) to provide more insights into PDF processing performance and bottlenecks.

        total_papers = await self.get_count()

        # Count processed papers
        processed_papers = await self.session.execute(select(func.count(Paper.id)).where(Paper.pdf_processed == True))
        processed_papers_count = processed_papers.scalar() or 0

        # Count papers with text
        papers_with_text = await self.session.execute(select(func.count(Paper.id)).where(Paper.raw_text != None))
        papers_with_text_count = papers_with_text.scalar() or 0

        # Return stats dictionary with calculated rates and counts
        return {
            "total_papers": total_papers,
            "processed_papers": processed_papers_count,
            "papers_with_text": papers_with_text_count,
            "processing_rate": (processed_papers_count / total_papers * 100) if total_papers > 0 else 0,
            "text_extraction_rate": (papers_with_text_count / processed_papers_count * 100) if processed_papers_count > 0 else 0,
        }

    async def update(self, paper: Paper) -> Paper:
        """
        Update an existing Paper record in the database.

        :param paper: Paper instance with updated data (must have valid ID)
        :return: The updated Paper instance
        """

        # TODO: Add check to ensure paper with given ID exists before updating

        # Add to session and commit
        self.session.add(paper)
        await self.session.commit()

        # Refresh to get latest data and return
        await self.session.refresh(paper)

        return paper

    async def upsert(self, paper: PaperCreate) -> Paper:
        """
        Upsert a Paper record in the database. If a paper with the same semantic_scholar_id exists, update it. Otherwise, create a new record.

        :param paper: PaperCreate schema instance containing paper data
        :return: The created or updated Paper instance
        """

        # Check if paper with same semantic_scholar_id already exists
        existing_paper = await self.get_by_s2_id(paper.semantic_scholar_id)
        if existing_paper:
            # Update existing paper with new data
            for field, value in paper.model_dump(exclude_unset=True).items():
                setattr(existing_paper, field, value)

            # Update the existing paper in the database
            return await self.update(existing_paper)

        else:
            # Create new paper in the database, also handles if paper doesn't exist
            return await self.create(paper)

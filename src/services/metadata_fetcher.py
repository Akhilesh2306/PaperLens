"""
MetadataFetcherService - an orchestrator service that coordinates fetching papers, downloading PDFs, parsing content, and storing metadata while keeping S2 client, PDF parser, and repository concerns separated.
"""

# Standard library
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

# Internal modules
from src.repositories.paper import PaperRepository
from src.schemas.pdf_parser.models import PdfContent
from src.schemas.semantic_scholar.paper import PaperCreate, SemanticScholarPaper
from src.services.pdf_parser.parser import PDFParserService
from src.services.semantic_scholar.client import SemanticScholarClient
from src.settings.config import Settings

# Setup logging
logger = logging.getLogger(__name__)


class MetadataFetcherService:
    """
    Orchestrates the process of fetching, parsing, and storing paper metadata.

        - Fetches paper metadata using the Semantic Scholar client.
        - Downloads PDFs when available and processes them using the PDF parser.
        - Stores the combined metadata and parsed content in the database via the repository layer.
        - Returns structured metadata and content for use in the application, while keeping concerns separated across different services.
    """

    def __init__(
        self,
        semantic_scholar_client: SemanticScholarClient,
        pdf_parser: PDFParserService,
        settings: Settings,
    ) -> None:
        """
        Initialize metadata fetcher service with necessary clients and settings.
        """

        # Get Semantic Scholar settings from centralized config
        self.s2_settings = settings.semantic_scholar

        # Get Semantic Scholar client
        self.semantic_scholar_client = semantic_scholar_client

        # Get PDF parser service
        self.pdf_parser = pdf_parser

        # Semaphore to limit concurrent PDF downloads and processing
        self._download_semaphore = asyncio.Semaphore(self.s2_settings.max_concurrent_downloads)

        # Semaphore to limit concurrent PDF parsing (set to 1 to avoid overloading the parser)
        self._parse_semaphore = asyncio.Semaphore(self.s2_settings.max_concurrent_parses)

    async def fetch_and_process_papers(
        self,
        query: str,
        session: AsyncSession,
    ) -> dict:
        """
        Main orchestrator - fetch papers from Semantic Scholar, download and parse PDFs, and store results in the database.

        :param query: Search query string to fetch papers from Semantic Scholar.
        :param session: AsyncSession instance for database operations.
        :return: Dict containing summary of operation including papers fetched, processed, and stored.
        """

        # Step 1: Initialize result summary
        stats = {
            "query": query,
            "papers_fetched": 0,
            "pdfs_downloaded": 0,
            "pdfs_parsed": 0,
            "papers_stored": 0,
            "pdfs_skipped": 0,
            "pdfs_failed": 0,
            "errors": [],
        }

        # Step 2: Search for papers using Semantic Scholar client
        try:
            papers = await self.semantic_scholar_client.search_papers(
                query=query,
                fields=self.s2_settings.paper_fields,
                fields_of_study=self.s2_settings.fields_of_study,
                limit=self.s2_settings.max_results,
            )

            stats["papers_fetched"] = len(papers)
            logger.info(f"Found {stats['papers_fetched']} papers for query {query}")

            if not papers:
                logger.info(f"No papers found for query {query}")
                return stats

        except Exception as e:
            logger.error(f"Error fetching papers from Semantic Scholar for query '{query}': {e}")
            stats["errors"].append(str(e))
            return stats

        # Step 3: Process papers - download and parse PDFs concurrently
        tasks = [self._download_and_parse_pdf(paper) for paper in papers]
        results = await asyncio.gather(*tasks)
        logger.info(f"Completed download and parse tasks for {len(results)} papers")

        # Step 4: Process results and Build PaperCreate instance for each paper
        papers_to_store = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in download and parse task: {result}")
                stats["errors"].append({"error": str(result), "stage": "download_parse"})
                continue

            paper, is_downloaded, pdf_content = result

            # Update PDF stats
            pdf_url = paper.pdf_url.get("url", None) if paper.pdf_url and paper.is_open_access else None

            if pdf_url is None:
                stats["pdfs_skipped"] += 1
                logger.debug(
                    f"No PDF available for paper - {paper.title} ({paper.semantic_scholar_id}), skipping download and parse"
                )

            elif is_downloaded and pdf_content:
                stats["pdfs_downloaded"] += 1
                stats["pdfs_parsed"] += 1
                logger.debug(f"Successfully downloaded and parsed PDF for paper - {paper.title} ({paper.semantic_scholar_id})")

            elif is_downloaded:
                stats["pdfs_downloaded"] += 1
                stats["pdfs_failed"] += 1  # downloaded but parse failed
                logger.warning(f"Downloaded PDF but failed to parse for paper - {paper.title} ({paper.semantic_scholar_id})")

            else:
                stats["pdfs_failed"] += 1
                logger.warning(f"Failed to download PDF for paper - {paper.title} ({paper.semantic_scholar_id})")

            # Build PaperCreate instance for each paper (with / without PDF content)
            paper_create = self._build_paper_create(
                paper=paper,
                pdf_content=pdf_content,
            )
            papers_to_store.append(paper_create)

        # Step 5: Store papers in database
        stats["papers_stored"] = await self._store_paper_to_db(
            papers_to_store,
            session,
        )

        logger.info(f"Finished processing papers for query '{query}' with stats: {stats}")
        return stats

    def _build_paper_create(
        self,
        paper: SemanticScholarPaper,
        pdf_content: Optional[PdfContent] = None,
    ) -> PaperCreate:
        """
        Build a PaperCreate schema instance from Semantic Scholar metadata and optional parsed PDF content. Not async since it's pure data transformation.

        :param paper: SemanticScholarPaper instance containing metadata from the API.
        :param pdf_content: Optional PdfContent instance containing parsed content and parser metadata.
        :return: PaperCreate instance ready to be stored in the database.
        """

        # Extract PDF url string if available
        pdf_url = paper.pdf_url.get("url", None) if paper.pdf_url else None

        # Extract TLDR text if available
        tldr_text = paper.tldr.get("text", None) if paper.tldr else None

        # Build base PaperCreate data from Semantic Scholar metadata
        paper_create_data = {
            "semantic_scholar_id": paper.semantic_scholar_id,
            "title": paper.title,
            "abstract": paper.abstract,
            "publication_date": paper.publication_date,
            "year": paper.year,
            "venue": paper.venue,
            "authors": paper.authors,
            "fields_of_study": paper.fields_of_study,
            "url": paper.url,
            "is_open_access": paper.is_open_access,
            "pdf_url": pdf_url,
            "reference_count": paper.reference_count,
            "citation_count": paper.citation_count,
            "tldr": tldr_text,
        }

        if pdf_content:
            # Add parsed PDF content and parser metadata if available
            paper_create_data.update({
                "raw_text": pdf_content.raw_text,
                "sections": [section.model_dump() for section in pdf_content.paper_sections],
                "pdf_processed": True,
                "pdf_processing_date": datetime.now(timezone.utc),
                "parser_used": pdf_content.parser_used.value,
                "parser_metadata": {
                    "page_count": pdf_content.page_count,
                    "file_size_bytes": pdf_content.file_size_bytes,
                    "parse_duration_seconds": pdf_content.parse_duration_seconds,
                },
            })

        return PaperCreate(**paper_create_data)

    async def _download_and_parse_pdf(
        self,
        paper: SemanticScholarPaper,
    ) -> tuple[SemanticScholarPaper, bool, Optional[PdfContent]]:
        """
        Download and parse the PDF for a given paper.

        :param paper: SemanticScholarPaper instance containing metadata from the API.
        :return: Tuple containing the original SemanticScholarPaper instance, a boolean indicating if the PDF was successfully downloaded, and an optional PdfContent instance if parsing was successful.
        """

        # Extract PDF url if available
        pdf_url = paper.pdf_url.get("url", None) if paper.pdf_url and paper.is_open_access else None

        if not pdf_url:
            logger.debug(f"No open access PDF available for paper - {paper.title} ({paper.semantic_scholar_id})")
            return (paper, False, None)

        is_downloaded = False
        try:
            # Download PDF with download semaphore to limit concurrent downloads
            async with self._download_semaphore:
                logger.debug(f"Downloading PDF for paper - {paper.title} ({paper.semantic_scholar_id})")
                pdf_path = await self.semantic_scholar_client.download_pdf(
                    paper_id=paper.semantic_scholar_id,
                    paper_url=pdf_url,
                )

            # If download failed, log and return early without attempting to parse
            if not pdf_path:
                logger.warning(f"Failed to download PDF for paper - {paper.title} ({paper.semantic_scholar_id})")
                return (paper, False, None)

            # Mark as downloaded before parsing
            is_downloaded = True

            # Parse PDF with parse semaphore to limit concurrent parsing
            async with self._parse_semaphore:
                logger.debug(f"Parsing PDF for paper - {paper.title} ({paper.semantic_scholar_id})")
                pdf_content = await self.pdf_parser.parse_pdf(pdf_path=Path(pdf_path))

            return (paper, True, pdf_content)

        except Exception as e:
            logger.error(f"Error processing PDF for paper - {paper.title} ({paper.semantic_scholar_id}): {e}")
            return (paper, is_downloaded, None)

    async def _store_paper_to_db(
        self,
        papers_data: list[PaperCreate],
        session: AsyncSession,
    ) -> int:
        """
        Store a list of PaperCreate instances in the database using the PaperRepository.

        :param papers_data: List of PaperCreate instances to store in the database.
        :param session: AsyncSession instance for database operations.
        :return: Number of papers successfully stored in the database.
        """

        # Counter for successfully stored papers
        stored_count = 0

        # Initialize paper repository with session
        paper_repo = PaperRepository(session)

        for paper_data in papers_data:
            try:
                # Nested transaction to ensure each paper is stored atomically, allowing us to continue processing other papers even if one fails
                async with session.begin_nested():
                    # Store paper in database
                    await paper_repo.upsert(paper_data)

                stored_count += 1

                logger.debug(f"Successfully stored paper {paper_data.title} ({paper_data.semantic_scholar_id}) to database")

            except Exception as e:
                logger.error(f"Error storing paper {paper_data.title} ({paper_data.semantic_scholar_id}) to database: {e}")
                continue

        try:
            await session.commit()  # Commit all changes after processing the batch

        except Exception as e:
            logger.error(f"Failed to commit batch: {e}")
            await session.rollback()
            raise

        return stored_count


def make_metadata_fetcher_service(
    semantic_scholar_client: SemanticScholarClient,
    pdf_parser: PDFParserService,
    settings: Settings,
) -> MetadataFetcherService:
    """
    Factory function to create an instance of MetadataFetcherService with all dependencies injected.

    :param semantic_scholar_client: SemanticScholarClient instance to fetch paper metadata and download PDFs.
    :param pdf_parser: PDFParserService instance to parse downloaded PDFs.
    :param settings: Settings instance containing configuration for the service.
    :return: An initialized MetadataFetcherService instance ready for use.
    """
    return MetadataFetcherService(
        semantic_scholar_client=semantic_scholar_client,
        pdf_parser=pdf_parser,
        settings=settings,
    )

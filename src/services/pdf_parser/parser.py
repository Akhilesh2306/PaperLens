"""
File containing the main PDF parsing service. This service will be responsible for orchestrating the PDF parsing process, and delegating the actual parsing to the appropriate parser (e.g., Docling).
"""

# Standard library
import asyncio
import logging
from pathlib import Path
from typing import Optional

# Internal modules
from src.exceptions import PDFParsingException, PDFValidationError
from src.schemas.pdf_parser.models import PdfContent
from src.services.pdf_parser.docling import DoclingParser

# Setup logging
logger = logging.getLogger(__name__)


class PDFParserService:
    """
    Main PDF parsing service. Currently uses Docling parser only, but can be extended to support multiple parsers in the future.
    """

    def __init__(
        self,
        max_pages: int,
        max_file_size_mb: int,
        do_ocr: bool = False,
        do_table_structure: bool = True,
    ):
        """
        Initialize PDF parser service.
        """

        self.docling_parser = DoclingParser(
            max_pages=max_pages,
            max_file_size_mb=max_file_size_mb,
            do_ocr=do_ocr,
            do_table_structure=do_table_structure,
        )

    async def parse_pdf(self, pdf_path: Path) -> Optional[PdfContent]:
        """
        Parse the PDF file and return structured content.

        :param pdf_path: Path to the PDF file
        :returns: PdfContent object containing structured content or None if parsing fails
        """

        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise PDFValidationError(f"PDF file not found: {pdf_path}")

        try:
            result = await asyncio.to_thread(self.docling_parser.parse_pdf, pdf_path)
            if result:
                logger.info(f"Successfully parsed PDF: {pdf_path.name}")
                return result

            else:
                logger.warning(f"Docling parsing returned no result for {pdf_path.name}")
                return None

        except (PDFValidationError, PDFParsingException):
            raise

        except Exception as e:
            logger.error(f"Docling parsing error for {pdf_path.name}: {e}")
            raise PDFParsingException(f"Docling parsing error for {pdf_path.name}: {e}")

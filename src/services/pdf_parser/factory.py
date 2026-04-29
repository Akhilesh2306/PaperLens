"""
File for PDF parser factory. This factory will be responsible for creating instances of different PDF parsers based on configurations. It will handle dependency injection and ensure that the parsers are properly configured with the necessary settings, such as page limits, file size limits, and any specific parsing options required by different parser implementations.
"""

# Standard library
from functools import lru_cache

# Internal modules
from src.services.pdf_parser.parser import PDFParserService
from src.settings.config import get_settings


@lru_cache(maxsize=1)
def make_pdf_parser_service() -> PDFParserService:
    """
    Factory function to create a cached instance of PDFParserService. This ensures that the same instance is reused across the application, avoiding unnecessary reinitialization of the parser and its underlying models.
    """

    # Get settings from the cofiguration
    settings = get_settings()

    # Return a configured instance of PDFParserService
    return PDFParserService(
        max_pages=settings.pdf_parser.max_pages,
        max_file_size_mb=settings.pdf_parser.max_file_size_mb,
        do_ocr=settings.pdf_parser.do_ocr,
        do_table_structure=settings.pdf_parser.do_table_structure,
    )

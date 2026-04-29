"""
File for Docling-based PDF parser implementation. This parser uses the Docling library to extract structured content from PDFs, including sections, figures, tables, and references. It includes comprehensive PDF validation to ensure that only valid and reasonably sized PDFs are processed, and it pre-warms the models to avoid cold start latency on the first parse.
"""

# Standard library
import logging
import time
from pathlib import Path

import pypdfium2 as pdfium

# Docling
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Internal modules
from src.exceptions import PDFParsingException, PDFValidationError
from src.schemas.pdf_parser.models import PaperSection, ParserType, PdfContent

# Setup logging
logger = logging.getLogger(__name__)


class DoclingParser:
    """
    Docling PDF parser for scientific document processing.
    """

    def __init__(
        self,
        max_pages: int,
        max_file_size_mb: int,
        do_ocr: bool = False,
        do_table_structure: bool = True,
    ) -> None:
        """
        Initialize DocumentConverter with optimized pipeline options.

        :param max_pages: Maximum number of pages to process
        :param max_file_size_mb: Maximum file size in MB
        :param do_ocr: Enable OCR for scanned PDFs (default: False, very slow)
        :param do_table_structure: Extract table structures (default: True)
        :return: None
        """

        # Configure pipeline options
        pipeline_options = PdfPipelineOptions(
            do_table_structure=do_table_structure,
            do_ocr=do_ocr,  # Usually disabled for speed
        )
        self._converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            }
        )
        self.max_pages = max_pages
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    def _validate_pdf(self, pdf_path: Path) -> bool:
        """
        Validate PDF file if it exists, for size and page limits.

        :param pdf_path: Path to PDF file
        :return: True if validates, False otherwise
        """

        try:
            file_size = pdf_path.stat().st_size

            # Check file exists and is not empty
            if file_size == 0:
                logger.error(f"PDF file is empty: {pdf_path}")
                raise PDFValidationError(f"PDF file is empty: {pdf_path}")

            # Check file size limit
            if file_size > self.max_file_size_bytes:
                logger.warning(
                    f"PDF file size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({self.max_file_size_bytes / 1024 / 1024:.1f}MB), skipping processing"
                )
                raise PDFValidationError(
                    f"PDF file size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({self.max_file_size_bytes / 1024 / 1024:.1f}MB)"
                )

            # Check if file starts with PDF header
            with open(pdf_path, "rb") as f:
                header = f.read(8)
                if not header.startswith(b"%PDF-"):
                    logger.error(f"File does not have PDF header: {pdf_path}")
                    raise PDFValidationError(f"File does not have PDF header: {pdf_path}")

            # Check page count
            pdf_reader = pdfium.PdfDocument(str(pdf_path))
            actual_pages = len(pdf_reader)
            pdf_reader.close()

            if actual_pages > self.max_pages:
                logger.warning(f"PDF page count ({actual_pages}) exceeds limit ({self.max_pages}), skipping processing")
                raise PDFValidationError(f"PDF page count ({actual_pages}) exceeds limit ({self.max_pages})")

            return True

        except PDFValidationError:
            raise  # Re-raise known validation errors without modification

        except Exception as e:
            logger.error(f"Error validating the PDF file: {e}")
            raise PDFValidationError(f"Error validating the PDF file: {e}")

    def parse_pdf(self, pdf_path: Path):
        """
        Parse the PDF file and return structured content.

        :param pdf_path: Path to PDF file
        :return: Parsed content or failure
        :raises PDFParsingException: If parsing fails due to validation or processing errors
        """

        try:
            # Validate the PDF file first
            self._validate_pdf(pdf_path=pdf_path)

            # If validation passes, proceed with parsing
            start_time = time.time()
            parsed_content = self._converter.convert(
                str(pdf_path),
                max_num_pages=self.max_pages,
                max_file_size=self.max_file_size_bytes,
            )
            parse_duration = time.time() - start_time
            logger.info(f"Parsed PDF {pdf_path} in {parse_duration:.2f} seconds")

            # Extract structured content from the parsed one
            doc = parsed_content.document

            # Extract paper sections
            sections = []
            current_section = {
                "title": "Content",
                "content": "",
            }

            for element in doc.texts:
                if hasattr(element, "label") and element.label in ("title", "section_header"):
                    # Save previous section if it has content
                    if current_section["content"].strip():
                        sections.append(
                            PaperSection(
                                section_title=current_section["title"],
                                section_content=current_section["content"].strip(),
                            )
                        )
                    # Start a new section
                    current_section = {
                        "title": element.text.strip(),
                        "content": "",
                    }
                else:
                    # Accumulate text into current section
                    if hasattr(element, "text") and element.text:
                        current_section["content"] += element.text + "\n"

            if current_section["content"].strip():
                sections.append(
                    PaperSection(
                        section_title=current_section["title"],
                        section_content=current_section["content"].strip(),
                    )
                )

            return PdfContent(
                paper_sections=sections,
                paper_figures=[],  # Placeholder for actual figure extraction logic
                paper_tables=[],  # Placeholder for actual table extraction logic
                raw_text=doc.export_to_text(),  # Full raw text extracted from PDF
                references=[],  # Placeholder for actual reference extraction logic
                parser_used=ParserType.DOCLING,
                page_count=len(doc.pages),
                file_size_bytes=pdf_path.stat().st_size,
                parse_duration_seconds=parse_duration,
            )

        except PDFValidationError as e:
            error_msg = str(e).lower()
            if "exceeds limit" in error_msg or "page count" in error_msg:
                logger.info(f"Skipping PDF due to limits: {e}")
                return None
            raise  # corrupt/invalid PDFs still raise

        except Exception as e:
            logger.error(f"Failed to parse PDF with Docling: {e}")
            logger.error(f"PDF path: {pdf_path}")
            logger.error(f"PDF size: {pdf_path.stat().st_size} bytes")
            logger.error(f"Error type: {type(e).__name__}")

            raise PDFParsingException(f"Error parsing PDF {pdf_path}: {e}")

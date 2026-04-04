"""
File containing custom exceptions hierarchy for the project.
The idea: every layer of the app (DB, API, parsing, search, LLM) has its own exception base class so you can catch errors at the right level of granularity.
"""


# Exceptions related to repository/database operations
class RepositoryException(Exception):
    """
    Base exception for repositoy-related errors such as DB connections, query failures, etc.
    """


class PaperNotFound(RepositoryException):
    """
    Exception raised when paper data is not found in the repository.
    """


class PaperNotSaved(RepositoryException):
    """
    Exception raised when paper data is not saved to the repository.
    """


# Exceptions related to OpenSearch
class OpenSearchException(Exception):
    """
    Exception raised for OpenSearch-related errors.
    """


# Exceptions related to PDF downloading, parsing, and validation
class PDFDownloadException(Exception):
    """
    Base exception for PDF download-related errors.
    """


class PDFDownloadTimeoutError(PDFDownloadException):
    """
    Exception raised when PDF download times out.
    """


class ParsingException(Exception):
    """
    Base exception for parsing-related errors such as data extraction, transformation, and validation issues.
    """


class PDFParsingException(ParsingException):
    """
    Exception raised for errors encountered during PDF parsing.
    """


class PDFValidationError(PDFParsingException):
    """
    Exception raised when PDF file validation fails, such as unsupported format, corrupted file, etc.
    """


# Exceptions related to LLM interactions
class LLMException(Exception):
    """
    Base exception for LLM-related errors such as API failures.
    """


class OllamaException(LLMException):
    """
    Exception raised for errors related to Ollama LLM interactions.
    """


class OllamaConnectionError(OllamaException):
    """
    Exception raised when connection to Ollama LLM fails.
    """


class OllamaTimeoutError(OllamaException):
    """
    Exception raised when Ollama LLM request times out.
    """


# Exceptions related to App configurations and environment variables
class ConfigurationError(Exception):
    """
    Exception raised for configuration errors such as missing environment variables, invalid settings, etc.
    """

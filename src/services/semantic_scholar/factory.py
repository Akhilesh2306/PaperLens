"""
File for Semantic Scholar service factory. This factory will be responsible for creating instances of the Semantic Scholar client and any related services. It will handle dependency injection and ensure that the client is properly configured with the necessary settings.
"""

# Internal modules
from src.services.semantic_scholar.client import SemanticScholarClient
from src.settings.config import get_settings


def make_semantic_scholar_client() -> SemanticScholarClient:
    """
    Factory function to create a Semantic Scholar client instance.

    :returns: An instance of the Semantic Scholar client
    """

    # Get settings from centralized config
    settings = get_settings()

    # Create Semantic Scholar client with explicit settings
    client = SemanticScholarClient(settings=settings)

    return client

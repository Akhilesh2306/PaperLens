"""
File for Semantic Scholar client. This client will handle all interactions with the Semantic Scholar API, including fetching paper metadata, downloading PDFs, and handling rate limits. It will also include error handling specific to Semantic Scholar API responses.
"""

# Import external libraries
import asyncio
import logging
import time
from pathlib import Path

import httpx

# Import internal modules
from src.exceptions import (
    SemanticScholarBadRequest,
    SemanticScholarPaperNotFound,
    SemanticScholarRateLimitError,
    SemanticScholarServerError,
)
from src.schemas.semantic_scholar.paper import SemanticScholarPaper
from src.settings.config import SemanticScholarSettings

# Setup logging
logger = logging.getLogger(__name__)


class SemanticScholarClient:
    """
    Client for interacting with the Semantic Scholar API.
     - Fetch paper metadata based on search queries or paper IDs.
     - Download PDFs of papers when available.
     - Handle rate limits and retries for API calls.
     - Provide error handling for common API issues such as bad requests, not found errors, and server errors.
    """

    def __init__(self, settings: SemanticScholarSettings):
        """
        Initialize the Semantic Scholar client with the provided settings.
        """
        self.settings = settings
        self._last_request_time: float = 0.0

    async def search_papers(
        self,
        query: str,
        fields: list[str],
        offset: int = 0,
        limit: int = None,
        fields_of_study: list[str] = None,
    ) -> list[SemanticScholarPaper]:
        """
        Search for papers based on a query and return their metadata.

        :param query: The search query string.
        :param fields: List of metadata fields to retrieve for each paper.
        :param offset: The number of results to skip (for pagination).
        :param limit: The maximum number of results to return.
        :param fields_of_study: List of fields of study to filter the search results.

        :return: A list of SemanticScholarPaper instances containing the metadata for each paper that matches the search query.
        """

        s2_api_url = f"{self.settings.base_url}/paper/search"

        params = {
            "query": query,
            "fields": ",".join(fields),
            "offset": offset,
            "limit": limit or self.settings.max_results,
        }

        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)

        # Get response from API and parse into list of SemanticScholarPaper instances
        response_data = await self._make_request(
            method="GET",
            url=s2_api_url,
            params=params,
        )
        logger.info(f"Search query '{query}' returned {len(response_data.get('data', []))} results.")

        paper_list = [SemanticScholarPaper(**paper) for paper in response_data.get("data", [])]

        return paper_list

    async def get_papers_batch(
        self,
        paper_ids: list[str],
        fields: list[str],
    ) -> list[SemanticScholarPaper]:
        """
        Fetch metadata for a batch of papers given their IDs.

        :param paper_ids: List of paper IDs to fetch metadata for.
        :param fields: List of metadata fields to retrieve for each paper.

        :return: A list of SemanticScholarPaper instances containing the metadata for each paper.
        """

        s2_paper_url = f"{self.settings.base_url}/paper/batch"

        # Params for batch request
        params = {
            "fields": ",".join(fields),
        }

        # Body for batch request
        body = {
            "ids": paper_ids,
        }

        # Get response from API and return list of paper metadata dicts
        response_data = await self._make_request(
            method="POST",
            url=s2_paper_url,
            params=params,
            json=body,
        )

        logger.info(f"Batch request for {len(paper_ids)} papers returned {len(response_data)} results.")

        # Parse response into list of SemanticScholarPaper instances
        paper_list = [SemanticScholarPaper(**paper) for paper in response_data if paper is not None]

        return paper_list

    async def download_pdf(
        self,
        paper_id: str,
        paper_url: str,
    ) -> str | None:
        """
        Download the PDF of a paper if available and save it to the pdf cache directory.

        :param paper_id: The ID of the paper to download.
        :param paper_url: The URL from which to download the PDF.

        :return: The file path of the downloaded PDF or None if not available.
        """

        # PDF save path
        pdf_save_path = Path(self.settings.pdf_cache_dir) / f"{paper_id}.pdf"

        # If PDF already exists in cache, return the path
        if pdf_save_path.exists():
            return str(pdf_save_path)

        # Create cache directory if it doesn't exist
        pdf_save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    paper_url,
                    timeout=30.0,
                    follow_redirects=True,
                )

            if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
                with open(pdf_save_path, "wb") as f:
                    f.write(response.content)

                logger.info(f"Downloaded PDF for paper {paper_id} to {pdf_save_path}")

                return str(pdf_save_path)

            else:
                logger.warning(f"PDF not available for paper {paper_id} at URL: {paper_url}")
                return None

        except Exception as e:
            logger.error(f"Error downloading PDF for paper {paper_id} from URL: {paper_url}. Error: {e}")
            return None

    async def _rate_limit(self) -> None:
        """
        Handle rate limiting by ensuring that API calls are spaced out according to the configured delay.
        """

        now = time.time()  # current time
        time_since_last_request = now - self._last_request_time  # time since last request

        if time_since_last_request < self.settings.rate_limit_delay:
            wait_time = self.settings.rate_limit_delay - time_since_last_request
            await asyncio.sleep(wait_time)  # sleep time

        self._last_request_time = time.time()  # update AFTER sleeping

    async def _make_request(
        self,
        method: str,
        url: str,
        params: dict = None,
        json: dict = None,
    ) -> dict:
        """
        Central HTTP call with retries and error handling for Semantic Scholar API requests.
        """

        max_retries = self.settings.max_retries
        for attempt in range(max_retries + 1):
            await self._rate_limit()  # Ensure to respect rate limits

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=self._get_headers(),
                    timeout=30.0,  # Set timeout for API calls
                )

            try:
                self._handle_response_errors(response)
                return response.json()  # Return the JSON data if no errors

            except (SemanticScholarRateLimitError, SemanticScholarServerError) as e:
                if attempt == max_retries:
                    raise

                backoff_time = self.settings.rate_limit_delay * (2**attempt)  # Exponential backoff
                logger.warning(f"Request failed with error: {e}. Retrying in {backoff_time:.2f} seconds...")

                await asyncio.sleep(backoff_time)  # wait before retrying

            except (SemanticScholarBadRequest, SemanticScholarPaperNotFound) as e:
                logger.error(f"Request failed with error: {e}. Not retrying since it's a client error.")
                raise

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """
        Handle errors in API responses. Map HTTP status codes to appropriate exceptions.
        """

        if response.status_code >= 400 and response.status_code < 599:
            try:
                error_data = response.json()
                error_message = error_data.get("error", response.text)

            except Exception:
                error_message = response.text

            if response.status_code == 400:
                raise SemanticScholarBadRequest(f"Bad request: {error_message}")

            elif response.status_code == 404:
                raise SemanticScholarPaperNotFound(f"Paper not found: {error_message}")

            elif response.status_code == 429:
                raise SemanticScholarRateLimitError(f"Rate limit exceeded: {error_message}")

            elif response.status_code >= 500:
                raise SemanticScholarServerError(f"Server error: {error_message}")

    def _get_headers(self) -> dict:
        """
        Build headers dict for API requests, including x-api-key if set
        """

        headers = {}
        headers["Accept"] = "application/json"

        if self.settings.api_key:
            headers["x-api-key"] = self.settings.api_key

        return headers

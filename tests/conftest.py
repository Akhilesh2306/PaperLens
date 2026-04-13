"""
Shared pytest fixtures for PaperLens tests.
Sets up async HTTP client with mocked database session so tests don't need real PostgreSQL.
"""

# Import external libraries
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

# Import internal modules
from src.dependencies import get_db_session
from src.main import app


@pytest.fixture
async def mock_db_session():
    """
    Creates a mock database session.
    mock_session.execute() is an AsyncMock, so awaiting it returns without error —
    this makes the health endpoint's `await db_session.execute(text("SELECT 1"))` succeed.
    """
    mock_session = AsyncMock()
    return mock_session


@pytest.fixture
async def async_client(mock_db_session):
    """
    Async HTTP client that talks to the FastAPI app with the database dependency mocked out.
    """

    # Override the real get_db_session with a fake async generator that yields the mock
    async def _override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_db_session] = _override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://paperlens-testserver") as client:
        yield client

    # Cleanup: remove the override so it doesn't leak into other tests
    app.dependency_overrides.clear()

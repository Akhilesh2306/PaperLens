"""
Test for the health router. This test for the /health endpoint. The test use a mocked database session to simulate both healthy and degraded database states.
"""

# Import internal modules
from src.schemas.api.health import HealthResponse


async def test_health_check_healthy(async_client):
    """
    Test the /health endpoint when the database is healthy.

    :param async_client: The async HTTP client fixture that talks to the FastAPI app with a mocked database session.
    :return: None
    """
    response = await async_client.get("/api/v1/health/")
    assert response.status_code == 200

    data = response.json()
    health_response = HealthResponse(**data)

    assert health_response.status == "ok"
    assert health_response.services["database"].status == "healthy"
    assert health_response.services["database"].message == "Connected successfully"


async def test_health_check_degraded(async_client, mock_db_session):
    """
    Test the /health endpoint when the database is degraded.

    :param async_client: Async HTTP client fixture
    :param mock_db_session: Mocked database session fixture

    :return: None
    """

    # Simulate database failure by making the execute method raise an exception
    mock_db_session.execute.side_effect = Exception("Database connection failed")

    response = await async_client.get("/api/v1/health/")
    assert response.status_code == 200

    data = response.json()
    health_response = HealthResponse(**data)

    assert health_response.status == "degraded"
    assert health_response.services["database"].status == "degraded"
    assert health_response.services["database"].message == "Failed to connect"

"""
File for ping route handler. A simple route to check if the application is running and responsive. It can also be used for health checks by load balancers or monitoring tools.
"""

# Import external libraries
from fastapi import APIRouter
from sqlalchemy import text

# Import internal modules
from src.dependencies import SessionDependency, SettingsDependency
from src.schemas.api.health import HealthResponse, ServiceStatus

health_router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@health_router.get("/")
async def health_check(
    settings: SettingsDependency,
    db_session: SessionDependency,
):
    """
    Health check endpoint to check if application is running.
    """

    # Check database health
    try:
        await db_session.execute(text("SELECT 1"))  # Simple query to check database connectivity
        db_status = "healthy"
    except Exception:
        db_status = "degraded"

    # Construct health response
    health_response = HealthResponse(
        status="ok" if db_status == "healthy" else "degraded",
        version=settings.app_version,
        environment=settings.environment,
        service_name=settings.service_name,
        services={
            "database": ServiceStatus(
                status=db_status,
                message="Connected successfully" if db_status == "healthy" else "Failed to connect",
            ),
        },
    )

    return health_response

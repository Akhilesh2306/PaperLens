"""
Main application entry point for PaperLens API.
Initializes FastAPI, middleware, and routes. Manages startup/shutdown lifecycle (database connections, cleanup).
"""

# Import external libraries
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

# Import internal modules
from src.db.factory import make_database
from src.routers.health import health_router
from src.settings.config import get_settings
from src.settings.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()


# Setup lifespan for startup/shutdown management
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events. It is used to initialize resources like database connections, external service clients, and perform any necessary cleanup on shutdown.
    """
    logger.info("Starting PaperLens API...")

    # Initialize settings and store in app state for global access
    app.state.settings = settings

    # Initialize database connection and store in app state
    database = await make_database()
    app.state.database = database

    # Initialize other services (e.g., OpenSearch, Telegram, etc.) and store in app state as needed

    logger.info("PaperLens API started successfully")

    yield  # Control is returned to FastAPI to handle requests until shutdown is triggered

    # Perform any necessary cleanup on shutdown
    logger.info("Shutting down PaperLens API...")

    # Close database connection
    await app.state.database.close()
    logger.info("Database connection closed")

    logger.info("PaperLens API shutdown complete")


# Initialize FastAPI app with lifespan for startup/shutdown management
app = FastAPI(
    title="PaperLens API",
    description="API for PaperLens - a research paper search and recommendation system.",
    version=settings.app_version,
    lifespan=lifespan,
)


# Import and include API routers
app.include_router(
    health_router,
    prefix="/api/v1",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8585,
    )

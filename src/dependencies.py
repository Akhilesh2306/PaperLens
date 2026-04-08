"""
File for defining dependencies that can be injected into FastAPI route handlers.
This is where you can set up things like database connections, authentication, or any other shared resources that your route handlers might need.
"""

# Import external libraries
from functools import lru_cache
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

# Import internal modules
from src.db.interfaces.base import BaseDatabase
from src.settings.config import Settings


@lru_cache  # Cache the settings instance to avoid reloading it on every request
def get_settings() -> Settings:
    """
    Get application settings.
    """
    return Settings()


def get_database(request: Request) -> BaseDatabase:
    """
    Get the database instance from the application state.

    :param request: FastAPI Request object
    :return: Database instance
    """
    return request.app.state.database


async def get_db_session(database: Annotated[BaseDatabase, Depends(get_database)]) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for a request.

    :param database: Database instance injected by FastAPI
    :return: Database session
    """
    async with database.get_session() as session:
        yield session


# Define type aliases for dependencies to be used in route handlers
SettingsDependency = Annotated[Settings, Depends(get_settings)]
DatabaseDependency = Annotated[BaseDatabase, Depends(get_database)]
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]

"""
File for base database repository class.
The idea is to have a common interface for all database repositories (e.g., OpenSearch, SQL, etc.) so that we can easily switch between different database implementations if needed.
"""

# Import external libraries
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class BaseDatabase(ABC):
    """
    Base class for database operations. This defines the contract any database backend must follow.
    """

    @abstractmethod
    async def startup(self) -> None:
        """
        Initialize the database connection, to be called when the application starts.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Close database connection and clean up resources, to be called when application shuts down.
        """

    @abstractmethod
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session which returns context manager yielding Session object.
        """


class BaseRepository(ABC):
    """
    Base repository pattern for data access. This defines the common CRUD operations that any repository should implement.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> Any:
        """
        Create a new record in the database.
        """

    @abstractmethod
    async def update(self, record_id: Any, data: dict[str, Any]) -> Any:
        """
        Update an existing record in database by its ID.
        """

    @abstractmethod
    async def delete(self, record_id: Any) -> bool:
        """
        Delete a record from the database by its ID.
        """

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> list[Any]:
        """
        List records from the database with pagination support.
        """

    @abstractmethod
    async def get_by_id(self, record_id: Any) -> Any:
        """
        Get a single record from database by its ID.
        """

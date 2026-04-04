"""
File for PostgreSQL database operations.
This implements the BaseDatabase interfaces for PostgreSQL using SQLAlchemy's async engine.
"""

# Import external libraries
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Import internal modules
from src.db.interfaces.base import BaseDatabase
from src.settings.logging import setup_logging

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)


# Define a base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Define the PostgreSQL database settings dataclass
@dataclass
class PostgreSQLSettings:
    """
    Configuration settings for PostgreSQL database connection. This can be extended with additional parameters as needed.
    """

    database_url: str = "postgresql+asyncpg://test_user:test_password@localhost:5432/paperlens_db"
    echo_sql: bool = False
    pool_size: int = 20
    max_overflow: int = 0


# Define the PostgreSQL database implementation
class PostgreSQLDatabase(BaseDatabase):
    """
    PostgreSQL database implementation which manages the database connection and provides a session factory for repositories to use.
    """

    def __init__(self, config: PostgreSQLSettings):
        self.config = config
        self.engine = None
        self.session_factory = None

    async def startup(self) -> None:
        """
        Initialize the PostgreSQL database connection and session factory.
        """
        try:
            logger.info(
                f"Attempting to connect to PostgreSQL at: {self.config.database_url.split('@')[1] if '@' in self.config.database_url else 'localhost'}"
            )

            # Create async engine
            self.engine = create_async_engine(
                url=self.config.database_url,
                echo=self.config.echo_sql,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,  # Ensure connections are valid before use
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )

            # Test the connection
            logger.info("Testing database connection...")
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")

            # Create tables if they don't exist (idempotent operation)
            async with self.engine.begin() as conn:
                # Get existing tables before creation
                existing_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

                # Create tables
                await conn.run_sync(Base.metadata.create_all)

                # Get updated tables after creation
                updated_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

                # Determine if any new tables were created
                new_tables = set(updated_tables) - set(existing_tables)

                if new_tables:
                    logger.info(f"Created new tables: {', '.join(new_tables)}")
                else:
                    logger.info("All tables already exist - no new tables created")

            logger.info("PostgreSQL database initialized successfully")
            assert self.engine is not None
            logger.info(f"Database: {self.engine.url.database} at {self.engine.url.host}:{self.engine.url.port} connected")
            logger.info("Database connection established")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL database: {e}")
            raise

    async def close(self) -> None:
        """
        Close the PostgreSQL database connection and dispose engine, called when application shuts down to clean up resources.
        """

        if self.engine:
            logger.info("Closing PostgreSQL database connections...")
            await self.engine.dispose()
            logger.info("PostgreSQL database connections closed")

    @asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a new database session from session factory. This is an async generator that yields a session and ensures it is properly closed after use.
        """

        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call startup() first.")

        # Create new session and yield it for use in repositories
        async with self.session_factory() as session:
            try:
                yield session

            except Exception:
                await session.rollback()
                raise

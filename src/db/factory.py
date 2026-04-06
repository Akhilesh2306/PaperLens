"""
File for factory function to create database instances based on configuration.
The idea is to centralize the logic for creating database connections and repositories, so that we can easily switch between different database implementations (e.g., PostgreSQL, OpenSearch) by changing the configuration without modifying the application code.
"""

# Import internal modules
from src.db.interfaces.base import BaseDatabase
from src.db.interfaces.postgresql import PostgreSQLDatabase, PostgreSQLSettings
from src.settings.config import get_settings


async def make_database() -> BaseDatabase:
    """
    Factory function to create database instance.

    :returns: An instance of database
    :rtype: BaseDatabase
    """

    # Get settings from centralized config
    settings = get_settings()

    # Create PostgreSQL config from settings
    config = PostgreSQLSettings(
        database_url=settings.postgres_database_url,
        echo_sql=settings.postgres_echo_sql,
        pool_size=settings.postgres_pool_size,
        max_overflow=settings.postgres_max_overflow,
    )

    database = PostgreSQLDatabase(config=config)
    await database.startup()

    return database

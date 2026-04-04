"""
File for factory function to create database instances based on configuration.
The idea is to centralize the logic for creating database connections and repositories, so that we can easily switch between different database implementations (e.g., PostgreSQL, OpenSearch) by changing the configuration without modifying the application code.
"""

# Import internal modules
from src.settings import get_settings
from src.db.interfaces.base import BaseDatabase
from src.db.interfaces.postgresql import PostgreSQLDatabase


def make_database():
    """
    Factory function to create database instance.


    """

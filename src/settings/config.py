"""
Configuration file containing all the necessary settings and parameters for the project including database configurations, API keys, logging settings, and other relevant information that can be easily modified without changing the core codebase.
"""

# Import external libraries
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define constants
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class BaseConfigSettings(BaseSettings):
    """
    Base configuration settings for the project.
    This class serves as a blueprint for all configuration settings.
    """

    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_nested_delimiter="__",  # Support nested env variables
        extra="ignore",  # Ignore extra fields
        frozen=True,  # Make settings immutable after initialization
        case_sensitive=False,  # Environment variables are case-insensitive
    )


class OpenSearchSettings(BaseConfigSettings):
    """
    Configuration settings for OpenSearch.
    """

    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_prefix="OPENSEARCH__",
        extra="ignore",
        frozen=True,
        case_sensitive=False,
    )

    host: str = "http://localhost:9200"
    index_name: str = "paperlens-index"
    chunk_index_suffix: str = "chunks"
    max_text_size: int = 1000000


class Settings(BaseConfigSettings):
    """
    Main configuration settings for the project, aggregating all individual service settings.
    """

    # General settings
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["DEV", "UAT", "PROD"] = "DEV"
    service_name: str = "paperlens-api"

    # Database settings
    postgres_database_url: str = "postgresql+asyncpg://test_user:test_password@localhost:5432/paperlens_db"
    postgres_echo_sql: bool = False
    postgres_pool_size: int = 20
    postgres_max_overflow: int = 0

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    ollama_timeout: int = 300

    # OpenSearch settings
    opensearch: OpenSearchSettings = Field(default_factory=OpenSearchSettings)

    @field_validator("postgres_database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """
        Validate the database URL. The app should not start if the URL is invalid to prevent runtime errors.
        """
        if not (value.startswith("postgresql://") or value.startswith("postgresql+asyncpg://")):
            raise ValueError("Invalid database URL. It must start with 'postgresql://' or 'postgresql+asyncpg://'")
        return value


def get_settings() -> Settings:
    """
    Get application settings from .env file.
    """
    return Settings()

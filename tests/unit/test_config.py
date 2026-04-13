"""
File for testing the configuration of the application. This includes testing that the settings are loaded correctly and that the application can connect to the database using the configured settings.
"""

# Import internal modules
from src.settings.config import Settings


def test_settings_load_defaults():
    """
    Test that the settings are loaded correctly from the environment variables.
    """
    settings = Settings()

    assert settings.app_version == "0.1.0"
    assert settings.environment == "DEV"
    assert settings.service_name == "paperlens-api-test"
    assert settings.debug == True


def test_settings_validate_database_url():
    """
    Test that the database URL is validated correctly.
    """
    # Valid database URL
    settings = Settings(postgres_database_url="postgresql+asyncpg://user:password@localhost:5432/paperlens")
    assert settings.postgres_database_url == "postgresql+asyncpg://user:password@localhost:5432/paperlens"

    # Invalid database URL
    try:
        Settings(postgres_database_url="invalid_database_url")
        assert False, "Expected ValueError for invalid database URL"
    except ValueError:
        pass


def test_opensearch_settings_defaults():
    """
    Test that the OpenSearch settings are loaded correctly from the environment variables.
    """
    settings = Settings()

    assert settings.opensearch.host == "http://localhost:9200"
    assert settings.opensearch.index_name == "paperlens-test-index"

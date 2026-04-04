"""
File for implementing logging configuration and utilities.
This includes setting up loggers, formatters, and handlers to ensure consistent logging across the application.
"""

# Import external libraries
import logging


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the application. This configures the root logger with a console handler and a standard format.

    :param log_level: The logging level to use (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

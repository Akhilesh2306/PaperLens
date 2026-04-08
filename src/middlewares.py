"""
Simple logging utilities for Week 1.

Not yet integrated into FastAPI's middleware system — that comes later.
For now, these are plain helper functions that route handlers or main.py can call directly.
"""

import logging

logger = logging.getLogger(__name__)


def log_request(method: str, path: str) -> None:
    """
    Log an incoming request.

    :param method: HTTP method of the request (e.g. GET, POST)
    :param path: URL path of the request (e.g. /papers)
    """
    logger.info(f"{method} {path}")


def log_error(error: str, method: str, path: str) -> None:
    """
    Log a request error.

    :param error: Error message or exception details
    :param method: HTTP method of the request that caused the error
    :param path: URL path of the request that caused the error
    """
    logger.error(f"Error in {method} {path}: {error}")

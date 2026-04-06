"""
File for health check API schema. This defines the Pydantic models used for the health check endpoint response, including overall service status and individual component statuses.
"""

# Import external libraries
from typing import Optional

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """
    Individual service status for health check response.
    """

    status: str = Field(..., description="Service status", examples=["healthy", "unhealthy"])
    message: Optional[str] = Field(
        None, description="Detailed message about the service status", examples=["Service is running smoothly", "Service is down"]
    )


class HealthResponse(BaseModel):
    """
    Health check response model including overall status and individual service statuses.
    """

    status: str = Field(
        ...,
        description="Overall health status",
        examples=[
            "ok",
            "degraded",
            "down",
        ],
    )
    version: str = Field(
        ...,
        description="Application version",
        examples=["0.1.0"],
    )
    environment: str = Field(
        ...,
        description="Deployment environment",
        examples=["DEV", "PROD"],
    )
    service_name: str = Field(
        ...,
        description="Service identifier",
        examples=["rag-api"],
    )
    services: Optional[dict[str, ServiceStatus]] = Field(
        None,
        description="Individual service statuses",
        examples=[
            {
                "database": {
                    "status": "healthy",
                    "message": "Connected successfully",
                }
            },
        ],
    )

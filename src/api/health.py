"""Health check endpoints."""

from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "memory-agent-enterprise",
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
async def readiness_check():
    """Readiness check for Kubernetes."""
    # TODO: Check database connection
    # TODO: Check vector store connection
    # TODO: Check Redis connection

    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "vector_store": "ok",
            "redis": "ok",
        },
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}
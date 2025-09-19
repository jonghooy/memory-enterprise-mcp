"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config import settings
from src.api import health, auth, mcp_mock
# Temporarily disable memory API that depends on services
# from src.api import memory
# Temporarily comment out LlamaIndex-dependent imports
# from src.services.memory_service import MemoryService
# from src.core.rag_engine import RAGEngine
# from src.core.vector_store import VectorStoreManager
# from src.mcp.server import setup_mcp_routes

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize services - temporarily disabled due to LlamaIndex issues
    # vector_store = VectorStoreManager()
    # rag_engine = RAGEngine(vector_store)
    # memory_service = MemoryService(rag_engine)

    # Store in app state
    # app.state.vector_store = vector_store
    # app.state.rag_engine = rag_engine
    # app.state.memory_service = memory_service
    logger.info("Services initialization temporarily disabled")

    yield

    # Shutdown
    logger.info("Shutting down application")
    # Cleanup if needed


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise Memory Agent with MCP support",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.memory-agent.com"],
    )

# Add Prometheus metrics
if settings.prometheus_enabled:
    Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(mcp_mock.router, tags=["mcp"])

# Include SSE MCP router
from src.mcp import sse_server
app.include_router(sse_server.router, tags=["mcp-sse"])

# Include JSON-RPC over SSE router
from src.mcp import jsonrpc_sse_server
app.include_router(jsonrpc_sse_server.router, tags=["mcp-jsonrpc-sse"])
# Temporarily disabled until LlamaIndex issues are resolved
# app.include_router(memory.router, prefix="/api/v1/memories", tags=["memories"])

# Setup MCP routes (initialized after app startup) - temporarily disabled
# @app.on_event("startup")
# async def setup_mcp():
#     """Setup MCP routes after services are initialized."""
#     if hasattr(app.state, 'memory_service'):
#         setup_mcp_routes(app, app.state.memory_service)
#         logger.info("MCP routes configured")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        workers=settings.workers if not settings.is_development else 1,
    )
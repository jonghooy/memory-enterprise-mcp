"""MCP server implementation for Claude/Cursor integration."""

import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import asyncio
import logging

from src.services.memory_service import MemoryService
from src.services.wiki_link_service import WikiLinkService
from src.core.config import settings

logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """MCP request model."""
    method: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    id: Optional[str] = None


class MCPResponse(BaseModel):
    """MCP response model."""
    result: Any
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]


class MCPServer:
    """MCP server for Claude/Cursor integration."""

    def __init__(self, memory_service: MemoryService):
        """Initialize MCP server."""
        self.memory_service = memory_service
        self.wiki_link_service = WikiLinkService()
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, MCPTool]:
        """Initialize available MCP tools."""
        return {
            "memory_search": MCPTool(
                name="memory_search",
                description="Search memories using semantic vector search",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID for multi-tenancy"
                        },
                        "metadata_filter": {
                            "type": "object",
                            "description": "Additional metadata filters"
                        }
                    },
                    "required": ["query", "tenant_id"]
                }
            ),
            "memory_create": MCPTool(
                name="memory_create",
                description="Create a new memory entry",
                parameters={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Memory content text"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID for multi-tenancy"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID who created the memory"
                        },
                        "source": {
                            "type": "object",
                            "description": "Source information",
                            "properties": {
                                "type": {"type": "string"},
                                "url": {"type": "string"},
                                "title": {"type": "string"}
                            }
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        }
                    },
                    "required": ["content", "tenant_id", "user_id"]
                }
            ),
            "memory_update": MCPTool(
                name="memory_update",
                description="Update an existing memory",
                parameters={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "Memory ID to update"
                        },
                        "content": {
                            "type": "string",
                            "description": "Updated content"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Updated metadata"
                        }
                    },
                    "required": ["memory_id"]
                }
            ),
            "memory_delete": MCPTool(
                name="memory_delete",
                description="Delete a memory",
                parameters={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "Memory ID to delete"
                        }
                    },
                    "required": ["memory_id"]
                }
            ),
            "memory_list": MCPTool(
                name="memory_list",
                description="List memories with pagination",
                parameters={
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID for multi-tenancy"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Filter by user ID"
                        },
                        "skip": {
                            "type": "integer",
                            "description": "Number of items to skip",
                            "default": 0
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50
                        }
                    },
                    "required": ["tenant_id"]
                }
            ),
            "wiki_link_extract": MCPTool(
                name="wiki_link_extract",
                description="Extract wiki-links from text",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to extract wiki-links from"
                        }
                    },
                    "required": ["text"]
                }
            ),
            "wiki_link_graph": MCPTool(
                name="wiki_link_graph",
                description="Generate knowledge graph from wiki-links",
                parameters={
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID for multi-tenancy"
                        },
                        "entity": {
                            "type": "string",
                            "description": "Central entity for the graph"
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Graph traversal depth",
                            "default": 2
                        }
                    },
                    "required": ["tenant_id"]
                }
            )
        }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request."""
        try:
            method = request.method
            params = request.params or {}

            if method == "tools/list":
                # List available tools
                result = {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters
                        }
                        for tool in self.tools.values()
                    ]
                }

            elif method == "tools/call":
                # Call a specific tool
                tool_name = params.get("tool")
                tool_params = params.get("params", {})

                if tool_name not in self.tools:
                    raise ValueError(f"Unknown tool: {tool_name}")

                result = await self._execute_tool(tool_name, tool_params)

            else:
                raise ValueError(f"Unknown method: {method}")

            return MCPResponse(
                result=result,
                id=request.id
            )

        except Exception as e:
            logger.error(f"MCP request error: {e}")
            return MCPResponse(
                result=None,
                error={
                    "code": -32603,
                    "message": str(e)
                },
                id=request.id
            )

    async def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a specific tool."""

        if tool_name == "memory_search":
            results = await self.memory_service.search_memories(
                query=params["query"],
                tenant_id=params["tenant_id"],
                limit=params.get("limit", 10),
                metadata_filter=params.get("metadata_filter")
            )
            return {
                "memories": [
                    {
                        "id": str(m.id),
                        "content": m.content,
                        "score": m.score if hasattr(m, 'score') else None,
                        "metadata": m.metadata,
                        "source": m.source.dict() if m.source else None,
                        "created_at": m.created_at.isoformat() if m.created_at else None
                    }
                    for m in results
                ]
            }

        elif tool_name == "memory_create":
            memory = await self.memory_service.create_memory(
                content=params["content"],
                tenant_id=params["tenant_id"],
                user_id=params["user_id"],
                source=params.get("source"),
                metadata=params.get("metadata", {})
            )
            return {
                "memory": {
                    "id": str(memory.id),
                    "content": memory.content,
                    "tenant_id": memory.tenant_id,
                    "user_id": memory.user_id,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                }
            }

        elif tool_name == "memory_update":
            memory = await self.memory_service.update_memory(
                memory_id=params["memory_id"],
                content=params.get("content"),
                metadata=params.get("metadata")
            )
            return {
                "memory": {
                    "id": str(memory.id),
                    "content": memory.content,
                    "updated_at": memory.updated_at.isoformat() if memory.updated_at else None
                }
            }

        elif tool_name == "memory_delete":
            success = await self.memory_service.delete_memory(
                memory_id=params["memory_id"]
            )
            return {"success": success}

        elif tool_name == "memory_list":
            memories = await self.memory_service.list_memories(
                tenant_id=params["tenant_id"],
                user_id=params.get("user_id"),
                skip=params.get("skip", 0),
                limit=params.get("limit", 50)
            )
            return {
                "memories": [
                    {
                        "id": str(m.id),
                        "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
                        "created_at": m.created_at.isoformat() if m.created_at else None
                    }
                    for m in memories
                ]
            }

        elif tool_name == "wiki_link_extract":
            links = self.wiki_link_service.extract_wiki_links(params["text"])
            return {"wiki_links": links}

        elif tool_name == "wiki_link_graph":
            graph = await self.memory_service.get_knowledge_graph(
                tenant_id=params["tenant_id"],
                entity=params.get("entity"),
                depth=params.get("depth", 2)
            )
            return {"graph": graph}

        else:
            raise ValueError(f"Tool not implemented: {tool_name}")

    async def handle_sse(self, request: MCPRequest) -> StreamingResponse:
        """Handle Server-Sent Events for streaming responses."""
        async def event_generator():
            try:
                # Start processing
                yield f"data: {json.dumps({'status': 'processing'})}\n\n"

                # Execute request
                response = await self.handle_request(request)

                # Send result
                yield f"data: {json.dumps(response.dict())}\n\n"

            except Exception as e:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                yield f"data: {json.dumps(error_response)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )


def setup_mcp_routes(app: FastAPI, memory_service: MemoryService):
    """Setup MCP routes in FastAPI app."""
    mcp_server = MCPServer(memory_service)

    @app.post("/mcp/request")
    async def handle_mcp_request(request: MCPRequest):
        """Handle MCP request."""
        response = await mcp_server.handle_request(request)
        return response

    @app.post("/mcp/stream")
    async def handle_mcp_stream(request: MCPRequest):
        """Handle MCP streaming request."""
        return await mcp_server.handle_sse(request)

    @app.get("/mcp/tools")
    async def list_mcp_tools():
        """List available MCP tools."""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
                for tool in mcp_server.tools.values()
            ]
        }

    logger.info("MCP routes configured successfully")
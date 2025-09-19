"""
MCP Server with SSE (Server-Sent Events) transport for Memory Enterprise.
This provides real-time streaming capabilities for web clients.
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any, Dict, AsyncGenerator, Optional
import json
import asyncio
import uuid
import logging
from datetime import datetime
import re

router = APIRouter(prefix="/mcp/sse", tags=["mcp-sse"])

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory storage for testing
memory_storage: Dict[str, Dict] = {}
# Session storage
sessions: Dict[str, Dict] = {}


class MCPMessage(BaseModel):
    """MCP message model."""
    jsonrpc: str = "2.0"
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


@router.get("/stream")
async def sse_stream(request: Request) -> StreamingResponse:
    """SSE endpoint for streaming MCP messages."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "initialized": False,
        "created_at": datetime.now().isoformat()
    }

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'session_id': session_id})}\n\n"

            # Keep connection alive and handle incoming messages
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                yield f"event: ping\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for session {session_id}")
        finally:
            # Clean up session
            if session_id in sessions:
                del sessions[session_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/message")
async def handle_message(message: MCPMessage) -> MCPMessage:
    """Handle incoming MCP messages."""
    try:
        method = message.method
        params = message.params or {}

        logger.debug(f"Handling SSE message: {method}")

        if method == "initialize":
            result = await initialize(params)
        elif method == "tools/list":
            result = await list_tools()
        elif method == "tools/call":
            result = await call_tool(params)
        elif method == "ping":
            result = {"pong": True}
        else:
            raise ValueError(f"Unknown method: {method}")

        return MCPMessage(
            jsonrpc="2.0",
            result=result,
            id=message.id
        )

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return MCPMessage(
            jsonrpc="2.0",
            error={
                "code": -32603,
                "message": str(e)
            },
            id=message.id
        )


async def initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the MCP session."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "prompts": {},
            "resources": {}
        },
        "serverInfo": {
            "name": "memory-enterprise-sse",
            "version": "1.0.0"
        }
    }


async def list_tools() -> Dict[str, Any]:
    """List available tools."""
    tools = [
        {
            "name": "memory_search",
            "description": "Search through stored memories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "tenant_id": {"type": "string"},
                    "limit": {"type": "number", "default": 10}
                },
                "required": ["query", "tenant_id"]
            }
        },
        {
            "name": "memory_create",
            "description": "Create a new memory entry",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "tenant_id": {"type": "string"},
                    "user_id": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["content", "tenant_id", "user_id"]
            }
        },
        {
            "name": "memory_update",
            "description": "Update an existing memory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string"},
                    "content": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["memory_id"]
            }
        },
        {
            "name": "memory_delete",
            "description": "Delete a memory entry",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string"}
                },
                "required": ["memory_id"]
            }
        },
        {
            "name": "memory_list",
            "description": "List all memories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "skip": {"type": "number", "default": 0},
                    "limit": {"type": "number", "default": 50}
                },
                "required": ["tenant_id"]
            }
        },
        {
            "name": "wiki_link_extract",
            "description": "Extract wiki-links from text",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    ]

    return {"tools": tools}


async def call_tool(params: Dict[str, Any]) -> Any:
    """Execute a tool."""
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})

    logger.debug(f"Calling tool: {tool_name}")

    if tool_name == "memory_create":
        memory_id = str(uuid.uuid4())
        memory = {
            "id": memory_id,
            "content": tool_args["content"],
            "tenant_id": tool_args["tenant_id"],
            "user_id": tool_args["user_id"],
            "metadata": tool_args.get("metadata", {}),
            "created_at": datetime.now().isoformat(),
            "wiki_links": extract_wiki_links(tool_args["content"])
        }
        memory_storage[memory_id] = memory

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Memory created with ID: {memory_id}"
                }
            ],
            "memory": memory
        }

    elif tool_name == "memory_search":
        query = tool_args["query"].lower()
        tenant_id = tool_args["tenant_id"]
        limit = tool_args.get("limit", 10)

        results = []
        for mem_id, memory in memory_storage.items():
            if memory["tenant_id"] != tenant_id:
                continue

            content_lower = memory["content"].lower()
            if any(word in content_lower for word in query.split()):
                score = sum(1 for word in query.split() if word in content_lower) / len(query.split())
                results.append({
                    "id": mem_id,
                    "content": memory["content"],
                    "score": score,
                    "metadata": memory.get("metadata", {}),
                    "created_at": memory.get("created_at")
                })

        results.sort(key=lambda x: x["score"], reverse=True)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"memories": results[:limit]}, indent=2)
                }
            ]
        }

    elif tool_name == "memory_update":
        memory_id = tool_args["memory_id"]
        if memory_id not in memory_storage:
            raise ValueError(f"Memory {memory_id} not found")

        memory = memory_storage[memory_id]
        if "content" in tool_args:
            memory["content"] = tool_args["content"]
            memory["wiki_links"] = extract_wiki_links(tool_args["content"])
        if "metadata" in tool_args:
            memory["metadata"].update(tool_args["metadata"])
        memory["updated_at"] = datetime.now().isoformat()

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Memory {memory_id} updated successfully"
                }
            ]
        }

    elif tool_name == "memory_delete":
        memory_id = tool_args["memory_id"]
        if memory_id in memory_storage:
            del memory_storage[memory_id]
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Memory {memory_id} deleted successfully"
                    }
                ]
            }
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Memory {memory_id} not found"
                }
            ]
        }

    elif tool_name == "memory_list":
        tenant_id = tool_args["tenant_id"]
        skip = tool_args.get("skip", 0)
        limit = tool_args.get("limit", 50)

        tenant_memories = [
            {
                "id": mem_id,
                "content": memory["content"][:200] + "..." if len(memory["content"]) > 200 else memory["content"],
                "created_at": memory.get("created_at")
            }
            for mem_id, memory in memory_storage.items()
            if memory["tenant_id"] == tenant_id
        ]

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"memories": tenant_memories[skip:skip + limit]}, indent=2)
                }
            ]
        }

    elif tool_name == "wiki_link_extract":
        text = tool_args["text"]
        links = extract_wiki_links(text)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"wiki_links": links}, indent=2)
                }
            ]
        }

    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def extract_wiki_links(text: str) -> list[str]:
    """Extract wiki-links from text."""
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, text)
    return list(set(matches))
"""
JSON-RPC over SSE (Server-Sent Events) MCP Server
Implements the standard JSON-RPC 2.0 protocol over SSE transport.

Specification:
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
- SSE: https://html.spec.whatwg.org/multipage/server-sent-events.html
- MCP: Model Context Protocol
"""

from fastapi import APIRouter, Request, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Literal
import json
import asyncio
import uuid
import logging
from datetime import datetime
from collections import defaultdict
import re
from enum import Enum

router = APIRouter(prefix="/mcp/jsonrpc-sse", tags=["mcp-jsonrpc-sse"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session storage
sessions: Dict[str, "SessionState"] = {}
# Message queues for each session
message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)


class JSONRPCErrorCode(Enum):
    """Standard JSON-RPC 2.0 error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Custom MCP error codes (-32000 to -32099)
    SESSION_NOT_FOUND = -32000
    UNAUTHORIZED = -32001
    RESOURCE_NOT_FOUND = -32002


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request."""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Optional[Union[str, int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"},
                "id": "1"
            }
        }


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response."""
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "jsonrpc": "2.0",
                "result": {"status": "success"},
                "id": "1"
            }
        }


class JSONRPCNotification(BaseModel):
    """JSON-RPC 2.0 Notification (no id field)."""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None


class SessionState:
    """Represents a session state."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.initialized = False
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.tenant_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.capabilities: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()


# In-memory storage for demo (replace with actual database)
memory_storage: Dict[str, Dict] = {}


def create_error_response(
    code: JSONRPCErrorCode,
    message: str,
    data: Optional[Any] = None,
    request_id: Optional[Union[str, int]] = None
) -> JSONRPCResponse:
    """Create a JSON-RPC error response."""
    error = {
        "code": code.value,
        "message": message
    }
    if data is not None:
        error["data"] = data

    return JSONRPCResponse(
        jsonrpc="2.0",
        error=error,
        id=request_id
    )


def create_success_response(
    result: Any,
    request_id: Optional[Union[str, int]] = None
) -> JSONRPCResponse:
    """Create a JSON-RPC success response."""
    return JSONRPCResponse(
        jsonrpc="2.0",
        result=result,
        id=request_id
    )


@router.get("/stream/{session_id}")
async def jsonrpc_sse_stream(
    session_id: str,
    request: Request
) -> StreamingResponse:
    """
    JSON-RPC over SSE stream endpoint.
    Establishes bidirectional communication using SSE for server->client
    and regular HTTP POST for client->server.
    """

    # Create or get session
    if session_id not in sessions:
        sessions[session_id] = SessionState(session_id)

    session = sessions[session_id]
    queue = message_queues[session_id]

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events with JSON-RPC messages."""
        try:
            # Send initial connection notification
            connection_notification = JSONRPCNotification(
                method="session.connected",
                params={
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "protocol": "jsonrpc-sse/2.0"
                }
            )
            yield f"data: {connection_notification.json()}\n\n"

            # Main event loop
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # Wait for messages with timeout for heartbeat
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Send the message as SSE event
                    if isinstance(message, dict):
                        yield f"data: {json.dumps(message)}\n\n"
                    else:
                        yield f"data: {message}\n\n"

                except asyncio.TimeoutError:
                    # Send heartbeat notification
                    heartbeat = JSONRPCNotification(
                        method="session.heartbeat",
                        params={
                            "session_id": session_id,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    yield f"data: {heartbeat.json()}\n\n"

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for session {session_id}")

        finally:
            # Send disconnection notification if possible
            try:
                disconnect_notification = JSONRPCNotification(
                    method="session.disconnected",
                    params={
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                yield f"data: {disconnect_notification.json()}\n\n"
            except:
                pass

            # Clean up session
            if session_id in sessions:
                del sessions[session_id]
            if session_id in message_queues:
                del message_queues[session_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.post("/request/{session_id}")
async def handle_jsonrpc_request(
    session_id: str,
    request: JSONRPCRequest,
    background_tasks: BackgroundTasks
) -> JSONRPCResponse:
    """
    Handle JSON-RPC requests from client.
    This endpoint processes the request and sends responses via SSE.
    """

    # Validate session
    if session_id not in sessions:
        return create_error_response(
            JSONRPCErrorCode.SESSION_NOT_FOUND,
            "Session not found",
            {"session_id": session_id},
            request.id
        )

    session = sessions[session_id]
    session.update_activity()

    try:
        # Route to appropriate handler
        result = await route_method(request.method, request.params, session)

        # Create response
        response = create_success_response(result, request.id)

        # For requests with ID, also send via SSE
        if request.id is not None:
            await message_queues[session_id].put(response.dict())

        return response

    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return create_error_response(
            JSONRPCErrorCode.INTERNAL_ERROR,
            str(e),
            None,
            request.id
        )


async def route_method(method: str, params: Any, session: SessionState) -> Any:
    """Route JSON-RPC method to appropriate handler."""

    # MCP standard methods
    if method == "initialize":
        return await handle_initialize(params, session)
    elif method == "initialized":
        return await handle_initialized(params, session)
    elif method == "tools/list":
        return await handle_list_tools(params, session)
    elif method == "tools/call":
        return await handle_call_tool(params, session)
    elif method == "resources/list":
        return await handle_list_resources(params, session)
    elif method == "resources/read":
        return await handle_read_resource(params, session)
    elif method == "prompts/list":
        return await handle_list_prompts(params, session)
    elif method == "prompts/get":
        return await handle_get_prompt(params, session)
    # Custom memory methods
    elif method.startswith("memory/"):
        return await handle_memory_method(method, params, session)
    else:
        raise ValueError(f"Method not found: {method}")


async def handle_initialize(params: Any, session: SessionState) -> Dict[str, Any]:
    """Handle initialize method."""
    session.initialized = True

    if isinstance(params, dict):
        session.capabilities = params.get("capabilities", {})
        if "clientInfo" in params:
            session.metadata["clientInfo"] = params["clientInfo"]

    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {"subscribe": True},
            "prompts": {},
            "logging": {}
        },
        "serverInfo": {
            "name": "memory-enterprise-jsonrpc-sse",
            "version": "1.0.0"
        }
    }


async def handle_initialized(params: Any, session: SessionState) -> Dict[str, Any]:
    """Handle initialized notification."""
    session.initialized = True
    return {"status": "acknowledged"}


async def handle_list_tools(params: Any, session: SessionState) -> Dict[str, Any]:
    """List available tools."""
    tools = [
        {
            "name": "memory_search",
            "description": "Search through stored memories using semantic search",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "limit": {"type": "number", "description": "Max results", "default": 10}
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
                    "content": {"type": "string", "description": "Memory content"},
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "user_id": {"type": "string", "description": "User ID"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
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
                    "memory_id": {"type": "string", "description": "Memory ID"},
                    "content": {"type": "string", "description": "New content"},
                    "metadata": {"type": "object", "description": "Updated metadata"}
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
                    "memory_id": {"type": "string", "description": "Memory ID to delete"}
                },
                "required": ["memory_id"]
            }
        },
        {
            "name": "memory_list",
            "description": "List all memories for a tenant",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID"},
                    "skip": {"type": "number", "default": 0},
                    "limit": {"type": "number", "default": 50}
                },
                "required": ["tenant_id"]
            }
        }
    ]

    return {"tools": tools}


async def handle_call_tool(params: Any, session: SessionState) -> Any:
    """Execute a tool."""
    if not isinstance(params, dict):
        raise ValueError("Invalid params for tool call")

    tool_name = params.get("name")
    tool_args = params.get("arguments", {})

    # Memory tools
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

        # Send notification to session
        notification = JSONRPCNotification(
            method="memory.created",
            params={"memory_id": memory_id, "tenant_id": tool_args["tenant_id"]}
        )
        await message_queues[session.session_id].put(notification.dict())

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Memory created with ID: {memory_id}"
                }
            ],
            "isError": False
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
            ],
            "isError": False
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
            ],
            "isError": False
        }

    else:
        raise ValueError(f"Unknown tool: {tool_name}")


async def handle_list_resources(params: Any, session: SessionState) -> Dict[str, Any]:
    """List available resources."""
    resources = [
        {
            "uri": f"memory://tenant/{session.tenant_id or 'default'}/all",
            "name": "All Memories",
            "description": "Access to all memories in the tenant",
            "mimeType": "application/json"
        }
    ]
    return {"resources": resources}


async def handle_read_resource(params: Any, session: SessionState) -> Dict[str, Any]:
    """Read a resource."""
    if not isinstance(params, dict) or "uri" not in params:
        raise ValueError("Invalid params for resource read")

    uri = params["uri"]

    # Parse memory URI
    if uri.startswith("memory://"):
        parts = uri.replace("memory://", "").split("/")
        if len(parts) >= 3 and parts[0] == "tenant":
            tenant_id = parts[1]

            memories = [
                memory for memory in memory_storage.values()
                if memory["tenant_id"] == tenant_id
            ]

            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(memories, indent=2)
                    }
                ]
            }

    raise ValueError(f"Resource not found: {uri}")


async def handle_list_prompts(params: Any, session: SessionState) -> Dict[str, Any]:
    """List available prompts."""
    prompts = [
        {
            "name": "search_memories",
            "description": "Template for searching memories",
            "arguments": [
                {
                    "name": "query",
                    "description": "Search query",
                    "required": True
                }
            ]
        }
    ]
    return {"prompts": prompts}


async def handle_get_prompt(params: Any, session: SessionState) -> Dict[str, Any]:
    """Get a specific prompt."""
    if not isinstance(params, dict) or "name" not in params:
        raise ValueError("Invalid params for prompt get")

    name = params["name"]
    arguments = params.get("arguments", {})

    if name == "search_memories":
        return {
            "description": "Search for relevant memories",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Search for memories related to: {arguments.get('query', 'your topic')}"
                    }
                }
            ]
        }

    raise ValueError(f"Prompt not found: {name}")


async def handle_memory_method(method: str, params: Any, session: SessionState) -> Any:
    """Handle custom memory methods."""
    # Extract method name
    memory_method = method.replace("memory/", "")

    if memory_method == "stats":
        total = len(memory_storage)
        tenant_count = len(set(m["tenant_id"] for m in memory_storage.values()))
        return {
            "total_memories": total,
            "tenant_count": tenant_count,
            "session_id": session.session_id
        }

    raise ValueError(f"Unknown memory method: {memory_method}")


def extract_wiki_links(text: str) -> List[str]:
    """Extract wiki-links from text."""
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, text)
    return list(set(matches))


@router.post("/batch/{session_id}")
async def handle_batch_request(
    session_id: str,
    requests: List[JSONRPCRequest]
) -> List[JSONRPCResponse]:
    """
    Handle batch JSON-RPC requests.
    Processes multiple requests and returns multiple responses.
    """

    if session_id not in sessions:
        return [
            create_error_response(
                JSONRPCErrorCode.SESSION_NOT_FOUND,
                "Session not found",
                {"session_id": session_id},
                req.id
            )
            for req in requests
        ]

    session = sessions[session_id]
    responses = []

    for request in requests:
        try:
            result = await route_method(request.method, request.params, session)
            response = create_success_response(result, request.id)
            responses.append(response)

            # Send via SSE if has ID
            if request.id is not None:
                await message_queues[session_id].put(response.dict())

        except Exception as e:
            response = create_error_response(
                JSONRPCErrorCode.INTERNAL_ERROR,
                str(e),
                None,
                request.id
            )
            responses.append(response)

    return responses


@router.get("/sessions")
async def list_sessions() -> Dict[str, Any]:
    """List active sessions (admin endpoint)."""
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "initialized": s.initialized,
                "created_at": s.created_at.isoformat(),
                "last_activity": s.last_activity.isoformat()
            }
            for s in sessions.values()
        ],
        "total": len(sessions)
    }


@router.delete("/sessions/{session_id}")
async def close_session(session_id: str) -> Dict[str, Any]:
    """Close a specific session."""
    if session_id in sessions:
        del sessions[session_id]
        if session_id in message_queues:
            del message_queues[session_id]
        return {"status": "closed", "session_id": session_id}

    return {"status": "not_found", "session_id": session_id}
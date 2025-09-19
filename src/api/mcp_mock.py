"""Mock MCP endpoints for testing without LlamaIndex dependencies."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import re

router = APIRouter(prefix="/mcp", tags=["mcp"])

# In-memory storage for testing
memory_storage: Dict[str, Dict] = {}


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


@router.post("/request")
async def handle_mcp_request(request: MCPRequest) -> MCPResponse:
    """Handle MCP request."""
    try:
        if request.method == "tools/list":
            # Return available tools
            from src.mcp.tools import get_mcp_tools
            result = {"tools": get_mcp_tools()}

        elif request.method == "tools/call":
            # Call a specific tool
            tool_name = request.params.get("tool")
            tool_params = request.params.get("params", {})
            result = await execute_mock_tool(tool_name, tool_params)

        else:
            raise ValueError(f"Unknown method: {request.method}")

        return MCPResponse(result=result, id=request.id)

    except Exception as e:
        return MCPResponse(
            result=None,
            error={"code": -32603, "message": str(e)},
            id=request.id
        )


async def execute_mock_tool(tool_name: str, params: Dict[str, Any]) -> Any:
    """Execute a mock tool."""

    if tool_name == "memory_create":
        # Create a new memory
        memory_id = str(uuid.uuid4())
        memory = {
            "id": memory_id,
            "content": params["content"],
            "tenant_id": params["tenant_id"],
            "user_id": params["user_id"],
            "metadata": params.get("metadata", {}),
            "source": params.get("source"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            # Extract wiki-links for later use
            "wiki_links": extract_wiki_links(params["content"])
        }
        memory_storage[memory_id] = memory

        return {
            "memory": {
                "id": memory_id,
                "content": memory["content"],
                "tenant_id": memory["tenant_id"],
                "user_id": memory["user_id"],
                "created_at": memory["created_at"]
            }
        }

    elif tool_name == "memory_search":
        # Search memories
        query = params["query"].lower()
        tenant_id = params["tenant_id"]
        limit = params.get("limit", 10)

        results = []
        for mem_id, memory in memory_storage.items():
            if memory["tenant_id"] != tenant_id:
                continue

            # Simple keyword matching for mock
            content_lower = memory["content"].lower()
            if any(word in content_lower for word in query.split()):
                # Calculate a simple relevance score
                score = sum(1 for word in query.split() if word in content_lower) / len(query.split())
                results.append({
                    "id": mem_id,
                    "content": memory["content"],
                    "score": score,
                    "metadata": memory.get("metadata", {}),
                    "source": memory.get("source"),
                    "created_at": memory.get("created_at")
                })

        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"memories": results[:limit]}

    elif tool_name == "memory_update":
        # Update a memory
        memory_id = params["memory_id"]
        if memory_id not in memory_storage:
            raise ValueError(f"Memory {memory_id} not found")

        memory = memory_storage[memory_id]
        if "content" in params:
            memory["content"] = params["content"]
            memory["wiki_links"] = extract_wiki_links(params["content"])
        if "metadata" in params:
            memory["metadata"].update(params["metadata"])
        memory["updated_at"] = datetime.now().isoformat()

        return {
            "memory": {
                "id": memory_id,
                "content": memory["content"],
                "updated_at": memory["updated_at"]
            }
        }

    elif tool_name == "memory_delete":
        # Delete a memory
        memory_id = params["memory_id"]
        if memory_id in memory_storage:
            del memory_storage[memory_id]
            return {"success": True}
        return {"success": False}

    elif tool_name == "memory_list":
        # List memories
        tenant_id = params["tenant_id"]
        skip = params.get("skip", 0)
        limit = params.get("limit", 50)

        tenant_memories = [
            {
                "id": mem_id,
                "content": memory["content"][:200] + "..." if len(memory["content"]) > 200 else memory["content"],
                "created_at": memory.get("created_at")
            }
            for mem_id, memory in memory_storage.items()
            if memory["tenant_id"] == tenant_id
        ]

        # Apply pagination
        return {"memories": tenant_memories[skip:skip + limit]}

    elif tool_name == "wiki_link_extract":
        # Extract wiki-links from text
        text = params["text"]
        links = extract_wiki_links(text)
        return {"wiki_links": links}

    elif tool_name == "wiki_link_graph":
        # Generate a simple knowledge graph
        tenant_id = params["tenant_id"]
        entity = params.get("entity")
        depth = params.get("depth", 2)

        # Build a simple graph from stored memories
        graph = {"nodes": [], "edges": []}
        entities = set()

        for memory in memory_storage.values():
            if memory["tenant_id"] != tenant_id:
                continue

            for link in memory.get("wiki_links", []):
                entities.add(link)

        graph["nodes"] = [{"id": e, "label": e} for e in entities]

        # Create edges based on co-occurrence
        for memory in memory_storage.values():
            if memory["tenant_id"] != tenant_id:
                continue

            links = memory.get("wiki_links", [])
            for i, link1 in enumerate(links):
                for link2 in links[i+1:]:
                    graph["edges"].append({
                        "from": link1,
                        "to": link2,
                        "label": "related"
                    })

        return {"graph": graph}

    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def extract_wiki_links(text: str) -> List[str]:
    """Extract wiki-links from text."""
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, text)
    return list(set(matches))  # Remove duplicates


@router.get("/tools")
async def list_tools():
    """List available MCP tools."""
    # Return tool definitions directly to avoid import issues
    tools = [
        {
            "name": "memory_search",
            "description": "Search through stored memories using semantic search"
        },
        {
            "name": "memory_create",
            "description": "Create a new memory entry"
        },
        {
            "name": "memory_update",
            "description": "Update an existing memory entry"
        },
        {
            "name": "memory_delete",
            "description": "Delete a memory entry"
        },
        {
            "name": "memory_list",
            "description": "List all memories with pagination"
        },
        {
            "name": "wiki_link_extract",
            "description": "Extract wiki-links ([[entity]]) from text"
        },
        {
            "name": "wiki_link_graph",
            "description": "Generate a knowledge graph from wiki-links"
        }
    ]
    return {"tools": tools}
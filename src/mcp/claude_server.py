#!/usr/bin/env python3
"""Standalone MCP server for Claude Desktop integration."""

import sys
import json
import asyncio
import logging
from typing import Any, Dict, Optional
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import settings
from src.services.memory_service import MemoryService
from src.services.wiki_link_service import WikiLinkService
from src.core.rag_engine import RAGEngine
from src.core.vector_store import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeMCPServer:
    """MCP server for Claude Desktop."""

    def __init__(self):
        """Initialize Claude MCP server."""
        # Initialize services
        self.vector_store = VectorStoreManager()
        self.rag_engine = RAGEngine(self.vector_store)
        self.memory_service = MemoryService(self.rag_engine)
        self.wiki_link_service = WikiLinkService()

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP request from Claude Desktop."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "0.1.0",
                        "serverInfo": {
                            "name": "memory-agent",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": True
                        }
                    },
                    "id": request_id
                }

            elif method == "tools/list":
                from src.mcp.tools import get_mcp_tools
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": get_mcp_tools()
                    },
                    "id": request_id
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                result = await self.execute_tool(tool_name, tool_params)
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                }

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_id
            }

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
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
                        "score": getattr(m, 'score', None),
                        "metadata": m.metadata,
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
                    "updated_at": memory.updated_at.isoformat() if hasattr(memory, 'updated_at') else None
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
            raise ValueError(f"Unknown tool: {tool_name}")

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Claude MCP Server...")

        while True:
            try:
                # Read request from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                # Parse JSON-RPC request
                request = json.loads(line)

                # Process request
                response = await self.process_request(request)

                # Write response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except Exception as e:
                logger.error(f"Server error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()


def main():
    """Main entry point."""
    server = ClaudeMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
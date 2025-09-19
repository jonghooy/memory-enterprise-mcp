#!/usr/bin/env python3
"""
MCP Server with stdio transport for Memory Enterprise.
This implements the standard MCP protocol using stdio for Claude Desktop integration.
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, Optional
import uuid

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='/tmp/mcp_server.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage for testing
memory_storage: Dict[str, Dict] = {}


class MCPStdioServer:
    """MCP Server using stdio transport."""

    def __init__(self):
        self.initialized = False
        self.session_id = str(uuid.uuid4())

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        logger.debug(f"Handling request: {method}")

        try:
            if method == "initialize":
                result = await self.initialize(params)
            elif method == "tools/list":
                result = await self.list_tools()
            elif method == "tools/call":
                result = await self.call_tool(params)
            elif method == "ping":
                result = {}
            elif method.startswith("notifications/"):
                # Notifications don't require a response
                return None
            else:
                raise ValueError(f"Unknown method: {method}")

            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_id
            }

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP session."""
        self.initialized = True
        logger.info(f"Session initialized: {self.session_id}")

        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "prompts": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "memory-enterprise",
                "version": "1.0.0"
            }
        }

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        tools = [
            {
                "name": "memory_search",
                "description": "Search through stored memories using semantic search",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results",
                            "default": 10
                        }
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
                        "content": {
                            "type": "string",
                            "description": "Content to store"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        }
                    },
                    "required": ["content", "tenant_id", "user_id"]
                }
            },
            {
                "name": "memory_list",
                "description": "List all memories",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results",
                            "default": 50
                        }
                    },
                    "required": ["tenant_id"]
                }
            }
        ]

        return {"tools": tools}

    async def call_tool(self, params: Dict[str, Any]) -> Any:
        """Execute a tool."""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        logger.debug(f"Calling tool: {tool_name} with args: {tool_args}")

        if tool_name == "memory_create":
            memory_id = str(uuid.uuid4())
            memory = {
                "id": memory_id,
                "content": tool_args["content"],
                "tenant_id": tool_args["tenant_id"],
                "user_id": tool_args["user_id"],
                "metadata": tool_args.get("metadata", {})
            }
            memory_storage[memory_id] = memory

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Created memory with ID: {memory_id}"
                    }
                ]
            }

        elif tool_name == "memory_search":
            query = tool_args["query"].lower()
            tenant_id = tool_args["tenant_id"]
            limit = tool_args.get("limit", 10)

            results = []
            for mem_id, memory in memory_storage.items():
                if memory["tenant_id"] != tenant_id:
                    continue

                if query in memory["content"].lower():
                    results.append({
                        "id": mem_id,
                        "content": memory["content"],
                        "metadata": memory.get("metadata", {})
                    })

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"memories": results[:limit]}, indent=2)
                    }
                ]
            }

        elif tool_name == "memory_list":
            tenant_id = tool_args["tenant_id"]
            limit = tool_args.get("limit", 50)

            tenant_memories = [
                {
                    "id": mem_id,
                    "content": memory["content"][:100] + "..." if len(memory["content"]) > 100 else memory["content"]
                }
                for mem_id, memory in memory_storage.items()
                if memory["tenant_id"] == tenant_id
            ]

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"memories": tenant_memories[:limit]}, indent=2)
                    }
                ]
            }

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def run(self):
        """Run the stdio server."""
        logger.info("Starting MCP stdio server...")

        while True:
            try:
                # Read from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                # Parse JSON-RPC request
                request = json.loads(line.strip())
                logger.debug(f"Received request: {request}")

                # Handle request
                response = await self.handle_request(request)

                # Write response to stdout (skip if None for notifications)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    },
                    "id": None
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

            except KeyboardInterrupt:
                logger.info("Server interrupted")
                break

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                continue

        logger.info("MCP stdio server stopped")


async def main():
    """Main entry point."""
    server = MCPStdioServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
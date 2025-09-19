"""MCP tool definitions and utilities."""

from typing import Dict, Any, List
import json


def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get MCP tool definitions for Claude/Cursor."""
    return [
        {
            "name": "memory_search",
            "description": "Search through stored memories using semantic search",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                        "default": 10
                    },
                    "tenant_id": {
                        "type": "string",
                        "description": "Tenant ID for multi-tenancy"
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
                        "description": "The content to store as a memory"
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
                        "description": "Source information for the memory",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["manual", "google_docs", "notion", "api", "web"]
                            },
                            "url": {
                                "type": "string",
                                "description": "URL of the source"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title of the source document"
                            }
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata for the memory"
                    }
                },
                "required": ["content", "tenant_id", "user_id"]
            }
        },
        {
            "name": "memory_update",
            "description": "Update an existing memory entry",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "ID of the memory to update"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content for the memory"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Updated metadata"
                    }
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
                    "memory_id": {
                        "type": "string",
                        "description": "ID of the memory to delete"
                    }
                },
                "required": ["memory_id"]
            }
        },
        {
            "name": "memory_list",
            "description": "List all memories with pagination",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tenant_id": {
                        "type": "string",
                        "description": "Tenant ID for multi-tenancy"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID (optional)"
                    },
                    "skip": {
                        "type": "number",
                        "description": "Number of items to skip",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of items to return",
                        "default": 50
                    }
                },
                "required": ["tenant_id"]
            }
        },
        {
            "name": "wiki_link_extract",
            "description": "Extract wiki-links ([[entity]]) from text",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract wiki-links from"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "wiki_link_graph",
            "description": "Generate a knowledge graph from wiki-links",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tenant_id": {
                        "type": "string",
                        "description": "Tenant ID for multi-tenancy"
                    },
                    "entity": {
                        "type": "string",
                        "description": "Central entity for the graph (optional)"
                    },
                    "depth": {
                        "type": "number",
                        "description": "How many levels deep to traverse the graph",
                        "default": 2
                    }
                },
                "required": ["tenant_id"]
            }
        }
    ]


def format_for_claude_desktop() -> Dict[str, Any]:
    """Format MCP tools for Claude Desktop configuration."""
    return {
        "mcpServers": {
            "memory-agent": {
                "command": "python",
                "args": ["-m", "src.mcp.claude_server"],
                "env": {
                    "PYTHONPATH": ".",
                    "MCP_MODE": "claude_desktop"
                }
            }
        }
    }


def format_for_cursor() -> Dict[str, Any]:
    """Format MCP tools for Cursor configuration."""
    return {
        "memory_agent": {
            "endpoint": "http://localhost:8080/mcp",
            "tools": get_mcp_tools()
        }
    }


def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI specification for MCP tools."""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Memory Agent MCP API",
            "version": "1.0.0",
            "description": "MCP tools for memory management and knowledge graph operations"
        },
        "servers": [
            {
                "url": "http://localhost:8005",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/mcp/request": {
                "post": {
                    "summary": "Execute MCP tool",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "method": {"type": "string"},
                                        "params": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Tool execution result"
                        }
                    }
                }
            },
            "/mcp/tools": {
                "get": {
                    "summary": "List available MCP tools",
                    "responses": {
                        "200": {
                            "description": "List of available tools",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tools": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


if __name__ == "__main__":
    # Export tool definitions for documentation
    import json

    tools = get_mcp_tools()
    with open("mcp_tools.json", "w") as f:
        json.dump(tools, f, indent=2)

    print(f"Exported {len(tools)} MCP tools to mcp_tools.json")
# Cursor Integration Guide for Memory Agent MCP

This guide explains how to integrate the Memory Agent MCP server with Cursor for enhanced AI-assisted development with persistent memory management.

## Prerequisites

1. Cursor installed (latest version)
2. Memory Agent server running (`docker-compose up`)
3. Python 3.11+ environment with Poetry

## Installation Steps

### 1. Start the MCP Server

First, ensure all services are running:

```bash
# Start Docker services
docker-compose up -d

# Install dependencies
poetry install

# Start the FastAPI server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8005
```

### 2. Configure Cursor

Add the following to your Cursor settings (`.cursor/settings.json`):

```json
{
  "mcp": {
    "servers": {
      "memory-agent": {
        "endpoint": "http://localhost:8005/mcp",
        "description": "Memory Agent for persistent knowledge management",
        "enabled": true
      }
    }
  }
}
```

### 3. Available MCP Tools

Once configured, you can use these tools in Cursor:

#### memory_search
Search through stored memories using semantic search.

Example:
```
@memory-agent Search for information about authentication implementation
```

#### memory_create
Create a new memory entry.

Example:
```
@memory-agent Remember that we use JWT tokens with 24-hour expiration for auth
```

#### memory_update
Update an existing memory.

Example:
```
@memory-agent Update the memory about JWT tokens to include refresh token rotation
```

#### memory_delete
Delete a memory entry.

Example:
```
@memory-agent Delete the outdated memory about session-based auth
```

#### memory_list
List all memories with pagination.

Example:
```
@memory-agent Show me all memories related to the current project
```

#### wiki_link_extract
Extract wiki-links ([[entity]]) from text.

Example:
```
@memory-agent Extract entities from "The [[authentication]] system uses [[JWT]] tokens"
```

#### wiki_link_graph
Generate a knowledge graph from wiki-links.

Example:
```
@memory-agent Show me the knowledge graph around [[authentication]]
```

## Usage Examples

### 1. Project Knowledge Management

```
# Store project decisions
@memory-agent Remember that we decided to use PostgreSQL for the main database and Redis for caching

# Search for past decisions
@memory-agent What database technology did we choose?

# Create connections between concepts
@memory-agent The [[authentication]] system depends on [[PostgreSQL]] for user storage and [[Redis]] for session caching
```

### 2. Code Documentation

```
# Document complex implementations
@memory-agent Remember the rate limiting implementation uses a sliding window algorithm with Redis

# Search implementation details
@memory-agent How does our rate limiting work?
```

### 3. Team Knowledge Sharing

```
# Share team decisions
@memory-agent Team decided to use feature branches with PR reviews for all changes

# Query team practices
@memory-agent What's our git workflow?
```

## Multi-Tenancy

The Memory Agent supports multi-tenancy. Configure different tenants for different projects:

```json
{
  "mcp": {
    "servers": {
      "memory-agent-project1": {
        "endpoint": "http://localhost:8005/mcp",
        "defaultParams": {
          "tenant_id": "project1",
          "user_id": "developer1"
        }
      },
      "memory-agent-project2": {
        "endpoint": "http://localhost:8005/mcp",
        "defaultParams": {
          "tenant_id": "project2",
          "user_id": "developer1"
        }
      }
    }
  }
}
```

## Troubleshooting

### Connection Issues

1. Verify the server is running:
```bash
curl http://localhost:8005/health
```

2. Check MCP tools availability:
```bash
curl http://localhost:8005/mcp/tools
```

### Memory Indexing Issues

1. Check vector store status:
```bash
docker-compose logs qdrant
```

2. Verify embeddings are being created:
```bash
curl -X POST http://localhost:8005/mcp/request \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## Advanced Configuration

### Custom Embedding Models

Modify `.env` to use different embedding models:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

### Production Deployment

For production, use Pinecone instead of Qdrant:

```env
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=memory-agent-prod
```

## API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review the documentation in `/docs`
3. Submit issues to the project repository
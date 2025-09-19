# Claude Desktop Integration Guide for Memory Agent MCP

This guide explains how to integrate the Memory Agent MCP server with Claude Desktop for enhanced AI interactions with persistent memory management.

## Prerequisites

1. Claude Desktop installed (latest version)
2. Python 3.11+ with Poetry installed
3. Docker and Docker Compose installed
4. Memory Agent repository cloned

## Installation Steps

### 1. Setup the Environment

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd rag-mcp

# Install dependencies
poetry install

# Start Docker services
docker-compose up -d
```

### 2. Configure Claude Desktop

#### Option A: Automatic Configuration (Recommended)

1. Copy the provided configuration to Claude Desktop config directory:

**macOS:**
```bash
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```powershell
copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
cp claude_desktop_config.json ~/.config/claude/claude_desktop_config.json
```

2. Restart Claude Desktop

#### Option B: Manual Configuration

1. Open Claude Desktop settings
2. Navigate to "Developer" → "MCP Servers"
3. Add a new server with these details:

```json
{
  "name": "memory-agent",
  "command": "python",
  "args": ["-m", "src.mcp.claude_server"],
  "cwd": "/path/to/rag-mcp",
  "env": {
    "PYTHONPATH": "/path/to/rag-mcp",
    "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/memory_agent",
    "REDIS_URL": "redis://localhost:6380/0",
    "QDRANT_HOST": "localhost",
    "QDRANT_PORT": "6333"
  }
}
```

### 3. Verify Installation

1. Restart Claude Desktop
2. Open a new conversation
3. Type: `@memory-agent` - you should see available tools
4. Test with: `@memory-agent list available tools`

## Available Tools

### memory_search
Search through your stored memories using semantic search.

**Example Usage:**
```
@memory-agent search for "authentication implementation details"
```

### memory_create
Create a new memory to remember important information.

**Example Usage:**
```
@memory-agent create memory: "The project uses JWT tokens with RS256 algorithm for authentication, tokens expire after 24 hours"
```

### memory_update
Update an existing memory with new information.

**Example Usage:**
```
@memory-agent update memory [memory_id] with: "Added refresh token rotation every 7 days"
```

### memory_delete
Delete a memory that's no longer relevant.

**Example Usage:**
```
@memory-agent delete memory [memory_id]
```

### memory_list
List all your stored memories with pagination.

**Example Usage:**
```
@memory-agent list all memories (limit: 20)
```

### wiki_link_extract
Extract wiki-style links from text to build knowledge connections.

**Example Usage:**
```
@memory-agent extract links from: "The [[authentication]] module uses [[JWT]] and connects to [[PostgreSQL]]"
```

### wiki_link_graph
Generate a knowledge graph showing connections between concepts.

**Example Usage:**
```
@memory-agent show knowledge graph for "authentication" (depth: 2)
```

## Use Cases

### 1. Project Documentation Memory

```
You: @memory-agent create memory: "Project architecture:
- Frontend: React with TypeScript
- Backend: FastAPI with Python 3.11
- Database: PostgreSQL with SQLAlchemy
- Cache: Redis
- Vector Store: Qdrant
- Authentication: JWT with refresh tokens"

Claude: I've stored this architecture information in memory.

[Later in another conversation...]
You: @memory-agent search for "project architecture"

Claude: Here's what I found about your project architecture...
```

### 2. Code Patterns and Decisions

```
You: @memory-agent create memory: "Database connection pattern:
We use SQLAlchemy with async sessions. Connection pooling is configured with:
- pool_size=20
- max_overflow=10
- pool_pre_ping=True
Always use dependency injection for database sessions."

[When working on database code...]
You: @memory-agent search for "database connection pattern"
```

### 3. Knowledge Graph Building

```
You: @memory-agent create memory: "The [[authentication]] system uses [[JWT]] tokens stored in [[Redis]] cache. User data is persisted in [[PostgreSQL]]."

You: @memory-agent show knowledge graph for "authentication"

Claude: Here's the knowledge graph:
authentication → JWT
authentication → Redis
authentication → PostgreSQL
JWT → Redis (token storage)
```

## Multi-Tenancy Configuration

To use different memory spaces for different projects:

```json
{
  "mcpServers": {
    "memory-agent-work": {
      "command": "python",
      "args": ["-m", "src.mcp.claude_server"],
      "cwd": "/path/to/rag-mcp",
      "env": {
        "DEFAULT_TENANT_ID": "work-projects",
        "DEFAULT_USER_ID": "john-doe"
      }
    },
    "memory-agent-personal": {
      "command": "python",
      "args": ["-m", "src.mcp.claude_server"],
      "cwd": "/path/to/rag-mcp",
      "env": {
        "DEFAULT_TENANT_ID": "personal-projects",
        "DEFAULT_USER_ID": "john-doe"
      }
    }
  }
}
```

## Troubleshooting

### MCP Server Not Connecting

1. Check if Python environment is activated:
```bash
poetry shell
python -m src.mcp.claude_server
```

2. Verify services are running:
```bash
docker-compose ps
```

3. Check logs:
```bash
# Check Claude Desktop logs
# macOS: ~/Library/Logs/Claude/
# Windows: %APPDATA%\Claude\logs\
# Linux: ~/.config/claude/logs/
```

### Memory Search Not Working

1. Verify Qdrant is running:
```bash
curl http://localhost:6333/health
```

2. Check if embeddings are being created:
```bash
docker-compose logs qdrant
```

### Performance Issues

1. Adjust embedding batch size in `.env`:
```env
EMBEDDING_BATCH_SIZE=16
```

2. Use a smaller embedding model:
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

## Advanced Features

### Custom Commands

You can create aliases for common operations in Claude Desktop settings:

```json
{
  "aliases": {
    "remember": "memory-agent create memory:",
    "recall": "memory-agent search for:",
    "forget": "memory-agent delete memory"
  }
}
```

Usage:
```
@remember The deployment process uses GitHub Actions with staging and production environments
@recall deployment process
@forget [memory_id]
```

### Scheduled Memory Cleanup

Configure automatic cleanup of old memories:

```python
# In src/mcp/claude_server.py, add:
async def cleanup_old_memories(days=90):
    """Remove memories older than specified days."""
    # Implementation
```

## Best Practices

1. **Structured Memories**: Use consistent formatting for better retrieval
2. **Wiki-Links**: Use [[concept]] notation to build knowledge graphs
3. **Metadata**: Include project names, dates, and categories
4. **Regular Reviews**: Periodically review and update memories
5. **Tenant Separation**: Use different tenants for different projects

## Security Considerations

1. **Local Only**: Default configuration runs locally only
2. **Authentication**: Add authentication for production use
3. **Encryption**: Enable encryption for sensitive memories
4. **Access Control**: Implement role-based access control
5. **Audit Logs**: Enable logging for compliance

## Support and Resources

- API Documentation: http://localhost:8080/docs
- Project Repository: [GitHub Link]
- Issue Tracker: [GitHub Issues]
- Discord Community: [Discord Invite]

## Next Steps

1. Explore integration with Google Docs and Notion
2. Set up automated memory extraction from documents
3. Configure team-wide memory sharing
4. Implement memory versioning and history
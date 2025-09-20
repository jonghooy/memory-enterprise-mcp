# Pinecone MCP Server Setup Guide

## 🎯 Overview
Pinecone MCP (Model Context Protocol) server has been installed and configured for your RAG-MCP project. This enables AI assistants like Claude Desktop and Cursor IDE to interact with Pinecone vector databases directly.

## ✅ Installation Status
- **Package**: `@pinecone-database/mcp` - Installed ✅
- **Claude Desktop Config**: Updated ✅
- **Cursor IDE Config**: Created ✅
- **API Key**: Needs configuration ⚠️

## 📁 Configuration Files

### 1. Claude Desktop Configuration
**File**: `claude_desktop_config.json`
```json
{
  "mcpServers": {
    "pinecone": {
      "command": "npx",
      "args": ["-y", "@pinecone-database/mcp"],
      "env": {
        "PINECONE_API_KEY": "YOUR_PINECONE_API_KEY_HERE"
      }
    }
  }
}
```

### 2. Cursor IDE Configuration
**File**: `.cursor/mcp.json`
- Same structure as Claude Desktop config
- Located in project root

### 3. Environment Variables
**File**: `.env`
```env
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=memory-agent-index
```

## 🔑 Getting Your Pinecone API Key

1. **Sign up/Login**: Visit [Pinecone Console](https://app.pinecone.io)
2. **Create Project**: If you don't have one already
3. **Get API Key**:
   - Go to API Keys section
   - Create a new API key
   - Copy the key value
4. **Update Configuration**:
   - Replace `YOUR_PINECONE_API_KEY_HERE` in config files
   - Update `.env` file with your actual key

## 🚀 Features Available

### Through MCP Server
The Pinecone MCP server provides these capabilities:

1. **Documentation Search**
   - Search Pinecone documentation
   - Get accurate answers about Pinecone features
   - Learn about best practices

2. **Index Management**
   - Create and configure indexes
   - View index statistics
   - Manage index settings

3. **Vector Operations**
   - Upsert vectors to indexes
   - Query and search vectors
   - Update and delete vectors

4. **Code Generation**
   - Generate code based on your index config
   - Create embedding pipelines
   - Build search implementations

## 💻 Usage Examples

### In Claude Desktop
After configuring and restarting Claude Desktop:
```
"Search Pinecone docs for hybrid search"
"Help me create a Pinecone index for my RAG system"
"Show me how to upsert embeddings to Pinecone"
```

### In Your Code
```python
from pinecone import Pinecone

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create or connect to index
index = pc.Index("memory-agent-index")

# Upsert vectors
index.upsert(vectors=[
    {"id": "vec1", "values": [0.1, 0.2, 0.3...], "metadata": {"text": "..."}}
])

# Query vectors
results = index.query(vector=[0.1, 0.2, 0.3...], top_k=5)
```

## 🔄 Integration with RAG-MCP

### Current Setup
1. **Frontend**: Knowledge Management UI at `/kms/knowledge`
2. **Backend**: API endpoints for knowledge CRUD
3. **Vector Store**: Can switch between Pinecone/Qdrant/ChromaDB

### Switching to Pinecone
Update `.env`:
```env
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=your-index
```

## 📝 Testing

Run the test script:
```bash
node test_pinecone_mcp.js
```

## 🛠️ Troubleshooting

### MCP Server Not Loading
1. Ensure Node.js and npx are in PATH
2. Check API key is correctly set
3. Restart Claude Desktop/Cursor after config changes

### Connection Issues
1. Verify API key is valid
2. Check network connectivity to Pinecone
3. Ensure index exists if querying

### Package Issues
```bash
# Reinstall package
npm uninstall @pinecone-database/mcp
npm install @pinecone-database/mcp

# Clear npm cache if needed
npm cache clean --force
```

## 📚 Resources
- [Pinecone Documentation](https://docs.pinecone.io)
- [MCP Protocol Spec](https://modelcontextprotocol.org)
- [Pinecone MCP Guide](https://docs.pinecone.io/guides/operations/mcp-server)
- [Pinecone Console](https://app.pinecone.io)

## ✨ Next Steps
1. Get your Pinecone API key
2. Update configuration files with your key
3. Create a Pinecone index for your data
4. Test the integration with sample data
5. Connect your Knowledge UI to use Pinecone as the vector store
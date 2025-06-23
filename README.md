# Python Alfresco MCP Server **🚧 (Preview)**

**Python based Model Context Protocol server for Alfresco Content Services**

Provides AI-native access to Alfresco content management operations through the [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk).

## 🚀 Features

### Comprehensive Content Management Tools
- **Search API**: Advanced text search with AFTS query language
- **Document Lifecycle**: Upload, download, checkin, checkout, cancel checkout
- **Version Management**: Create major/minor versions with comments
- **Folder Operations**: Create and delete folders with metadata
- **Property Management**: Get and set document/folder properties and names
- **Node Operations**: Delete documents and folders (trash or permanent)

### Enterprise-Ready Architecture
- **Multiple Transports**: stdio (direct MCP) and FastAPI (HTTP/testing)
- **Type Safety**: Full Pydantic v2 models and async support
- **Configuration**: Environment variables and config file support
- **Logging**: Comprehensive logging with configurable levels
- **Error Handling**: Graceful error handling with detailed messages

### AI Integration
- **MCP Tools**: 9 comprehensive tools for content operations
- **MCP Resources**: Repository metadata and status
- **MCP Prompts**: AI-friendly templates for common workflows

## 📋 Requirements

- Python 3.8+
- Alfresco Content Services (Community or Enterprise)
- python-alfresco-api >= 1.0.0

## 🛠️ Installation

### 1. Install Dependencies

```bash
# Install MCP server
pip install -e .

# Or with development dependencies
pip install -e .[dev]
```

### 2. Configure Alfresco Connection

**Environment Variables** (recommended):
```bash
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
export ALFRESCO_VERIFY_SSL="false"
```

**Or Config File** (`config.yaml`):
```yaml
alfresco_url: "http://localhost:8080"
username: "admin"
password: "admin"
verify_ssl: false
```

## 🚀 Usage

### stdio Transport (MCP Client)

```bash
# Run MCP server with stdio transport
alfresco-mcp-server --transport stdio

# Or directly
python -m alfresco_mcp_server.main --transport stdio
```

### FastAPI Transport (HTTP/Testing)

```bash
# Run HTTP server for testing
alfresco-mcp-server --transport fastapi

# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### MCP Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "alfresco_mcp_server.main", "--transport", "stdio"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Search for documents
            result = await session.call_tool(
                "search_content", 
                arguments={"query": "important document", "max_results": 10}
            )
            print(result)
```

## 🛠️ Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_content` | Search documents and folders | `query` (str), `max_results` (int) |
| `download_document` | Download document content | `node_id` (str) |
| `upload_document` | Upload new document | `filename` (str), `content_base64` (str), `parent_id` (str), `description` (str) |
| `checkout_document` | Check out for editing | `node_id` (str) |
| `checkin_document` | Check in after editing | `node_id` (str), `comment` (str), `major_version` (bool) |
| `create_folder` | Create new folder | `folder_name` (str), `parent_id` (str), `description` (str) |
| `delete_node` | Delete document/folder | `node_id` (str), `permanent` (bool) |
| `get_node_properties` | Get node metadata | `node_id` (str) |
| `update_node_properties` | Update node metadata | `node_id` (str), `properties` (dict), `name` (str) |

## 🔧 Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ALFRESCO_URL` | `http://localhost:8080` | Alfresco server URL |
| `ALFRESCO_USERNAME` | `admin` | Username for authentication |
| `ALFRESCO_PASSWORD` | `admin` | Password for authentication |
| `ALFRESCO_VERIFY_SSL` | `false` | Verify SSL certificates |
| `ALFRESCO_TIMEOUT` | `30` | Request timeout (seconds) |
| `FASTAPI_HOST` | `localhost` | FastAPI host |
| `FASTAPI_PORT` | `8000` | FastAPI port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `100000000` | Max upload size (bytes) |



## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│           MCP Client                │
│    (Claude, Custom App, etc.)       │
└─────────────┬───────────────────────┘
              │ stdio/HTTP
┌─────────────▼───────────────────────┐
│        Alfresco MCP Server          │
│  ┌─────────────┬─────────────────┐  │
│  │ MCP Tools   │ MCP Resources   │  │
│  │ MCP Prompts │ FastAPI API     │  │
│  └─────────────┴─────────────────┘  │
└─────────────┬───────────────────────┘
              │ python-alfresco-api
┌─────────────▼───────────────────────┐
│      Alfresco Content Services      │
│   (Community/Enterprise Edition)    │
└─────────────────────────────────────┘
```

## 🧪 Development

### Setup Development Environment

```bash
git clone <repository>
cd python-alfresco-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -e .[dev]

# Install python-alfresco-api (local development)
pip install -e ../python-alfresco-api
```

### Run Tests

```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=alfresco_mcp_server

# Run specific test
pytest tests/test_server.py -v
```

### Code Quality

```bash
# Format code
black alfresco_mcp_server/

# Type checking
mypy alfresco_mcp_server/

# Linting
ruff check alfresco_mcp_server/
```

## 📚 Examples

See the `examples/` directory for:
- `basic_client.py` - Basic MCP client usage
- `fastapi_client.py` - HTTP API testing
- `document_workflow.py` - Complete document lifecycle
- `search_examples.py` - Advanced search patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Alfresco 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[python-alfresco-api](https://github.com/your-org/python-alfresco-api)** - The MCP server uses this
- **[Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)** - Official MCP Python SDK
- **[Angel's Alfresco MCP PoC](https://github.com/aborroy/alfresco-mcp-poc)** - Java MCP client, TypeScript MCP server for Alfresco
- **[Box MCP Server](https://github.com/box-community/mcp-server-box)** - Box Python based MCP server

## 🙋‍♂️ Support

- 📚 **Documentation**: TBD
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-org/python-alfresco-mcp-server/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/python-alfresco-mcp-server/discussions)

---

**Built using [python-alfresco-api](https://github.com/your-org/python-alfresco-api) and the [Model Context Protoco Python SDK](https://github.com/modelcontextprotocol/python-sdk)**

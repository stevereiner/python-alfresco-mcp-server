# Quick Start Guide

Get up and running with the Alfresco MCP Server in 5 minutes! This guide walks you through installation, configuration, and your first successful connection.

## ⏱️ 5-Minute Setup

### Step 1: Prerequisites (30 seconds)

Ensure you have:
- ✅ Python 3.10+ installed
- ✅ Access to an Alfresco server (local or remote)
- ✅ Administrator credentials for Alfresco

```bash
# Check Python version
python --version  # Should be 3.10 or higher
```

### Step 2: Installation (1 minute)

**Option A: UV (Recommended - Automatic dependency management)**

```bash
# Install UV if you don't have it
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
# curl -LsSf https://astral.sh/uv/install.sh | sh          # macOS/Linux

# Clone the repository
git clone https://github.com/your-org/python-alfresco-mcp-server.git
cd python-alfresco-mcp-server

# That's it! UV will handle venv and dependencies automatically
# Test with:
uv run python-alfresco-mcp-server --help
```

**Option B: Traditional pip (Manual venv management)**

```bash
# Clone the repository
git clone https://github.com/your-org/python-alfresco-mcp-server.git
cd python-alfresco-mcp-server

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows

# Install the package
pip install -e .

# Verify installation
python -m alfresco_mcp_server.fastmcp_server --help
```

### Step 3: Configuration (1 minute)

Set up your Alfresco connection:

```bash
# Option 1: Environment variables (recommended)
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"

# Option 2: Create config.yaml (alternative)
cp alfresco_mcp_server/config.yaml.example config.yaml
# Edit config.yaml with your settings
```

### Step 4: Test Connection (30 seconds)

```bash
# With UV (recommended)
uv run python examples/quick_start.py

# With traditional pip
python examples/quick_start.py
```

Expected output:
```
🚀 Alfresco MCP Server - Quick Start Example
==================================================
✅ Connected successfully!
🛠️ Available Tools:
  1. search_content - Search for documents and folders
  2. upload_document - Upload a new document
  ...
```

### Step 5: First MCP Operation (2 minutes)

Run your first document search:

```python
# Create test_search.py
import asyncio
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp

async def first_search():
    async with Client(mcp) as client:
        # Search for documents
        result = await client.call_tool("search_content", {
            "query": "*",
            "max_results": 5
        })
        print("Search Results:")
        print(result[0].text)

# Run the search
asyncio.run(first_search())
```

## 🎉 Success!

If you see search results, congratulations! Your Alfresco MCP Server is working.

## 🚀 Next Steps

Now that you're connected, try these:

### 1. Upload Your First Document

```python
import base64
import asyncio
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp

async def upload_demo():
    async with Client(mcp) as client:
        # Create sample content
        content = "Hello from MCP Server!"
        content_b64 = base64.b64encode(content.encode()).decode()
        
        # Upload document
        result = await client.call_tool("upload_document", {
            "filename": "hello_mcp.txt",
            "content_base64": content_b64,
            "parent_id": "-root-",
            "description": "My first MCP upload"
        })
        print(result[0].text)

asyncio.run(upload_demo())
```

### 2. Create a Folder

```python
async def create_folder_demo():
    async with Client(mcp) as client:
        result = await client.call_tool("create_folder", {
            "folder_name": "My_MCP_Folder",
            "parent_id": "-root-",
            "description": "Created via MCP Server"
        })
        print(result[0].text)

asyncio.run(create_folder_demo())
```

### 3. Get Repository Information

```python
async def repo_info_demo():
    async with Client(mcp) as client:
        # Get repository info
        info = await client.read_resource("alfresco://repository/info")
        print("Repository Info:")
        print(info[0].text)

asyncio.run(repo_info_demo())
```

## 🌐 Transport Options

The server supports multiple transport protocols:

```bash
# STDIO (default)
python -m alfresco_mcp_server.fastmcp_server

# HTTP
python -m alfresco_mcp_server.fastmcp_server --transport http --port 8001

# Server-Sent Events
python -m alfresco_mcp_server.fastmcp_server --transport sse --port 8002
```

## 🔧 Common Configuration

### Custom Alfresco URL
```bash
export ALFRESCO_URL="https://my-alfresco.company.com"
```

### Authentication Token
```bash
export ALFRESCO_TOKEN="your-auth-token"
```

### Debug Mode
```bash
export ALFRESCO_DEBUG="true"
```

## ⚡ Quick Examples

### Complete Document Workflow
```python
import asyncio
import base64
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp

async def complete_workflow():
    async with Client(mcp) as client:
        # 1. Create folder
        folder_result = await client.call_tool("create_folder", {
            "folder_name": "Quick_Start_Demo",
            "parent_id": "-root-",
            "description": "Demo folder from quick start"
        })
        print("✅ Folder created")
        
        # 2. Upload document
        content = "This is a demo document created during quick start."
        content_b64 = base64.b64encode(content.encode()).decode()
        
        upload_result = await client.call_tool("upload_document", {
            "filename": "demo_document.txt",
            "content_base64": content_b64,
            "parent_id": "-root-",
            "description": "Demo document"
        })
        print("✅ Document uploaded")
        
        # 3. Search for our content
        search_result = await client.call_tool("search_content", {
            "query": "Quick_Start_Demo",
            "max_results": 10
        })
        print("✅ Search completed")
        print("Search Results:", search_result[0].text)

# Run the complete workflow
asyncio.run(complete_workflow())
```

## 🆘 Troubleshooting

### Connection Issues
```bash
# Test Alfresco connectivity
curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-
```

### Common Errors

**Error: Connection refused**
- ✅ Check if Alfresco server is running
- ✅ Verify ALFRESCO_URL is correct
- ✅ Check firewall settings

**Error: Authentication failed**
- ✅ Verify username/password
- ✅ Check user permissions in Alfresco

**Error: Module not found**
- ✅ Run `pip install -e .` again
- ✅ Check Python virtual environment

### Getting Help

- 📖 Read the [troubleshooting guide](troubleshooting.md)
- 💬 Check GitHub Issues for common questions
- 🐛 Report issues on GitHub

## 📖 What's Next?

Explore more advanced features:

- 📄 **[Document Lifecycle](../examples/document_lifecycle.py)** - Complete document management
- 🔍 **[Search Examples](../examples/search_examples.py)** - Advanced search patterns
- ⚡ **[Batch Operations](../examples/batch_operations.py)** - Bulk processing
- 🌐 **[Transport Examples](../examples/transport_examples.py)** - Different connection methods

## 🎯 Key Concepts

- **MCP Tools**: 15 tools for document management (search, upload, download, checkout/checkin workflow, etc.)
- **Transport Protocols**: STDIO, HTTP, SSE for different use cases
- **Resources**: Repository information and health status
- **Prompts**: AI-powered analysis and insights

---

**🚀 Complete!** You've successfully set up the Alfresco MCP Server. You're now ready to build document management integrations! 
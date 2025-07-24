# MCP Inspector Setup Guide

MCP Inspector is a debugging and testing tool for Model Context Protocol servers. This guide covers setup and connection for the Python Alfresco MCP Server.

## 🔍 MCP Inspector Overview

MCP Inspector provides:
- **Tool Testing**: Interactive testing of all 15 MCP tools
- **Resource Access**: View repository information and other resources
- **Protocol Debugging**: Monitor MCP protocol messages
- **Real-time Testing**: Live interaction with Alfresco server

## 🚀 Installation & Setup

### Prerequisites

1. **Node.js**: Required for running MCP Inspector
2. **Running MCP Server**: Your Python Alfresco MCP Server must be running
3. **Alfresco Server**: Live Alfresco instance for testing

### Method 1: Using Config File (Recommended)

This method uses the included configuration files and avoids proxy connection errors.

#### Step 1: Start MCP Server with HTTP Transport

**With UV (Recommended):**
```bash
uv run python-alfresco-mcp-server --transport http --port 8003
```

**Traditional Python:**
```bash
python -m alfresco_mcp_server.fastmcp_server --transport http --port 8003
```

#### Step 2: Start MCP Inspector

Use the included configuration file:
```bash
npx @modelcontextprotocol/inspector --config mcp-inspector-http-config.json --server python-alfresco-mcp-server
```

#### Step 3: Open Browser

MCP Inspector will provide a URL with pre-filled authentication token:
```
🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=d7a62ab6e032eefe5d85e807c50e13b9fffcd12badbf8bbc3377659c0be4fa8d
```

### Method 2: Manual Connection

#### Step 1: Start MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```

#### Step 2: Connect to Server
1. Open browser to `http://localhost:6274`
2. Click **"Add Server"** or use server connection field
3. Enter server URL: `http://localhost:8003`
4. Select transport: **HTTP**
5. Click **Connect**

## 📋 Configuration Files

The project includes pre-configured files for easy setup:

### HTTP Transport Configuration
**File**: `mcp-inspector-http-config.json`
```json
{
  "servers": {
    "python-alfresco-mcp-server": {
      "command": "uv",
      "args": ["run", "python-alfresco-mcp-server", "--transport", "http", "--port", "8003"],
      "env": {
        "ALFRESCO_URL": "http://localhost:8080",
        "ALFRESCO_USERNAME": "admin",
        "ALFRESCO_PASSWORD": "admin"
      }
    }
  }
}
```

### STDIO Transport Configuration  
**File**: `mcp-inspector-stdio-config.json`
```json
{
  "servers": {
    "python-alfresco-mcp-server": {
      "command": "uv",
      "args": ["run", "python-alfresco-mcp-server"],
      "env": {
        "ALFRESCO_URL": "http://localhost:8080",
        "ALFRESCO_USERNAME": "admin",
        "ALFRESCO_PASSWORD": "admin"
      }
    }
  }
}
```

## 🧪 Testing Tools and Features

### Available Tools (15 Total)

Once connected, you can test all tools:

#### Search Tools (4)
- **search_content**: Full text search
- **advanced_search**: AFTS query language  
- **search_by_metadata**: Property-based queries
- **cmis_search**: CMIS SQL queries

#### Core Tools (11)
- **browse_repository**: Browse folders
- **repository_info**: Get system information
- **upload_document**: Upload files
- **download_document**: Download content
- **create_folder**: Create directories
- **get_node_properties**: View metadata
- **update_node_properties**: Modify metadata
- **delete_node**: Remove content
- **checkout_document**: Lock for editing
- **checkin_document**: Save changes
- **cancel_checkout**: Cancel editing

### Resources
- **repository_info**: Repository status and configuration

### Prompts
- **search_and_analyze**: Interactive search form

## 🔧 Usage Examples

### Basic Testing Workflow

1. **Start with Repository Info**:
   ```json
   Tool: repository_info
   Parameters: {} 
   ```

2. **Search for Content**:
   ```json
   Tool: search_content
   Parameters: {
     "query": "test",
     "max_results": 10
   }
   ```

3. **Browse Repository**:
   ```json
   Tool: browse_repository
   Parameters: {
     "node_id": "-root-"
   }
   ```

4. **Upload Test Document**:
   ```json
   Tool: upload_document
   Parameters: {
     "filename": "test.txt",
     "content_base64": "VGVzdCBjb250ZW50",
     "parent_id": "-root-",
     "description": "Test upload"
   }
   ```

### Advanced Testing

**CMIS SQL Search**:
```json
Tool: cmis_search
Parameters: {
  "cmis_query": "SELECT * FROM cmis:document WHERE cmis:name LIKE '%test%'",
  "max_results": 5
}
```

**Metadata Search**:
```json
Tool: search_by_metadata
Parameters: {
  "property_name": "cm:name",
  "property_value": "test",
  "comparison": "contains"
}
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Cannot connect to server"
- **Check**: MCP server is running on correct port
- **Verify**: `curl http://localhost:8003/health` returns response
- **Solution**: Restart MCP server with HTTP transport

#### 2. "Proxy connection failed"
- **Use**: Config file method instead of manual connection
- **Check**: No other service using port 8003
- **Alternative**: Try different port: `--port 8004`

#### 3. "Authentication failed"
- **Check**: Environment variables are set correctly
- **Verify**: Alfresco server is accessible
- **Test**: `curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-`

#### 4. "Port 6274 already in use"
- **Auto-resolution**: MCP Inspector finds next available port
- **Manual**: Check what port is actually used in startup message
- **Check**: `netstat -an | findstr :6274`

### Network Issues

**Check ports**:
```bash
# Windows
netstat -an | findstr ":6274\|:8003\|:8080"

# Linux/macOS  
netstat -an | grep ":6274\|:8003\|:8080"
```

**Test connectivity**:
```bash
# Test MCP server
curl http://localhost:8003

# Test Alfresco server
curl http://localhost:8080/alfresco
```

### Tool-Specific Issues

#### Search Returns No Results
- **Check**: Alfresco has content indexed
- **Verify**: Search service is running
- **Test**: Simple query like `*` to return all content

#### Upload Fails
- **Check**: Base64 encoding is correct
- **Verify**: Parent folder exists and is writable
- **Test**: Upload to Company Home (-root-)

#### Authentication Errors
- **Verify**: Username/password in environment variables
- **Check**: User has required permissions
- **Test**: Basic authentication with curl

## 📊 Expected Behavior

### Successful Connection
When properly connected, you should see:
- ✅ Green connection status
- 📊 List of 15 available tools
- 🔍 Repository resource available
- 🎯 Search and analyze prompt available

### Typical Response Times
- **Search operations**: < 1 second
- **Repository browsing**: < 500ms
- **Document upload**: 1-3 seconds
- **Download operations**: 1-2 seconds

## 🔗 Alternative Testing Methods

### Command Line Testing
Use the examples in [`examples/`](../examples/) for programmatic testing:
```bash
python examples/quick_start.py
python examples/document_lifecycle.py
```

### Integration Tests
Run the automated test suite:
```bash
pytest tests/ -m integration
```

### Manual Testing with Claude Desktop
See [`prompts-for-claude.md`](../prompts-for-claude.md) for 14 manual test scenarios.

## 📚 Additional Resources

- **[MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)**: Official documentation
- **[API Reference](./api_reference.md)**: Complete tool documentation
- **[Troubleshooting Guide](./troubleshooting.md)**: Problem diagnosis
- **[Configuration Guide](./configuration_guide.md)**: Advanced setup options

## 🎯 Quick Start Summary

1. **Start MCP Server**: `uv run python-alfresco-mcp-server --transport http --port 8003`
2. **Start Inspector**: `npx @modelcontextprotocol/inspector --config mcp-inspector-http-config.json --server python-alfresco-mcp-server`
3. **Open URL**: Use the provided URL with pre-filled token
4. **Test Tools**: Start with `repository_info` then explore other tools

This provides a comprehensive testing environment for validating all Alfresco MCP server functionality! 
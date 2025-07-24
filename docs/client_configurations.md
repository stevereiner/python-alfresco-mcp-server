# MCP Client Configuration Guide

This guide covers configuration for various MCP clients beyond Claude Desktop. For Claude Desktop configuration, see the [Claude Desktop Setup Guide](./claude_desktop_setup.md).

## 🔷 Cursor Configuration

Cursor is a VS Code fork with AI capabilities and MCP support.

> 📖 **Complete Setup Guide**: Detailed Cursor configuration instructions available at [playbooks.com](https://playbooks.com/mcp/stevereiner-alfresco-content-services#cursor-setup)

### For Users (PyPI Installation)

If you installed the package via PyPI with pipx:

```json
{
    "mcpServers": {
        "python-alfresco-mcp-server": {
            "command": "python-alfresco-mcp-server",
            "args": ["--transport", "stdio"],
            "env": {
                "ALFRESCO_URL": "http://localhost:8080",
                "ALFRESCO_USERNAME": "admin",
                "ALFRESCO_PASSWORD": "admin"
            }
        }
    }
}
```

### For Developers (Source Installation)

If you're using the source code with UV:

```json
{
    "mcpServers": {
        "python-alfresco-mcp-server": {
            "command": "uv",
            "args": ["run", "python-alfresco-mcp-server"],
            "cwd": "/path/to/python-alfresco-mcp-server",
            "env": {
                "ALFRESCO_URL": "http://localhost:8080",
                "ALFRESCO_USERNAME": "admin",
                "ALFRESCO_PASSWORD": "admin"
            }
        }
    }
}
```

## ⚡ Claude Code Configuration

Claude Code is Anthropic's VS Code extension with MCP support.

> 📖 **Complete Setup Guide**: Claude Code configuration instructions at [playbooks.com](https://playbooks.com/mcp/stevereiner-alfresco-content-services#claude-code-setup)

### For Users (PyPI Installation)

```bash
claude mcp add-json "python-alfresco-mcp-server" '{
  "command": "python-alfresco-mcp-server",
  "args": ["--transport", "stdio"],
  "env": {
    "ALFRESCO_URL": "http://localhost:8080",
    "ALFRESCO_USERNAME": "admin",
    "ALFRESCO_PASSWORD": "admin"
  }
}'
```

### For Developers (Source Installation)

```bash
claude mcp add-json "python-alfresco-mcp-server" '{
  "command": "uv",
  "args": ["run", "python-alfresco-mcp-server"],
  "cwd": "/path/to/python-alfresco-mcp-server",
  "env": {
    "ALFRESCO_URL": "http://localhost:8080",
    "ALFRESCO_USERNAME": "admin",
    "ALFRESCO_PASSWORD": "admin"
  }
}'
```

## 🔧 Other MCP Clients

For any MCP-compatible client, use these connection parameters based on your installation method:

### PyPI Installation (Users)

- **Command**: `python-alfresco-mcp-server` (assumes pipx installation)
- **Args**: `["--transport", "stdio"]`
- **Transport Options**: 
  - STDIO (default) - Direct MCP protocol
  - HTTP (add `--port 8001`) - RESTful API  
  - SSE (add `--port 8003`) - Server-Sent Events

### Source Installation (Developers)

- **Command**: `uv`
- **Args**: `["run", "python-alfresco-mcp-server"]`
- **Working Directory**: Path to cloned repository
- **Transport Options**: Same as above

### Traditional Python Installation

If using traditional pip in a virtual environment:

- **Command**: `/path/to/venv/bin/python-alfresco-mcp-server` (full path to executable)
- **Args**: `["--transport", "stdio"]`
- **Transport Options**: Same as above

## 🔧 Environment Variables

All clients need these environment variables configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `ALFRESCO_URL` | `http://localhost:8080` | Alfresco server URL |
| `ALFRESCO_USERNAME` | `admin` | Username for authentication |
| `ALFRESCO_PASSWORD` | `admin` | Password for authentication |
| `ALFRESCO_VERIFY_SSL` | `false` | Verify SSL certificates |
| `ALFRESCO_TIMEOUT` | `30` | Request timeout (seconds) |

### Windows-Specific Variables (if needed)

For Windows systems experiencing character encoding issues:

```json
"env": {
  "ALFRESCO_URL": "http://localhost:8080",
  "ALFRESCO_USERNAME": "admin",
  "ALFRESCO_PASSWORD": "admin",
  "PYTHONIOENCODING": "utf-8",
  "PYTHONLEGACYWINDOWSSTDIO": "1"
}
```

## 🚀 Transport Options

The MCP server supports three transport protocols:

### STDIO (Default)
- **Fastest** and most efficient
- Direct MCP protocol communication
- Recommended for most use cases
- Args: `["--transport", "stdio"]` (optional, it's the default)

### HTTP 
- RESTful API interface
- Useful for web services and testing
- Args: `["--transport", "http", "--port", "8001"]`

### SSE (Server-Sent Events)
- Real-time streaming updates
- Good for live monitoring
- Args: `["--transport", "sse", "--port", "8003"]`

## 🧪 Testing Your Configuration

After setting up your MCP client:

1. **Start Your Client**: Launch your MCP-enabled application
2. **Check Connection**: Look for "python-alfresco-mcp-server" in connected servers
3. **Test Basic Functionality**:
   - Try the `repository_info` tool to verify connection
   - Run a simple `search_content` query
   - Check that all 15 tools are available

## 🛠️ Troubleshooting

### Common Issues

1. **Command Not Found**
   - Ensure the package is installed correctly
   - For pipx: Run `pipx list` to verify installation
   - For source: Ensure UV is installed and working directory is correct

2. **Connection Failures**
   - Check Alfresco server is running
   - Verify environment variables are set correctly
   - Test connection with `curl http://localhost:8080/alfresco`

3. **Permission Errors**
   - Verify Alfresco username/password
   - Check that user has appropriate permissions
   - Try with admin credentials first

4. **Character Encoding (Windows)**
   - Add Windows-specific environment variables
   - Ensure UTF-8 encoding is configured

### Getting Help

- 📚 **Documentation**: Complete guides in [`../docs/`](./README.md)
- 🛠️ **Troubleshooting**: [Troubleshooting Guide](./troubleshooting.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/stevereiner/python-alfresco-mcp-server/issues)

## ⚠️ Security Notes

- **Never commit configuration files** with real credentials to version control
- **Use environment variables** for production deployments
- **Consider using .env files** for local development (they're ignored by git)
- **Use strong passwords** for production Alfresco servers 
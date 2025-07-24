# MCP Server Testing Instructions

## 🟢 Server Status: RUNNING
- **Process**: Python PID 57420 ✅
- **Port**: 8003 LISTENING ✅  
- **URL**: `http://localhost:8003/mcp/` ✅

## 🌐 MCP Inspector Testing

### Why Browser Shows Error
The error `"Not Acceptable: Client must accept text/event-stream"` is **NORMAL**:
- MCP servers use Server-Sent Events (SSE) format
- Regular browsers can't handle MCP protocol
- You need the MCP Inspector tool

### Setup MCP Inspector
1. **Download**: [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
2. **Install**: Follow their setup instructions
3. **Connect to**: `http://localhost:8003`
4. **No token required** - it's local development

### Expected in MCP Inspector
- ✅ Server connection successful
- ✅ 10 tools available (search_content, browse_repository, etc.)
- ✅ "Risky auth" warning - NORMAL for development
- ✅ Can test individual tools

## 💬 Claude Desktop Testing (Easier)

### Setup
1. **Config ready**: `claude-desktop-config.json` ✅
2. **Restart**: Claude Desktop application
3. **Ready**: MCP tools appear in conversation

### Your Config File
```json
{
  "mcpServers": {
    "alfresco": {
      "command": "C:\\newdev3\\python-alfresco-mcp-server\\venv_clean\\Scripts\\python.exe",
      "args": [
        "C:\\newdev3\\python-alfresco-mcp-server\\alfresco_mcp_server\\fastmcp_server.py"
      ],
      "env": {
        "ALFRESCO_URL": "http://localhost:8080",
        "ALFRESCO_USERNAME": "admin", 
        "ALFRESCO_PASSWORD": "admin"
      }
    }
  }
}
```

### Testing in Claude
Ask Claude to:
- Search for content: "Search for documents about 'project'"
- Browse repository: "Show me the repository structure"
- Get node info: "Get details about the root folder"

## 🔒 Security Notes

### LOCAL ONLY - No Central Registration
- ✅ Server runs on `localhost:8003` only
- ✅ Not accessible from internet
- ✅ Not registered in any central directory
- ✅ Private development server

### If You're Concerned About Name
The server name "Alfresco Document Management Server" is just a display name:
- ✅ Not registered anywhere
- ✅ Only visible to connected clients
- ✅ Can be changed in code if desired

## 🧪 Quick Test Commands

### Test Server Status
```bash
python tests/mcp_specific/test_server_status.py
```

### Test Server Tools
```bash
python tests/mcp_specific/test_server_fixed.py
```

### Stop Server
```bash
# Find and kill process 57420
taskkill /PID 57420 /F
```

## 🎯 Recommended Testing Order
1. **Start with Claude Desktop** (easiest to test)
2. **Then try MCP Inspector** (if you want detailed tool testing)
3. **Both use the same server** - no conflicts 
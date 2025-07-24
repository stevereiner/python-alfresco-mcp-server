# Starting MCP Server for Testing

## For MCP Inspector Testing (HTTP)

### Option 1: Using PowerShell
```powershell
cd C:\newdev3\python-alfresco-mcp-server
.\venv_clean\Scripts\activate
fastmcp run alfresco_mcp_server.fastmcp_server --host localhost --port 8003
```

### Option 2: Using Command Prompt
```cmd
cd C:\newdev3\python-alfresco-mcp-server
venv_clean\Scripts\activate.bat
fastmcp run alfresco_mcp_server.fastmcp_server --host localhost --port 8003
```

## For Claude Desktop Testing (STDIO)
Claude Desktop uses the stdio transport via the config file:
`claude-desktop-config.json`

## Testing Server Status
After starting the HTTP server, run:
```bash
python tests/mcp_specific/test_server_status.py
```

## MCP Inspector Setup
1. Start HTTP server on port 8003 (see above)
2. Open MCP Inspector in browser
3. Use URL: `http://localhost:8003`
4. **Note**: MCP Inspector will show warning about "risky auth" and include token in URL - this is normal for development testing

## Important Notes
- Make sure you're using `venv_clean` which has all the correct dependencies
- The FastMCP server will show import success messages when starting correctly
- If you see pydantic import errors, make sure you're using the correct virtual environment 
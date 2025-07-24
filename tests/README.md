# Testing Structure

This directory contains tests organized by their purpose.

## MCP Server Tests
- `test_*.py` files in the root test the MCP server functionality
- `mcp_specific/` contains files specifically for testing MCP server deployment

### Main Test Files (MCP Server Functionality)
- `test_unit_tools.py` - Unit tests for MCP tools
- `test_integration.py` - Integration tests with Alfresco
- `test_fastmcp_2_0.py` - FastMCP 2.0 specific tests
- `test_coverage.py` - Test coverage validation
- `test_authentication.py` - Authentication tests
- `test_search_debug.py` - Search functionality debugging
- `test_simple_search.py` - Simple search tests
- `test_response_structure.py` - Response structure validation
- `test_comprehensive_scenarios.py` - Comprehensive scenario testing

### MCP Specific (Deployment & Inspector)
- `mcp_specific/test_with_mcp_client.py` - MCP client testing
- `mcp_specific/test_http_server.ps1` - HTTP server testing script
- `mcp_specific/mcp_testing_guide.md` - Testing guide
- `mcp_specific/test_with_mcp_inspector.md` - MCP Inspector testing
- `mcp_specific/test_server_status.py` - Server status check

## Running Tests

### Unit Tests
```bash
python -m pytest tests/test_unit_tools.py -v
```

### Integration Tests (requires live Alfresco)
```bash
python -m pytest tests/test_integration.py -v
```

### MCP Server Status
```bash
python tests/mcp_specific/test_server_status.py
```

## Testing with MCP Inspector
1. Start HTTP server: `fastmcp run alfresco_mcp_server.fastmcp_server --host localhost --port 8003`
2. Use MCP Inspector with URL: `http://localhost:8003`
3. Note: MCP Inspector shows warning about risky auth and includes token in URL

## Testing with Claude Desktop
1. Update `claude-desktop-config.json` with current paths
2. Restart Claude Desktop application
3. Test MCP tools directly in Claude conversation 
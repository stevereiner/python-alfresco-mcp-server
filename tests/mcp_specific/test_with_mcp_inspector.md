# Testing with MCP Inspector

## Step 1: Start MCP Inspector

```bash
# Launch MCP Inspector
npx @modelcontextprotocol/inspector
```

This will open a web interface (usually at http://localhost:3000) where you can interactively test your MCP server.

## Step 2: Configure Server Connection

In the MCP Inspector interface:

1. **Server Type**: Select "stdio"
2. **Command**: Enter `python`
3. **Arguments**: Add these as separate entries:
   - `-m`
   - `alfresco_mcp_server.fastmcp_server`
4. **Environment Variables** (if needed):
   - `ALFRESCO_URL`: `http://localhost:8080`
   - `ALFRESCO_USERNAME`: `admin`
   - `ALFRESCO_PASSWORD`: `admin`
   - `ALFRESCO_VERIFY_SSL`: `false`

## Step 3: Connect and Explore

### Available Tools (15 total):
1. **search_content** - Search documents and folders
2. **search_by_metadata** - Search by metadata properties
3. **advanced_search** - Advanced search with filters
4. **cmis_search** - CMIS SQL-based search
5. **upload_document** - Upload new documents
6. **download_document** - Download document content
7. **browse_repository** - Browse repository structure
8. **repository_info** - Get repository information and status
9. **checkout_document** - Check out for editing
10. **checkin_document** - Check in after editing
11. **cancel_checkout** - Cancel document checkout
12. **delete_node** - Delete documents/folders
13. **get_node_properties** - Get node metadata
14. **update_node_properties** - Update node metadata
15. **create_folder** - Create new folders

### Available Resources (5 total):
1. **alfresco://repository/info** - Repository information
2. **alfresco://repository/health** - Health status
3. **alfresco://repository/stats** - Usage statistics
4. **alfresco://repository/config** - Configuration details
5. **alfresco://repository/{section}** - Dynamic repository info

### Available Prompts (1 total):
1. **search_and_analyze** - AI-friendly search template

## Step 4: Test Examples

### Quick Tests (No Alfresco Required):
- List tools: Should show all 15 tools
- List resources: Should show all 5 resources
- List prompts: Should show search_and_analyze prompt

### With Live Alfresco Server:
1. **Test Search**: 
   - Tool: `search_content`
   - Parameters: `{"query": "test", "max_results": 5}`

2. **Test Repository Info**:
   - Resource: `alfresco://repository/info`

3. **Test Create Folder**:
   - Tool: `create_folder`
   - Parameters: `{"folder_name": "MCP Test Folder", "description": "Created via MCP Inspector"}`

## Step 5: Advanced Testing

### Error Handling:
- Try invalid parameters
- Test without Alfresco connection
- Test with wrong credentials

### Performance:
- Large search queries
- Multiple concurrent operations
- File upload/download operations

## Troubleshooting

### Common Issues:
1. **Inspector won't start**: Check Node.js version, try `npm install -g @modelcontextprotocol/inspector`
2. **Server connection fails**: Verify Python path and module installation
3. **Alfresco errors**: Check server status, credentials, and network connectivity
4. **Tool execution fails**: Verify parameters match schema requirements

### Environment Setup:
```bash
# Windows PowerShell
$env:ALFRESCO_URL="http://localhost:8080"
$env:ALFRESCO_USERNAME="admin"
$env:ALFRESCO_PASSWORD="admin"
$env:ALFRESCO_VERIFY_SSL="false"

# Or use .env file (recommended)
# Copy sample-dot-env.txt to .env and modify
```

## Next Steps

1. **Start simple**: Test tool/resource listing first
2. **Add credentials**: Set up environment variables for Alfresco
3. **Test incrementally**: One tool at a time
4. **Explore features**: Try different parameters and combinations
5. **Production testing**: Test with your actual Alfresco deployment 
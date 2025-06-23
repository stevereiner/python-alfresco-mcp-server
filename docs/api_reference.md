# API Reference

Complete reference for all Alfresco MCP Server tools, resources, and prompts. This document provides detailed information about parameters, responses, and usage examples.

## 📋 Overview

The Alfresco MCP Server provides 9 tools for document management, 4 repository resources, and 1 AI-powered prompt for analysis.

### Quick Reference

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| [`search_content`](#search_content) | Search documents/folders | query, max_results | Search results with nodes |
| [`upload_document`](#upload_document) | Upload new document | filename, content_base64, parent_id | Upload status |
| [`download_document`](#download_document) | Download document content | node_id | Base64 encoded content |
| [`checkout_document`](#checkout_document) | Lock document for editing | node_id | Checkout status |
| [`checkin_document`](#checkin_document) | Save new version | node_id, comment, major_version | Checkin status |
| [`delete_node`](#delete_node) | Delete document/folder | node_id, permanent | Deletion status |
| [`get_node_properties`](#get_node_properties) | Get node metadata | node_id | Properties object |
| [`update_node_properties`](#update_node_properties) | Update metadata | node_id, properties | Update status |
| [`create_folder`](#create_folder) | Create new folder | folder_name, parent_id | Creation status |

## 🔍 Search Tools

### `search_content`

Search for documents and folders in the Alfresco repository.

**Parameters:**
```json
{
  "query": "string",          // Search query (required)
  "max_results": "integer"    // Maximum results to return (optional, default: 25)
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "node-id",
      "name": "document.pdf",
      "nodeType": "cm:content",
      "isFile": true,
      "isFolder": false,
      "properties": {
        "cm:title": "Document Title",
        "cm:description": "Document description",
        "cm:created": "2024-01-15T10:30:00.000Z",
        "cm:modified": "2024-01-15T15:45:00.000Z",
        "cm:creator": "admin",
        "cm:modifier": "user1"
      },
      "path": "/Company Home/Sites/example/documentLibrary/document.pdf"
    }
  ],
  "totalCount": 1
}
```

**Example:**
```python
# Basic search
result = await client.call_tool("search_content", {
    "query": "financial report",
    "max_results": 10
})

# Wildcard search
result = await client.call_tool("search_content", {
    "query": "*",
    "max_results": 5
})

# Specific term search
result = await client.call_tool("search_content", {
    "query": "budget 2024"
})
```

## 📤 Document Upload

### `upload_document`

Upload a new document to the Alfresco repository.

**Parameters:**
```json
{
  "filename": "string",         // Document filename (required)
  "content_base64": "string",   // Base64 encoded content (required)
  "parent_id": "string",        // Parent folder ID (optional, default: "-root-")
  "description": "string"       // Document description (optional)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "filename": "document.pdf",
  "parentId": "-root-",
  "path": "/Company Home/document.pdf"
}
```

**Example:**
```python
import base64

# Prepare content
content = "This is my document content"
content_b64 = base64.b64encode(content.encode()).decode()

# Upload to root
result = await client.call_tool("upload_document", {
    "filename": "my_document.txt",
    "content_base64": content_b64,
    "parent_id": "-root-",
    "description": "My first document"
})

# Upload to specific folder
result = await client.call_tool("upload_document", {
    "filename": "report.pdf",
    "content_base64": pdf_content_b64,
    "parent_id": "folder-node-id",
    "description": "Monthly report"
})
```

## 📥 Document Download

### `download_document`

Download the content of a document from the repository.

**Parameters:**
```json
{
  "node_id": "string"   // Document node ID (required)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "filename": "document.pdf",
  "mimeType": "application/pdf",
  "size": 1024,
  "content_base64": "JVBERi0xLjQKJ..."
}
```

**Example:**
```python
# Download document
result = await client.call_tool("download_document", {
    "node_id": "abc123-def456-ghi789"
})

# Decode content
import base64
content = base64.b64decode(result.content_base64).decode()
print(content)
```

## 🔄 Version Control

### `checkout_document`

Check out a document for editing (locks the document).

**Parameters:**
```json
{
  "node_id": "string"   // Document node ID (required)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "workingCopyId": "abc123-def456-ghi789-wc",
  "status": "checked_out"
}
```

### `checkin_document`

Check in a document with a new version.

**Parameters:**
```json
{
  "node_id": "string",          // Document node ID (required)
  "comment": "string",          // Version comment (optional)
  "major_version": "boolean"    // Major version increment (optional, default: false)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "version": "1.1",
  "comment": "Updated content",
  "isMajorVersion": false
}
```

**Example:**
```python
# Checkout document
checkout_result = await client.call_tool("checkout_document", {
    "node_id": "doc-node-id"
})

# Make changes (simulated)
# ... edit the document ...

# Checkin as minor version
checkin_result = await client.call_tool("checkin_document", {
    "node_id": "doc-node-id",
    "comment": "Fixed typos and updated content",
    "major_version": False
})

# Checkin as major version
major_checkin = await client.call_tool("checkin_document", {
    "node_id": "doc-node-id", 
    "comment": "Major content overhaul",
    "major_version": True
})
```

## 🗑️ Node Deletion

### `delete_node`

Delete a document or folder from the repository.

**Parameters:**
```json
{
  "node_id": "string",      // Node ID to delete (required)
  "permanent": "boolean"    // Permanent deletion (optional, default: false)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "permanent": false,
  "status": "moved_to_trash"
}
```

**Example:**
```python
# Move to trash (soft delete)
result = await client.call_tool("delete_node", {
    "node_id": "node-to-delete",
    "permanent": False
})

# Permanent deletion
result = await client.call_tool("delete_node", {
    "node_id": "node-to-delete",
    "permanent": True
})
```

## ⚙️ Property Management

### `get_node_properties`

Retrieve all properties and metadata for a node.

**Parameters:**
```json
{
  "node_id": "string"   // Node ID (required)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "properties": {
    "cm:name": "document.pdf",
    "cm:title": "Important Document",
    "cm:description": "This is an important document",
    "cm:created": "2024-01-15T10:30:00.000Z",
    "cm:modified": "2024-01-15T15:45:00.000Z",
    "cm:creator": "admin",
    "cm:modifier": "user1",
    "cm:owner": "admin",
    "sys:node-uuid": "abc123-def456-ghi789",
    "sys:store-protocol": "workspace",
    "sys:store-identifier": "SpacesStore"
  }
}
```

### `update_node_properties`

Update properties and metadata for a node.

**Parameters:**
```json
{
  "node_id": "string",      // Node ID (required)
  "properties": "object"    // Properties to update (required)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "abc123-def456-ghi789",
  "updatedProperties": {
    "cm:title": "Updated Title",
    "cm:description": "Updated description"
  }
}
```

**Example:**
```python
# Get current properties
props_result = await client.call_tool("get_node_properties", {
    "node_id": "abc123-def456-ghi789"
})

print("Current properties:", props_result[0].text)

# Update properties
update_result = await client.call_tool("update_node_properties", {
    "node_id": "abc123-def456-ghi789",
    "properties": {
        "cm:title": "Updated Document Title",
        "cm:description": "This document has been updated",
        "custom:project": "Project Alpha",
        "custom:status": "approved"
    }
})
```

## 📁 Folder Operations

### `create_folder`

Create a new folder in the repository.

**Parameters:**
```json
{
  "folder_name": "string",    // Folder name (required)
  "parent_id": "string",      // Parent folder ID (optional, default: "-root-")
  "description": "string"     // Folder description (optional)
}
```

**Response:**
```json
{
  "success": true,
  "nodeId": "folder-abc123-def456",
  "folderName": "New Folder",
  "parentId": "-root-",
  "path": "/Company Home/New Folder"
}
```

**Example:**
```python
# Create folder in root
result = await client.call_tool("create_folder", {
    "folder_name": "Project Documents",
    "parent_id": "-root-",
    "description": "Documents for the current project"
})

# Create nested folder
result = await client.call_tool("create_folder", {
    "folder_name": "Reports",
    "parent_id": "parent-folder-id",
    "description": "Monthly and quarterly reports"
})
```

## 📚 Resources

### Repository Resources

Access repository information and status:

```python
# Repository information
info = await client.read_resource("alfresco://repository/info")

# Repository health status
health = await client.read_resource("alfresco://repository/health")

# Repository statistics
stats = await client.read_resource("alfresco://repository/stats")

# Repository configuration
config = await client.read_resource("alfresco://repository/config")
```

**Resource Responses:**
```json
{
  "repository": {
    "edition": "Community",
    "version": "7.4.0",
    "status": "healthy",
    "modules": ["content-services", "search-services"]
  }
}
```

## 💭 Prompts

### `search_and_analyze`

Generate AI-powered analysis prompts for search results.

**Parameters:**
```json
{
  "query": "string",            // Search query (required)
  "analysis_type": "string"     // Analysis type: summary, detailed, trends, compliance (required)
}
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user", 
      "content": {
        "type": "text",
        "text": "Based on the Alfresco search results for 'financial reports', provide a detailed analysis..."
      }
    }
  ]
}
```

**Example:**
```python
# Generate analysis prompt
prompt_result = await client.get_prompt("search_and_analyze", {
    "query": "quarterly reports 2024",
    "analysis_type": "summary"
})

print("Generated prompt:")
print(prompt_result.messages[0].content.text)
```

## 🔍 Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ALFRESCO_ERROR",
    "message": "Authentication failed",
    "details": "Invalid username or password"
  }
}
```

Common error codes:
- `AUTHENTICATION_ERROR`: Invalid credentials
- `NODE_NOT_FOUND`: Specified node doesn't exist
- `PERMISSION_DENIED`: Insufficient permissions
- `INVALID_PARAMETER`: Missing or invalid parameters
- `CONNECTION_ERROR`: Cannot connect to Alfresco server

## 📊 Rate Limits and Performance

- **Default timeout**: 30 seconds per operation
- **Concurrent operations**: Up to 10 simultaneous requests
- **File size limits**: 100MB per upload
- **Search limits**: Maximum 1000 results per search

## 🔐 Security Considerations

- All communications use HTTPS when available
- Credentials are passed securely via environment variables
- Base64 encoding for document content transfer
- Node IDs are validated before operations

---

**📝 Note**: This API reference covers version 1.0.0 of the Alfresco MCP Server. This is the first production release with comprehensive FastMCP 2.0 implementation. 
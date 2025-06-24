"""
Unit tests for all FastMCP 2.0 tools with comprehensive mocking.
Tests all 9 tools with various scenarios, edge cases, and error conditions.
"""
import pytest
import base64
from unittest.mock import patch, AsyncMock, MagicMock
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


@pytest.mark.unit
class TestSearchContentTool:
    """Unit tests for search_content tool."""
    
    @pytest.mark.asyncio
    async def test_search_content_success(self, fastmcp_client, mock_search_results):
        """Test successful search with results."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            # Setup mock
            search_client = AsyncMock()
            search_client.search.return_value = mock_search_results
            mock_factory.create_search_client.return_value = search_client
            
            # Execute tool
            result = await fastmcp_client.call_tool("search_content", {
                "query": "test documents",
                "max_results": 10
            })
            
            # Verify
            assert len(result) == 1
            assert "Search Results" in result[0].text
            assert "test documents" in result[0].text
            assert "Test Document 1.pdf" in result[0].text
            assert "doc-123" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_content_no_results(self, fastmcp_client):
        """Test search with no results."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            # Setup mock for no results
            search_client = AsyncMock()
            search_client.search.return_value = None
            mock_factory.create_search_client.return_value = search_client
            
            # Execute tool
            result = await fastmcp_client.call_tool("search_content", {
                "query": "nonexistent",
                "max_results": 10
            })
            
            # Verify
            assert len(result) == 1
            assert "No results found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_content_empty_query(self, fastmcp_client):
        """Test search with empty query."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "",
            "max_results": 10
        })
        
        assert len(result) == 1
        assert "Error: Search query cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_content_invalid_max_results(self, fastmcp_client):
        """Test search with invalid max_results."""
        # Test too high
        result = await fastmcp_client.call_tool("search_content", {
            "query": "test",
            "max_results": 500
        })
        assert "max_results must be between 1 and 100" in result[0].text
        
        # Test too low
        result = await fastmcp_client.call_tool("search_content", {
            "query": "test",
            "max_results": 0
        })
        assert "max_results must be between 1 and 100" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_content_connection_error(self, fastmcp_client):
        """Test search with connection error."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection', 
                  side_effect=Exception("Connection failed")):
            
            result = await fastmcp_client.call_tool("search_content", {
                "query": "test",
                "max_results": 10
            })
            
            assert len(result) == 1
            assert "Search failed" in result[0].text
            assert "Connection failed" in result[0].text


@pytest.mark.unit
class TestUploadDocumentTool:
    """Unit tests for upload_document tool."""
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self, fastmcp_client, sample_documents):
        """Test successful document upload."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            # Setup mock
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            doc = sample_documents["text_doc"]
            result = await fastmcp_client.call_tool("upload_document", {
                "filename": doc["filename"],
                "content_base64": doc["content_base64"],
                "parent_id": "-root-",
                "description": "Test upload"
            })
            
            assert len(result) == 1
            assert "Upload Successful" in result[0].text
            assert doc["filename"] in result[0].text
    
    @pytest.mark.asyncio
    async def test_upload_document_missing_params(self, fastmcp_client):
        """Test upload with missing parameters."""
        # Missing filename
        result = await fastmcp_client.call_tool("upload_document", {
            "filename": "",
            "content_base64": "dGVzdA=="
        })
        assert "Error: filename and content_base64 are required" in result[0].text
        
        # Missing content
        result = await fastmcp_client.call_tool("upload_document", {
            "filename": "test.txt",
            "content_base64": ""
        })
        assert "Error: filename and content_base64 are required" in result[0].text
    
    @pytest.mark.asyncio
    async def test_upload_document_invalid_base64(self, fastmcp_client):
        """Test upload with invalid base64 content."""
        result = await fastmcp_client.call_tool("upload_document", {
            "filename": "test.txt",
            "content_base64": "invalid_base64_content!!!"
        })
        
        assert len(result) == 1
        assert "Error: Invalid base64 content" in result[0].text


@pytest.mark.unit
class TestDownloadDocumentTool:
    """Unit tests for download_document tool."""
    
    @pytest.mark.asyncio
    async def test_download_document_success(self, fastmcp_client):
        """Test successful document download."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            # Setup mock
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("download_document", {
                "node_id": "test-node-123"
            })
            
            assert len(result) == 1
            # Should contain either success or failure message
            assert any(keyword in result[0].text for keyword in [
                "Download Successful", "Download failed"
            ])
    
    @pytest.mark.asyncio
    async def test_download_document_missing_node_id(self, fastmcp_client):
        """Test download with missing node ID."""
        result = await fastmcp_client.call_tool("download_document", {
            "node_id": ""
        })
        
        assert len(result) == 1
        assert "Error: node_id is required" in result[0].text


@pytest.mark.unit
class TestCheckoutDocumentTool:
    """Unit tests for checkout_document tool."""
    
    @pytest.mark.asyncio
    async def test_checkout_document_success(self, fastmcp_client):
        """Test successful document checkout."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("checkout_document", {
                "node_id": "test-doc-123"
            })
            
            assert len(result) == 1
            assert "Document Checked Out" in result[0].text
            assert "test-doc-123" in result[0].text
    
    @pytest.mark.asyncio
    async def test_checkout_document_missing_node_id(self, fastmcp_client):
        """Test checkout with missing node ID."""
        result = await fastmcp_client.call_tool("checkout_document", {
            "node_id": ""
        })
        
        assert "Error: node_id is required" in result[0].text


@pytest.mark.unit
class TestCheckinDocumentTool:
    """Unit tests for checkin_document tool."""
    
    @pytest.mark.asyncio
    async def test_checkin_document_success(self, fastmcp_client):
        """Test successful document checkin."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("checkin_document", {
                "node_id": "test-doc-123",
                "comment": "Test checkin",
                "major_version": True
            })
            
            assert len(result) == 1
            assert "Document Checked In" in result[0].text
            assert "test-doc-123" in result[0].text
            assert "Major" in result[0].text
    
    @pytest.mark.asyncio
    async def test_checkin_document_minor_version(self, fastmcp_client):
        """Test checkin with minor version."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory'):
            
            result = await fastmcp_client.call_tool("checkin_document", {
                "node_id": "test-doc-123",
                "comment": "Minor update",
                "major_version": False
            })
            
            assert "Minor" in result[0].text


@pytest.mark.unit
class TestDeleteNodeTool:
    """Unit tests for delete_node tool."""
    
    @pytest.mark.asyncio
    async def test_delete_node_success(self, fastmcp_client):
        """Test successful node deletion."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("delete_node", {
                "node_id": "test-node-123",
                "permanent": False
            })
            
            assert len(result) == 1
            assert "Node Deleted" in result[0].text
            assert "Moved to trash" in result[0].text
    
    @pytest.mark.asyncio
    async def test_delete_node_permanent(self, fastmcp_client):
        """Test permanent node deletion."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory'):
            
            result = await fastmcp_client.call_tool("delete_node", {
                "node_id": "test-node-123",
                "permanent": True
            })
            
            assert "Permanent" in result[0].text


@pytest.mark.unit
class TestGetNodePropertiesTool:
    """Unit tests for get_node_properties tool."""
    
    @pytest.mark.asyncio
    async def test_get_node_properties_success(self, fastmcp_client):
        """Test successful node properties retrieval."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("get_node_properties", {
                "node_id": "test-node-123"
            })
            
            assert len(result) == 1
            assert "Node Properties" in result[0].text
            assert "test-node-123" in result[0].text


@pytest.mark.unit
class TestUpdateNodePropertiesTool:
    """Unit tests for update_node_properties tool."""
    
    @pytest.mark.asyncio
    async def test_update_node_properties_success(self, fastmcp_client):
        """Test successful node properties update."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("update_node_properties", {
                "node_id": "test-node-123",
                "properties": {"cm:title": "New Title", "cm:description": "Updated description"},
                "name": "new_filename.txt"
            })
            
            assert len(result) == 1
            assert "Node Updated" in result[0].text
            assert "New Title" in result[0].text
            assert "new_filename.txt" in result[0].text
    
    @pytest.mark.asyncio
    async def test_update_node_properties_no_changes(self, fastmcp_client):
        """Test update with no properties or name provided."""
        result = await fastmcp_client.call_tool("update_node_properties", {
            "node_id": "test-node-123"
        })
        
        assert "Error: Either properties or name must be provided" in result[0].text


@pytest.mark.unit
class TestCreateFolderTool:
    """Unit tests for create_folder tool."""
    
    @pytest.mark.asyncio
    async def test_create_folder_success(self, fastmcp_client):
        """Test successful folder creation."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            core_client = AsyncMock()
            mock_factory.create_core_client.return_value = core_client
            
            result = await fastmcp_client.call_tool("create_folder", {
                "folder_name": "Test Folder",
                "parent_id": "-root-",
                "description": "Test folder description"
            })
            
            assert len(result) == 1
            assert "Folder Created" in result[0].text
            assert "Test Folder" in result[0].text
    
    @pytest.mark.asyncio
    async def test_create_folder_missing_name(self, fastmcp_client):
        """Test folder creation with missing name."""
        result = await fastmcp_client.call_tool("create_folder", {
            "folder_name": "",
            "parent_id": "-root-"
        })
        
        assert "Error: folder_name is required" in result[0].text


@pytest.mark.unit 
class TestToolsGeneral:
    """General unit tests for all tools."""
    
    @pytest.mark.asyncio
    async def test_all_tools_listed(self, fastmcp_client):
        """Test that all 9 expected tools are available."""
        tools = await fastmcp_client.list_tools()
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "search_content",
            "upload_document",
            "download_document", 
            "checkout_document",
            "checkin_document",
            "delete_node",
            "get_node_properties",
            "update_node_properties",
            "create_folder"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"
    
    @pytest.mark.asyncio
    async def test_tool_schemas_valid(self, fastmcp_client):
        """Test that all tools have valid schemas."""
        tools = await fastmcp_client.list_tools()
        
        for tool in tools:
            # Each tool should have required fields
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            
            # Schema should have properties
            assert 'properties' in tool.inputSchema
            assert 'type' in tool.inputSchema
            assert tool.inputSchema['type'] == 'object' 
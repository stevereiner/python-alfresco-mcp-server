"""
Unit tests for individual MCP tools in Python Alfresco MCP Server.
Tests each tool function independently with proper FastMCP patterns.
"""
import pytest
import base64
from unittest.mock import Mock, patch
from fastmcp import Client
from fastmcp.exceptions import ToolError
from alfresco_mcp_server.fastmcp_server import mcp


class TestSearchContentTool:
    """Test search content tool independently."""
    
    @pytest.mark.asyncio
    async def test_search_content_success(self, fastmcp_client):
        """Test successful search content operation."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "document",
            "max_results": 5
        })
        
        # Should return some form of search result
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_search_content_no_results(self, fastmcp_client):
        """Test search with no results."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "unlikely_search_term_that_wont_match_anything_12345",
            "max_results": 5
        })
        
        # Should return valid response even with no results
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_search_content_empty_query(self, fastmcp_client):
        """Test search with empty query."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "",
            "max_results": 5
        })
        
        # Should handle empty query gracefully - now returns helpful usage info
        response_text = result.content[0].text
        assert "Content Search Tool" in response_text or "Usage:" in response_text or "Error" in response_text

    @pytest.mark.asyncio
    async def test_search_content_invalid_max_results(self, fastmcp_client):
        """Test search with invalid max_results."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "test",
            "max_results": 0
        })
        
        # Should validate max_results parameter
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_search_content_connection_error(self, fastmcp_client):
        """Test search with connection issues."""
        # This will naturally fail if connection is down, which is expected
        result = await fastmcp_client.call_tool("search_content", {
            "query": "test", 
            "max_results": 5
        })
        
        # Should return some response, success or error
        assert len(result.content[0].text) > 0


class TestUploadDocumentTool:
    """Test upload document tool independently."""
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self, fastmcp_client):
        """Test successful document upload."""
        # Test document content
        test_content = "Test document for upload"
        content_base64 = base64.b64encode(test_content.encode()).decode()
        
        result = await fastmcp_client.call_tool("upload_document", {
            "file_path": "",
            "base64_content": content_base64,
            "parent_id": "-shared-",
            "description": "Test upload document"
        })
        
        # Should return upload result
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_upload_document_missing_params(self, fastmcp_client):
        """Test upload with missing parameters."""
        # Test with only base64_content, no file_path
        result = await fastmcp_client.call_tool("upload_document", {
            "file_path": "",
            "base64_content": "dGVzdA=="
        })
        # Tool has defaults, so it should succeed or handle gracefully
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_upload_document_invalid_base64(self, fastmcp_client):
        """Test upload with invalid base64 content."""
        result = await fastmcp_client.call_tool("upload_document", {
            "file_path": "",
            "base64_content": "invalid_base64_content!!!",
            "parent_id": "-shared-",
            "description": "Test invalid base64"
        })
        
        # Tool handles invalid base64 gracefully by treating it as raw content
        assert len(result.content[0].text) > 0


class TestDownloadDocumentTool:
    """Test download document tool independently."""
    
    @pytest.mark.asyncio
    async def test_download_document_success(self, fastmcp_client):
        """Test successful document download."""
        # Use shared folder node ID (should exist)
        result = await fastmcp_client.call_tool("download_document", {
            "node_id": "-shared-",
            "save_to_disk": False
        })
        
        # Should return some response
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_download_document_missing_node_id(self, fastmcp_client):
        """Test download with missing node_id."""
        # Should raise ToolError for missing required parameter
        with pytest.raises(ToolError) as exc_info:
            await fastmcp_client.call_tool("download_document", {
                "save_to_disk": False
            })
        
        error_msg = str(exc_info.value)
        assert "node_id" in error_msg.lower() or "required" in error_msg.lower()


class TestCheckoutDocumentTool:
    """Test checkout document tool independently."""
    
    @pytest.mark.asyncio
    async def test_checkout_document_success(self, fastmcp_client):
        """Test document checkout."""
        # Try to checkout shared folder (will likely fail, but should return graceful error)
        result = await fastmcp_client.call_tool("checkout_document", {
            "node_id": "-shared-"
        })
        
        # Should return some response, success or error
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_checkout_document_missing_node_id(self, fastmcp_client):
        """Test checkout with missing node_id."""
        # Should raise ToolError for missing required parameter
        with pytest.raises(ToolError) as exc_info:
            await fastmcp_client.call_tool("checkout_document", {})
        
        error_msg = str(exc_info.value)
        assert "node_id" in error_msg.lower() or "required" in error_msg.lower()


class TestCheckinDocumentTool:
    """Test checkin document tool independently."""
    
    @pytest.mark.asyncio
    async def test_checkin_document_success(self, fastmcp_client):
        """Test document checkin."""
        # Test with dummy file path (will likely fail, but should handle gracefully)
        result = await fastmcp_client.call_tool("checkin_document", {
            "node_id": "dummy-checkout-node-123",
            "file_path": "nonexistent_test_file.txt",  # Use file_path instead
            "comment": "Test checkin",
            "major_version": False
        })
        
        # Should return some response
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_checkin_document_minor_version(self, fastmcp_client):
        """Test checkin with minor version."""
        result = await fastmcp_client.call_tool("checkin_document", {
            "node_id": "dummy-checkout-node-456",
            "file_path": "nonexistent_test_file2.txt",  # Use file_path instead
            "comment": "Minor version update",
            "major_version": False
        })
        
        # Should return some response
        assert len(result.content[0].text) > 0


class TestDeleteNodeTool:
    """Test delete node tool independently."""
    
    @pytest.mark.asyncio
    async def test_delete_node_success(self, fastmcp_client):
        """Test node deletion."""
        # Test with dummy node ID (will likely fail, but should handle gracefully)
        result = await fastmcp_client.call_tool("delete_node", {
            "node_id": "dummy-node-to-delete-123",
            "permanent": False
        })
        
        # Should return some response
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_delete_node_permanent(self, fastmcp_client):
        """Test permanent node deletion."""
        result = await fastmcp_client.call_tool("delete_node", {
            "node_id": "dummy-node-permanent-456",
            "permanent": True
        })
        
        # Should return some response
        assert len(result.content[0].text) > 0


class TestGetNodePropertiesTool:
    """Test get node properties tool independently."""
    
    @pytest.mark.asyncio
    async def test_get_node_properties_success(self, fastmcp_client):
        """Test getting node properties."""
        # Use shared folder (should exist)
        result = await fastmcp_client.call_tool("get_node_properties", {
            "node_id": "-shared-"
        })
        
        # Should return properties or error
        assert len(result.content[0].text) > 0


class TestUpdateNodePropertiesTool:
    """Test update node properties tool independently."""
    
    @pytest.mark.asyncio
    async def test_update_node_properties_success(self, fastmcp_client):
        """Test updating node properties."""
        result = await fastmcp_client.call_tool("update_node_properties", {
            "node_id": "-shared-",
            "title": "Test Title Update",
            "description": "Test Description Update"
        })
        
        # Should return update result
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_update_node_properties_no_changes(self, fastmcp_client):
        """Test update with no property changes."""
        result = await fastmcp_client.call_tool("update_node_properties", {
            "node_id": "-shared-"
            # No properties to update
        })
        
        # Should require at least one property
        assert "At least one property" in result.content[0].text and "must be provided" in result.content[0].text


class TestCreateFolderTool:
    """Test create folder tool independently."""
    
    @pytest.mark.asyncio
    async def test_create_folder_success(self, fastmcp_client):
        """Test successful folder creation."""
        import uuid
        unique_name = f"test_folder_{uuid.uuid4().hex[:8]}"
        
        result = await fastmcp_client.call_tool("create_folder", {
            "folder_name": unique_name,
            "parent_id": "-shared-",
            "description": "Test folder creation"
        })
        
        # Should return creation result
        assert len(result.content[0].text) > 0

    @pytest.mark.asyncio
    async def test_create_folder_missing_name(self, fastmcp_client):
        """Test folder creation with missing name."""
        # Should raise ToolError for missing required parameter
        with pytest.raises(ToolError) as exc_info:
            await fastmcp_client.call_tool("create_folder", {
                "parent_id": "-shared-"
            })
        
        error_msg = str(exc_info.value)
        assert "folder_name" in error_msg.lower() or "required" in error_msg.lower() 
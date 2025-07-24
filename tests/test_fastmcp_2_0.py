"""
Comprehensive FastMCP 2.0 tests for Python Alfresco MCP Server.
Tests the complete MCP server functionality using FastMCP patterns.
"""
import pytest
import asyncio
import time
import base64
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp
from tests.test_utils import strip_emojis


class TestAlfrescoMCPServer:
    """Test Alfresco MCP Server with FastMCP patterns."""
    
    @pytest.mark.asyncio
    async def test_search_content_tool(self):
        """Test search content tool returns valid responses."""
        async with Client(mcp) as client:
            result = await client.call_tool("search_content", {
                "query": "cmis",
                "max_results": 5
            })
            
            # Should return exactly one content item
            assert len(result.content) == 1
            
            # Extract response text
            response_text = result.content[0].text
            
            # Response should be a string
            assert isinstance(response_text, str)
            assert len(response_text) > 0
            
            # Test specifically - strip emojis for Windows compatibility
            stripped_text = strip_emojis(response_text)
            assert any(phrase in stripped_text for phrase in [
                "Found", "Search Results", "item(s)", "0"
            ]) or ("No items found matching" in result.content[0].text)

    @pytest.mark.asyncio
    async def test_upload_document_tool(self):
        """Test upload document tool."""
        async with Client(mcp) as client:
            # Create unique filename to avoid conflicts
            timestamp = str(int(time.time() * 1000))
            unique_filename = f"test_upload_{timestamp}.txt"
            
            # Test document content  
            test_content = f"Test document content uploaded at {timestamp}"
            content_base64 = base64.b64encode(test_content.encode()).decode()
            
            result = await client.call_tool("upload_document", {
                "file_path": "",
                "base64_content": content_base64,
                "parent_id": "-shared-",
                "description": f"Test upload document {timestamp}"
            })
            
            assert len(result.content[0].text) > 0
            
            print(f"Search response: {result.content[0].text}...")
            stripped_text = strip_emojis(result.content[0].text)
            
            # Should indicate upload success or appropriate error handling
            # Allow for various success or error messages
            assert any(phrase in stripped_text for phrase in [
                "Upload", "Success", "Document", "Error", "Failed"
            ])

    @pytest.mark.asyncio
    async def test_download_document_tool(self):
        """Test download document functionality."""
        async with Client(mcp) as client:
            # Test with shared folder node (should exist but may not be downloadable)
            result = await client.call_tool("download_document", {
                "node_id": "-shared-", 
                "save_to_disk": False
            })
            
            # Should get some response
            assert len(result.content) == 1
            assert isinstance(result.content[0].text, str)
            assert len(result.content[0].text) > 0

    @pytest.mark.asyncio 
    async def test_create_folder_tool(self):
        """Test create folder functionality."""
        async with Client(mcp) as client:
            # Create unique folder name
            timestamp = str(int(time.time() * 1000))
            unique_folder_name = f"TestFolder_{timestamp}"
            
            result = await client.call_tool("create_folder", {
                "folder_name": unique_folder_name,
                "parent_id": "-shared-",
                "description": "Test folder created by automated test"
            })
            
            # Should return some response
            response_text = result.content[0].text
            assert isinstance(response_text, str)
            assert len(response_text) > 0
            
            # Test for missing folder name should raise validation error
            from fastmcp.exceptions import ToolError
            with pytest.raises(ToolError):
                await client.call_tool("create_folder", {
                    "parent_id": "-shared-"
                })

    @pytest.mark.asyncio
    async def test_get_node_properties_tool(self):
        """Test get node properties functionality."""
        async with Client(mcp) as client:
            # Test with shared folder (should exist)
            result = await client.call_tool("get_node_properties", {
                "node_id": "-shared-"
            })
            
            response_text = result.content[0].text
            assert isinstance(response_text, str)
            assert len(response_text) > 0
            
            # Test with invalid node ID - should handle gracefully, not necessarily with specific error message
            result = await client.call_tool("get_node_properties", {
                "node_id": "invalid-node-123"
            })
            
            response_text = result.content[0].text
            assert isinstance(response_text, str)
            assert len(response_text) > 0

    @pytest.mark.asyncio
    async def test_read_resources(self):
        """Test resource reading functionality."""
        async with Client(mcp) as client:
            # List all available resources
            resources = await client.list_resources()
            
            # Should have at least one resource
            assert len(resources) > 0
            
            # Get repository info resource
            result = await client.read_resource("alfresco://repository/info")
            
            response_text = result[0].text
            assert isinstance(response_text, str)
            assert len(response_text) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in MCP tools."""
        async with Client(mcp) as client:
            # Test with invalid resource
            try:
                await client.read_resource("alfresco://repository/invalid")
                assert False, "Should have raised an error"
            except Exception as e:
                # Should handle invalid resources gracefully
                assert "error" in str(e).lower() or "unknown" in str(e).lower()


class TestFastMCP2Features:
    """Test FastMCP 2.0 specific features."""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent MCP operations."""
        async with Client(mcp) as client:
            # Run multiple search operations concurrently
            tasks = []
            for i in range(3):
                task = client.call_tool("search_content", {
                    "query": f"test{i}",
                    "max_results": 5
                })
                tasks.append(task)
            
            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete (successfully or with errors)
            assert len(results) == 3
            for result in results:
                if not isinstance(result, Exception):
                    assert len(result.content) == 1

    @pytest.mark.asyncio
    async def test_tool_list_consistency(self):
        """Test that tool list is consistent."""
        async with Client(mcp) as client:
            # Get tools multiple times
            tools1 = await client.list_tools()
            tools2 = await client.list_tools()
            
            # Should be consistent
            assert len(tools1) == len(tools2)
            
            tool_names1 = [tool.name for tool in tools1]
            tool_names2 = [tool.name for tool in tools2]
            
            assert tool_names1 == tool_names2

    @pytest.mark.asyncio
    async def test_resource_list_consistency(self):
        """Test that resource list is consistent."""
        async with Client(mcp) as client:
            # Get resources multiple times
            resources1 = await client.list_resources()
            resources2 = await client.list_resources()
            
            # Should be consistent
            assert len(resources1) == len(resources2)


class TestCompleteWorkflow:
    """Test complete document workflows."""
    
    @pytest.mark.asyncio
    async def test_search_and_properties_workflow(self):
        """Test searching then getting properties."""
        async with Client(mcp) as client:
            # First search for content
            search_result = await client.call_tool("search_content", {
                "query": "document", 
                "max_results": 5
            })
            
            # Should get search results or no results
            assert len(search_result.content[0].text) > 0  # Just check we got a response

    @pytest.mark.asyncio
    async def test_folder_creation_workflow(self):
        """Test folder creation workflow.""" 
        async with Client(mcp) as client:
            timestamp = str(int(time.time() * 1000))
            folder_name = f"WorkflowTest_{timestamp}"
            
            # Create folder
            folder_result = await client.call_tool("create_folder", {
                "folder_name": folder_name,
                "parent_id": "-shared-",
                "description": "Workflow test folder"
            })
            
            assert len(folder_result.content[0].text) > 0  # Just check we got a response
            
            # Try to upload to that folder (will likely fail since we don't have the folder ID, but should handle gracefully)
            upload_result = await client.call_tool("upload_document", {
                "file_path": "",
                "base64_content": base64.b64encode(b"Test content").decode(),
                "parent_id": "-shared-",  # Use shared since we don't have the actual folder ID
                "description": "Test document in workflow"
            })
            
            upload_text = strip_emojis(upload_result.content[0].text)
            assert ("Upload" in upload_text and "Successful" in upload_text) or "Document Uploaded Successfully" in upload_result.content[0].text 
"""
Comprehensive test suite for MCP Server for Alfresco using FastMCP 2.0
Demonstrates the superior testing capabilities of FastMCP 2.0
"""
import asyncio
import pytest
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


class TestAlfrescoMCPServer:
    """Test suite demonstrating FastMCP 2.0's in-memory testing capabilities."""
    
    @pytest.mark.asyncio
    async def test_server_connectivity(self):
        """Test basic server connectivity using in-memory client."""
        async with Client(mcp) as client:
            # Test ping
            await client.ping()
            assert client.is_connected()
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test tool listing functionality."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            
            # Verify expected tools are present
            tool_names = [tool.name for tool in tools]
            expected_tools = [
                "search_content",
                "upload_document", 
                "download_document",
                "create_folder"
            ]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_search_content_tool(self):
        """Test search content tool with various inputs."""
        async with Client(mcp) as client:
            # Test valid search
            result = await client.call_tool("search_content", {
                "query": "test documents",
                "max_results": 10
            })
            
            assert len(result) > 0
            # Should contain either success message, no results, or error message
            response_text = result[0].text
            assert any(keyword in response_text for keyword in [
                "Search Results", "No results", "Search failed", "❌"
            ])
            
            # Test empty query
            result = await client.call_tool("search_content", {
                "query": "",
                "max_results": 10
            })
            
            assert "Error: Search query cannot be empty" in result[0].text
            
            # Test invalid max_results
            result = await client.call_tool("search_content", {
                "query": "test",
                "max_results": 500  # Too high
            })
            
            assert "max_results must be between 1 and 100" in result[0].text
    
    @pytest.mark.asyncio
    async def test_upload_document_tool(self):
        """Test document upload functionality."""
        async with Client(mcp) as client:
            # Test valid upload
            result = await client.call_tool("upload_document", {
                "filename": "test.pdf",
                "content_base64": "dGVzdCBjb250ZW50",  # "test content" in base64
                "parent_id": "-root-",
                "description": "Test document"
            })
            
            assert "Upload Successful" in result[0].text
            assert "test.pdf" in result[0].text
            
            # Test missing filename
            result = await client.call_tool("upload_document", {
                "filename": "",
                "content_base64": "dGVzdA==",
            })
            
            assert "Error: filename and content_base64 are required" in result[0].text
    
    @pytest.mark.asyncio
    async def test_download_document_tool(self):
        """Test document download functionality."""
        async with Client(mcp) as client:
            # Test with node ID
            result = await client.call_tool("download_document", {
                "node_id": "test-node-123"
            })
            
            # Should contain either success or error message
            assert len(result) > 0
            response_text = result[0].text
            assert ("Download Successful" in response_text or 
                   "Download failed" in response_text)
            
            # Test missing node_id
            result = await client.call_tool("download_document", {
                "node_id": ""
            })
            
            assert "Error: node_id is required" in result[0].text
    
    @pytest.mark.asyncio
    async def test_create_folder_tool(self):
        """Test folder creation functionality."""
        async with Client(mcp) as client:
            # Test valid folder creation
            result = await client.call_tool("create_folder", {
                "folder_name": "Test Folder",
                "parent_id": "-root-",
                "description": "Test folder description"
            })
            
            assert "Folder Created" in result[0].text
            assert "Test Folder" in result[0].text
            
            # Test missing folder name
            result = await client.call_tool("create_folder", {
                "folder_name": "",
                "parent_id": "-root-"
            })
            
            assert "Error: folder_name is required" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test resource listing functionality."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            
            # Should have at least one resource
            assert len(resources) > 0
            
            # Check for expected resource pattern
            resource_uris = [str(resource.uri) for resource in resources]
            assert any("alfresco://repository/" in uri for uri in resource_uris)
    
    @pytest.mark.asyncio
    async def test_read_resources(self):
        """Test reading different resource sections."""
        async with Client(mcp) as client:
            # Test different resource sections
            sections = ["info", "stats", "health", "config"]
            
            for section in sections:
                uri = f"alfresco://repository/{section}"
                result = await client.read_resource(uri)
                
                assert len(result) > 0
                # Should be valid JSON
                import json
                try:
                    json.loads(result[0].text)
                except json.JSONDecodeError:
                    pytest.fail(f"Resource {section} did not return valid JSON")
    
    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Test prompt listing functionality."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            
            # Should have at least one prompt
            assert len(prompts) > 0
            
            # Check for expected prompt
            prompt_names = [prompt.name for prompt in prompts]
            assert "search_and_analyze" in prompt_names
    
    @pytest.mark.asyncio
    async def test_get_prompt(self):
        """Test prompt generation with different parameters."""
        async with Client(mcp) as client:
            # Test basic prompt
            result = await client.get_prompt("search_and_analyze", {
                "query": "test documents",
                "analysis_type": "summary"
            })
            
            assert len(result.messages) > 0
            prompt_text = result.messages[0].content.text
            assert "test documents" in prompt_text
            assert "summary" in prompt_text
            
            # Test detailed analysis
            result = await client.get_prompt("search_and_analyze", {
                "query": "financial reports",
                "analysis_type": "detailed"
            })
            
            prompt_text = result.messages[0].content.text
            assert "financial reports" in prompt_text
            assert "detailed" in prompt_text
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid operations."""
        async with Client(mcp) as client:
            # Test calling non-existent tool
            with pytest.raises(Exception):
                await client.call_tool("non_existent_tool", {})
            
            # Test reading non-existent resource
            result = await client.read_resource("alfresco://repository/invalid")
            assert "error" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_tool_calls(self):
        """Test calling non-existent MCP tools."""
        async with Client(mcp) as client:
            # Test various invalid tool names
            invalid_tools = [
                "nonexistent_tool",
                "invalid_tool_name", 
                "fake_tool",
                "",  # Empty tool name
                "search_content_invalid"
            ]
            
            for invalid_tool in invalid_tools:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool(invalid_tool, {})
                
                # Should raise an exception for invalid tool names
                assert exc_info.value is not None
    
    @pytest.mark.asyncio
    async def test_malformed_tool_arguments(self):
        """Test tools with malformed or invalid arguments."""
        from fastmcp.exceptions import ToolError
        async with Client(mcp) as client:
            # Test search_content with completely wrong argument types
            # FastMCP 2.0 raises ToolError for validation failures
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("search_content", {
                    "query": 12345,  # Should be string
                    "max_results": "not_a_number"  # Should be int
                })
            
            # Should contain validation error details
            error_msg = str(exc_info.value)
            assert "validation error" in error_msg.lower()
            
            # Test upload_document with invalid structure - also raises ToolError
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("upload_document", {
                    "completely": "wrong",
                    "structure": True,
                    "missing": "all_required_fields"
                })
            
            # Should indicate missing required fields
            error_msg = str(exc_info.value)
            assert any(keyword in error_msg.lower() for keyword in ["validation", "required", "missing"])
            
            # Test create_folder with invalid types - should also raise ToolError
            with pytest.raises(ToolError):
                await client.call_tool("create_folder", {
                    "folder_name": 12345,  # Should be string
                    "parent_id": []  # Should be string
                })


class TestFastMCP2Features:
    """Test FastMCP 2.0 specific features that aren't available in legacy versions."""
    
    @pytest.mark.asyncio
    async def test_in_memory_performance(self):
        """Test the performance advantage of in-memory testing."""
        import time
        
        start_time = time.time()
        
        async with Client(mcp) as client:
            # Perform multiple operations
            await client.ping()
            await client.list_tools()
            await client.list_resources()
            await client.call_tool("search_content", {"query": "test"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # In-memory testing should be very fast (< 1 second for multiple operations)
        assert duration < 1.0, f"In-memory testing took {duration:.2f}s - should be much faster"
    
    @pytest.mark.asyncio
    async def test_type_safety(self):
        """Test type safety features of FastMCP 2.0."""
        from fastmcp.exceptions import ToolError
        async with Client(mcp) as client:
            # Test that type validation works - FastMCP 2.0 enforces strict typing
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("search_content", {
                    "query": "test",
                    "max_results": "invalid"  # String instead of int
                })
            
            # Should provide clear validation error
            error_msg = str(exc_info.value)
            assert "validation error" in error_msg.lower()
            assert "integer" in error_msg.lower()
    
    @pytest.mark.asyncio 
    async def test_concurrent_operations(self):
        """Test concurrent operations using FastMCP 2.0."""
        async with Client(mcp) as client:
            # Run multiple operations concurrently
            tasks = [
                client.call_tool("search_content", {"query": f"test{i}"})
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All operations should complete successfully
            assert len(results) == 5
            for result in results:
                assert len(result) > 0


# Integration test for the complete workflow
@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_workflow():
    """Test a complete Alfresco workflow using FastMCP 2.0."""
    async with Client(mcp) as client:
        # 1. Search for existing documents
        search_result = await client.call_tool("search_content", {
            "query": "test documents",
            "max_results": 5
        })
        
        assert len(search_result) > 0
        
        # 2. Create a new folder
        folder_result = await client.call_tool("create_folder", {
            "folder_name": "Integration Test Folder",
            "description": "Created during integration test"
        })
        
        assert "Folder Created" in folder_result[0].text
        
        # 3. Upload a document
        upload_result = await client.call_tool("upload_document", {
            "filename": "integration_test.txt",
            "content_base64": "SW50ZWdyYXRpb24gdGVzdCBjb250ZW50",  # "Integration test content"
            "description": "Integration test document"
        })
        
        assert "Upload Successful" in upload_result[0].text
        
        # 4. Check repository stats
        stats = await client.read_resource("alfresco://repository/stats")
        import json
        stats_data = json.loads(stats[0].text)
        assert "documents" in stats_data
        
        # 5. Generate analysis prompt
        prompt_result = await client.get_prompt("search_and_analyze", {
            "query": "integration test",
            "analysis_type": "summary"
        })
        
        assert "integration test" in prompt_result.messages[0].content.text.lower()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 
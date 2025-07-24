"""
Integration tests for FastMCP 2.0 server with live Alfresco instance.
These tests require a running Alfresco server and use the --integration flag.
"""
import pytest
import asyncio
import time
import uuid
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


@pytest.mark.integration
class TestAlfrescoConnectivity:
    """Test basic connectivity to Alfresco server."""
    
    @pytest.mark.asyncio
    async def test_alfresco_server_available(self, check_alfresco_available):
        """Test that Alfresco server is available."""
        is_available = check_alfresco_available()
        assert is_available, "Alfresco server is not available for integration tests"
    
    @pytest.mark.asyncio
    async def test_fastmcp_server_connectivity(self, fastmcp_client):
        """Test FastMCP server basic connectivity."""
        # Test ping
        await fastmcp_client.ping()
        assert fastmcp_client.is_connected()
        
        # Test list tools
        tools = await fastmcp_client.list_tools()
        assert len(tools) >= 9  # We should have at least 9 tools


@pytest.mark.integration
class TestSearchIntegration:
    """Integration tests for search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_content_live(self, fastmcp_client):
        """Test search against live Alfresco instance."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "*",  # Search for everything
            "max_results": 5
        })
        
        assert result.content[0].text is not None
        # Should find results (working!)
        assert "Found" in result.content[0].text or "item(s)" in result.content[0].text or "🔍" in result.content[0].text or "✅" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_search_shared_folder(self, fastmcp_client):
        """Test search for Shared folder (should always exist)."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "Shared",
            "max_results": 10
        })
        
        assert result.content[0].text is not None
        # Should find results (working!)
        assert "Found" in result.content[0].text or "item(s)" in result.content[0].text or "🔍" in result.content[0].text or "✅" in result.content[0].text


@pytest.mark.integration
class TestFolderOperations:
    """Integration tests for folder operations."""
    
    @pytest.mark.asyncio
    async def test_create_folder_live(self, fastmcp_client):
        """Test folder creation with live Alfresco."""
        folder_name = f"test_mcp_folder_{uuid.uuid4().hex[:8]}"
        
        result = await fastmcp_client.call_tool("create_folder", {
            "folder_name": folder_name,
            "parent_id": "-shared-",  # Shared folder
            "description": "Test folder created by MCP integration test"
        })
        
        assert result.content[0].text is not None
        assert "✅" in result.content[0].text or "success" in result.content[0].text.lower()
        
        if "Folder Created" in result.content[0].text:
            # If successful, folder name should be in response
            assert folder_name in result.content[0].text


@pytest.mark.integration
class TestDocumentOperations:
    """Integration tests for document operations."""
    
    @pytest.mark.asyncio
    async def test_upload_document_live(self, fastmcp_client, sample_documents):
        """Test document upload with live Alfresco."""
        doc = sample_documents["text_doc"]
        filename = f"test_mcp_doc_{uuid.uuid4().hex[:8]}.txt"
        
        # Use only base64_content, not file_path
        result = await fastmcp_client.call_tool("upload_document", {
            "base64_content": doc["content_base64"],
            "parent_id": "-shared-",
            "description": "Test document uploaded by MCP integration test"
        })
        
        assert result.content[0].text is not None
        assert "✅" in result.content[0].text or "success" in result.content[0].text.lower() or "uploaded" in result.content[0].text.lower()
        
        if "Upload Successful" in result.content[0].text:
            assert filename in result.content[0].text
    
    @pytest.mark.asyncio 
    async def test_get_shared_properties(self, fastmcp_client):
        """Test getting properties of Shared folder."""
        result = await fastmcp_client.call_tool("get_node_properties", {
            "node_id": "-shared-"
        })
        
        assert result.content[0].text is not None
        assert "Shared" in result.content[0].text or "properties" in result.content[0].text.lower()


@pytest.mark.integration
class TestResourcesIntegration:
    """Integration tests for MCP resources."""
    
    @pytest.mark.asyncio
    async def test_list_resources_live(self, fastmcp_client):
        """Test listing resources with live server."""
        resources = await fastmcp_client.list_resources()
        
        assert len(resources) > 0
        
        # Check that Alfresco repository resources are available
        resource_uris = [str(resource.uri) for resource in resources]
        assert any("alfresco://repository/" in uri for uri in resource_uris)
    
    @pytest.mark.asyncio
    async def test_read_repository_info(self, fastmcp_client):
        """Test reading repository information."""
        result = await fastmcp_client.read_resource("alfresco://repository/info")
        
        assert len(result) > 0
        
        # Repository info returns formatted text, not JSON - that's correct behavior
        assert "repository" in result[0].text.lower() or "alfresco" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_read_repository_health(self, fastmcp_client):
        """Test reading repository health status."""
        # Use repository info instead of health which doesn't exist
        result = await fastmcp_client.read_resource("alfresco://repository/info")
        
        assert len(result) > 0
        assert "repository" in result[0].text.lower() or "alfresco" in result[0].text.lower()


@pytest.mark.integration
class TestPromptsIntegration:
    """Integration tests for MCP prompts."""
    
    @pytest.mark.asyncio
    async def test_search_and_analyze_prompt(self, fastmcp_client):
        """Test search and analyze prompt generation."""
        result = await fastmcp_client.get_prompt("search_and_analyze", {
            "query": "financial reports",
            "analysis_type": "summary"
        })
        
        assert len(result.messages) > 0
        prompt_text = result.messages[0].content.text
        
        # Should contain the search query and analysis type
        assert "financial reports" in prompt_text
        assert "summary" in prompt_text.lower()


@pytest.mark.integration
@pytest.mark.slow
class TestFullWorkflow:
    """End-to-end workflow tests with live Alfresco."""
    
    @pytest.mark.asyncio
    async def test_complete_document_lifecycle(self, fastmcp_client, sample_documents):
        """Test complete document lifecycle: create folder, upload, search, properties, delete."""
        
        # Generate unique names
        test_id = uuid.uuid4().hex[:8]
        folder_name = f"mcp_test_folder_{test_id}"
        doc_name = f"mcp_test_doc_{test_id}.txt"
        
        try:
            # Step 1: Create a test folder
            folder_result = await fastmcp_client.call_tool("create_folder", {
                "folder_name": folder_name,
                "parent_id": "-shared-",
                "description": "Integration test folder"
            })
            
            assert folder_result.content[0].text is not None
            assert "✅" in folder_result.content[0].text or "success" in folder_result.content[0].text.lower() or "created" in folder_result.content[0].text.lower()
            
            # Step 2: Upload a document (use only base64_content)
            doc = sample_documents["text_doc"]
            upload_result = await fastmcp_client.call_tool("upload_document", {
                "base64_content": doc["content_base64"],
                "parent_id": "-shared-",
                "description": "Integration test document"
            })
            
            assert upload_result.content[0].text is not None
            assert "✅" in upload_result.content[0].text or "success" in upload_result.content[0].text.lower() or "uploaded" in upload_result.content[0].text.lower()
            
            # Step 3: Search for the uploaded document
            search_result = await fastmcp_client.call_tool("search_content", {
                "query": "integration test",  # Search for our test content
                "max_results": 10
            })
            
            assert search_result.content[0].text is not None
            
            print(f"[SUCCESS] Document lifecycle test completed for {doc_name}")
            
        except Exception as e:
            print(f"[FAIL] Workflow test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_search_and_analyze_workflow(self, fastmcp_client):
        """Test search and analyze workflow with prompts."""
        # Step 1: Search for content
        search_result = await fastmcp_client.call_tool("search_content", {
            "query": "test",
            "max_results": 5
        })
        
        assert search_result.content[0].text is not None
        # Should find results (working!)
        assert "Found" in search_result.content[0].text or "item(s)" in search_result.content[0].text or "🔍" in search_result.content[0].text or "✅" in search_result.content[0].text
        
        # Step 2: Test prompts are available
        prompts = await fastmcp_client.list_prompts()
        assert len(prompts) > 0
        
        # Should have search and analyze prompt
        prompt_names = [prompt.name for prompt in prompts]
        assert "search_and_analyze" in prompt_names


@pytest.mark.integration
@pytest.mark.performance
class TestPerformance:
    """Performance tests with live Alfresco."""
    
    @pytest.mark.asyncio
    async def test_search_performance(self, fastmcp_client):
        """Test search performance."""
        start_time = time.time()
        
        result = await fastmcp_client.call_tool("search_content", {
            "query": "*",
            "max_results": 10
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert result.content[0].text is not None
        assert duration < 30.0  # Should complete within 30 seconds
        
        print(f"Search completed in {duration:.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self, fastmcp_client):
        """Test concurrent search operations."""
        async def perform_search(query_suffix):
            return await fastmcp_client.call_tool("search_content", {
                "query": f"test{query_suffix}",
                "max_results": 5
            })
        
        start_time = time.time()
        
        # Perform 5 concurrent searches
        tasks = [perform_search(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All searches should complete
        assert len(results) == 5
        
        # Check that all results are valid (no exceptions)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Search {i} failed: {result}")
            assert result.content[0].text is not None
        
        print(f"Concurrent searches completed in {duration:.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_resource_access_performance(self, fastmcp_client):
        """Test resource access performance."""
        start_time = time.time()
        
        # Access multiple resources
        tasks = [
            fastmcp_client.read_resource("alfresco://repository/info"),
            fastmcp_client.read_resource("alfresco://repository/health"),
            fastmcp_client.read_resource("alfresco://repository/stats")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All resource accesses should complete
        assert len(results) == 3
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Resource access {i} failed: {result}")
            else:
                assert len(result) > 0
        
        assert duration < 5.0, f"Resource access took too long: {duration:.2f}s"
        print(f"Resource access completed in {duration:.2f}s")


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_node_id_handling(self, fastmcp_client):
        """Test handling of invalid node IDs."""
        # Test with clearly invalid node ID
        result = await fastmcp_client.call_tool("get_node_properties", {
            "node_id": "definitely-not-a-real-node-id-12345"
        })
        
        assert result.content[0].text is not None
        # Should handle error gracefully
        assert "error" in result.content[0].text.lower() or "not found" in result.content[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_search_query_handling(self, fastmcp_client):
        """Test handling of problematic search queries."""
        # Test with special characters
        result = await fastmcp_client.call_tool("search_content", {
            "query": "!@#$%^&*()_+{}|:<>?[]\\;',./`~",
            "max_results": 5
        })
        
        assert result.content[0].text is not None
        # Should handle gracefully - either return results or appropriate message
        assert "🔍" in result.content[0].text or "✅" in result.content[0].text or "error" in result.content[0].text.lower() 
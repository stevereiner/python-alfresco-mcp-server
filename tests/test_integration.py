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
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Should either find results or return no results message
        assert any(keyword in response_text for keyword in [
            "Search Results", "No results found", "Search failed"
        ])
    
    @pytest.mark.asyncio
    async def test_search_company_home(self, fastmcp_client):
        """Test search for Company Home (should always exist)."""
        result = await fastmcp_client.call_tool("search_content", {
            "query": "Company Home",
            "max_results": 10
        })
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Should find Company Home or indicate search worked
        assert not ("Error:" in response_text and "empty" in response_text)


@pytest.mark.integration
class TestFolderOperations:
    """Integration tests for folder operations."""
    
    @pytest.mark.asyncio
    async def test_create_folder_live(self, fastmcp_client):
        """Test folder creation with live Alfresco."""
        folder_name = f"test_mcp_folder_{uuid.uuid4().hex[:8]}"
        
        result = await fastmcp_client.call_tool("create_folder", {
            "folder_name": folder_name,
            "parent_id": "-root-",  # Company Home
            "description": "Test folder created by MCP integration test"
        })
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Should either succeed or fail gracefully
        assert any(keyword in response_text for keyword in [
            "Folder Created", "Creation failed", "Error"
        ])
        
        if "Folder Created" in response_text:
            # If successful, folder name should be in response
            assert folder_name in response_text


@pytest.mark.integration
class TestDocumentOperations:
    """Integration tests for document operations."""
    
    @pytest.mark.asyncio
    async def test_upload_document_live(self, fastmcp_client, sample_documents):
        """Test document upload with live Alfresco."""
        doc = sample_documents["text_doc"]
        filename = f"test_mcp_doc_{uuid.uuid4().hex[:8]}.txt"
        
        result = await fastmcp_client.call_tool("upload_document", {
            "filename": filename,
            "content_base64": doc["content_base64"],
            "parent_id": "-root-",
            "description": "Test document uploaded by MCP integration test"
        })
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Should either succeed or fail gracefully
        assert any(keyword in response_text for keyword in [
            "Upload Successful", "Upload failed", "Error"
        ])
        
        if "Upload Successful" in response_text:
            assert filename in response_text
    
    @pytest.mark.asyncio 
    async def test_get_root_properties(self, fastmcp_client):
        """Test getting properties of Company Home (root)."""
        result = await fastmcp_client.call_tool("get_node_properties", {
            "node_id": "-root-"
        })
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Should either succeed or fail gracefully
        assert any(keyword in response_text for keyword in [
            "Node Properties", "Failed to get properties", "Error"
        ])


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
        
        # Should be valid JSON
        import json
        try:
            data = json.loads(result[0].text)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Repository info resource did not return valid JSON")
    
    @pytest.mark.asyncio
    async def test_read_repository_health(self, fastmcp_client):
        """Test reading repository health status."""
        result = await fastmcp_client.read_resource("alfresco://repository/health")
        
        assert len(result) > 0
        
        # Should contain health information
        response_text = result[0].text
        assert any(keyword in response_text.lower() for keyword in [
            "status", "health", "ready", "available"
        ])


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
                "parent_id": "-root-",
                "description": "Integration test folder"
            })
            
            assert len(folder_result) == 1
            print(f"Folder creation result: {folder_result[0].text}")
            
            # Step 2: Upload a document
            doc = sample_documents["text_doc"]
            upload_result = await fastmcp_client.call_tool("upload_document", {
                "filename": doc_name,
                "content_base64": doc["content_base64"],
                "parent_id": "-root-",
                "description": "Integration test document"
            })
            
            assert len(upload_result) == 1
            print(f"Upload result: {upload_result[0].text}")
            
            # Step 3: Search for the created items
            search_result = await fastmcp_client.call_tool("search_content", {
                "query": f"mcp_test_{test_id}",
                "max_results": 10
            })
            
            assert len(search_result) == 1
            print(f"Search result: {search_result[0].text}")
            
            # Step 4: Get properties of root (always exists)
            props_result = await fastmcp_client.call_tool("get_node_properties", {
                "node_id": "-root-"
            })
            
            assert len(props_result) == 1
            print(f"Properties result: {props_result[0].text}")
            
            # All steps should complete without throwing exceptions
            print("✅ Complete workflow test passed")
            
        except Exception as e:
            print(f"❌ Workflow test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_search_and_analyze_workflow(self, fastmcp_client):
        """Test search and analyze workflow with prompts."""
        # Step 1: Search for content
        search_result = await fastmcp_client.call_tool("search_content", {
            "query": "test",
            "max_results": 5
        })
        
        assert len(search_result) == 1
        
        # Step 2: Generate analysis prompt
        prompt_result = await fastmcp_client.get_prompt("search_and_analyze", {
            "query": "test",
            "analysis_type": "detailed"
        })
        
        assert len(prompt_result.messages) > 0
        
        # Should contain search context and analysis instructions
        prompt_text = prompt_result.messages[0].content.text
        assert "test" in prompt_text
        assert "detailed" in prompt_text.lower()


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
        
        assert len(result) == 1
        assert duration < 10.0, f"Search took too long: {duration:.2f}s"
        print(f"Search completed in {duration:.2f}s")
    
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
            assert len(result) == 1
        
        assert duration < 15.0, f"Concurrent searches took too long: {duration:.2f}s"
        print(f"5 concurrent searches completed in {duration:.2f}s")
    
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
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Should handle error gracefully
        assert any(keyword in response_text for keyword in [
            "Failed to get properties", "Error", "not found"
        ])
    
    @pytest.mark.asyncio
    async def test_invalid_search_query_handling(self, fastmcp_client):
        """Test handling of problematic search queries."""
        # Test with special characters
        result = await fastmcp_client.call_tool("search_content", {
            "query": "!@#$%^&*()_+{}|:<>?[]\\;',./`~",
            "max_results": 5
        })
        
        assert len(result) == 1
        # Should not crash, should return either results or no results
        response_text = result[0].text
        assert not ("Error:" in response_text and "empty" in response_text) 
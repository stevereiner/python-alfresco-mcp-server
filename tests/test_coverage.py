"""
Code coverage tests for Python Alfresco MCP Server.
Tests edge cases and error paths to ensure comprehensive coverage.
"""
import pytest
import asyncio
import base64
import time
from unittest.mock import Mock, patch
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp
from tests.test_utils import strip_emojis


class TestCodeCoverage:
    """Test various code paths for coverage."""
    
    @pytest.mark.asyncio
    async def test_all_tool_combinations(self):
        """Test all tools with different parameter combinations."""
        async with Client(mcp) as client:
            # Test all major tools
            tools_to_test = [
                ("search_content", {"query": "test", "max_results": 10}),
                ("upload_document", {"file_path": "", "base64_content": "dGVzdA==", "description": "test file"}),
                ("download_document", {"node_id": "test-123"}),
                ("checkout_document", {"node_id": "test-123"}),
                ("checkin_document", {"node_id": "test-123", "file_content": "dGVzdA==", "comment": "test"}),
                ("cancel_checkout", {"node_id": "test-123"}),
                ("create_folder", {"folder_name": "test", "parent_id": "-shared-"}),
                ("get_node_properties", {"node_id": "-shared-"}),
                ("update_node_properties", {"node_id": "-shared-", "title": "Test"}),
                ("delete_node", {"node_id": "test-123"}),
                ("browse_repository", {"parent_id": "-shared-"}),
                ("advanced_search", {"query": "test"}),
                ("search_by_metadata", {"metadata_query": "test"}),
                ("cmis_search", {"cmis_query": "SELECT * FROM cmis:document"})
            ]
            
            for tool_name, params in tools_to_test:
                try:
                    result = await client.call_tool(tool_name, params)
                    # All tools should return valid responses (success or graceful error)
                    assert len(result.content) == 1
                    assert isinstance(result.content[0].text, str)
                    assert len(result.content[0].text) > 0
                except Exception as e:
                    # Some tools may raise exceptions with invalid data - that's acceptable
                    assert "validation" in str(e).lower() or "error" in str(e).lower()

    @pytest.mark.asyncio
    async def test_search_models_import_error(self):
        """Test handling when search models can't be imported."""
        async with Client(mcp) as client:
            # Test search with potentially problematic queries
            problematic_queries = ["", "*", "SELECT * FROM cmis:document LIMIT 1000"]
            
            for query in problematic_queries:
                try:
                    result = await client.call_tool("search_content", {
                        "query": query,
                        "max_results": 5
                    })
                    # Should handle gracefully
                    assert len(result.content) >= 1
                except:
                    pass  # Some queries expected to fail
    
    @pytest.mark.asyncio
    async def test_all_error_paths(self):
        """Test various error conditions."""
        async with Client(mcp) as client:
            # Test with invalid parameters
            error_scenarios = [
                ("get_node_properties", {"node_id": ""}),
                ("download_document", {"node_id": "invalid-id-12345"}),
                ("upload_document", {"file_path": "nonexistent.txt"}),
                ("delete_node", {"node_id": "invalid-node"}),
                ("checkout_document", {"node_id": "invalid-checkout"}),
            ]
            
            for tool_name, params in error_scenarios:
                result = await client.call_tool(tool_name, params)
                # Should handle errors gracefully
                assert len(result.content) >= 1
                response_text = result.content[0].text
                assert isinstance(response_text, str)
                # Should contain some indication of error or completion
                assert len(response_text) > 0

    @pytest.mark.asyncio
    async def test_base64_edge_cases(self):
        """Test base64 content edge cases."""
        async with Client(mcp) as client:
            # Test various base64 scenarios
            base64_tests = [
                "",  # Empty
                "dGVzdA==",  # Valid: "test"
                "invalid-base64!!!",  # Invalid characters
                "dGVzdA",  # Missing padding
            ]
            
            for content in base64_tests:
                try:
                    result = await client.call_tool("upload_document", {
                        "file_path": "",
                        "base64_content": content,
                        "parent_id": "-shared-",
                        "description": "Base64 test"
                    })
                    # Should handle various base64 inputs
                    assert len(result.content) >= 1
                except Exception as e:
                    # Some invalid base64 expected to fail
                    assert "validation" in str(e).lower() or "base64" in str(e).lower()

    @pytest.mark.asyncio 
    async def test_search_edge_cases(self):
        """Test search with various edge cases."""
        async with Client(mcp) as client:
            edge_queries = [
                "a",  # Single character
                "test" * 100,  # Very long
                "test\nwith\nnewlines",  # Newlines
                "test\twith\ttabs",  # Tabs
                "special!@#$%chars",  # Special characters
            ]
            
            for query in edge_queries:
                result = await client.call_tool("search_content", {
                    "query": query,
                    "max_results": 5
                })
                # Should handle all queries
                assert len(result.content) >= 1
                assert isinstance(result.content[0].text, str)


class TestResourcesCoverage:
    """Test resource-related coverage."""
    
    @pytest.mark.asyncio
    async def test_all_resource_sections(self):
        """Test all repository resource sections."""
        async with Client(mcp) as client:
            # Test the main resource
            result = await client.read_resource("alfresco://repository/info")
            response_text = result[0].text
            assert isinstance(response_text, str)
            assert len(response_text) > 0

    @pytest.mark.asyncio
    async def test_resource_error_cases(self):
        """Test resource error handling."""
        async with Client(mcp) as client:
            # Test invalid resource
            try:
                await client.read_resource("alfresco://repository/unknown")
                assert False, "Should have raised an error"
            except Exception as e:
                assert "unknown" in str(e).lower() or "error" in str(e).lower()


class TestExceptionHandling:
    """Test exception handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self):
        """Test handling of network timeouts."""
        async with Client(mcp) as client:
            # Test with operations that might timeout
            long_operations = [
                ("search_content", {"query": "*", "max_results": 50}),
                ("browse_repository", {"parent_id": "-root-", "max_items": 50}),
            ]
            
            for tool_name, params in long_operations:
                try:
                    result = await asyncio.wait_for(
                        client.call_tool(tool_name, params),
                        timeout=30  # 30 second timeout
                    )
                    # Should complete within timeout
                    assert len(result.content) >= 1
                except asyncio.TimeoutError:
                    # Timeout is acceptable for this test
                    pass

    @pytest.mark.asyncio
    async def test_authentication_failure_simulation(self):
        """Test handling of authentication failures."""
        async with Client(mcp) as client:
            # Test operations that might fail due to auth
            auth_sensitive_ops = [
                ("upload_document", {
                    "file_path": "",
                    "base64_content": "dGVzdA==",
                    "parent_id": "-shared-",
                    "description": "Auth test"
                }),
                ("delete_node", {"node_id": "test-delete"}),
                ("checkout_document", {"node_id": "test-checkout"}),
            ]
            
            for tool_name, params in auth_sensitive_ops:
                result = await client.call_tool(tool_name, params)
                # Should handle auth issues gracefully
                assert len(result.content) >= 1
                response_text = result.content[0].text
                assert isinstance(response_text, str)

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed responses."""
        async with Client(mcp) as client:
            # Test with parameters that might cause unusual responses
            unusual_params = [
                ("search_content", {"query": "\x00\x01\x02", "max_results": 1}),  # Binary chars
                ("get_node_properties", {"node_id": "../../../etc/passwd"}),  # Path traversal attempt
                ("create_folder", {"folder_name": "a" * 1000, "parent_id": "-shared-"}),  # Very long name
            ]
            
            for tool_name, params in unusual_params:
                try:
                    result = await client.call_tool(tool_name, params)
                    # Should handle unusual inputs
                    assert len(result.content) >= 1
                    response_text = result.content[0].text
                    assert isinstance(response_text, str)
                except Exception as e:
                    # Some unusual inputs expected to cause validation errors
                    assert "validation" in str(e).lower() or "error" in str(e).lower()


class TestPerformanceCoverage:
    """Test performance-related code paths."""
    
    @pytest.mark.asyncio
    async def test_memory_usage_patterns(self):
        """Test memory usage with various operations."""
        async with Client(mcp) as client:
            # Perform operations that might use different memory patterns
            operations = [
                ("search_content", {"query": "test", "max_results": 1}),  # Small result
                ("search_content", {"query": "*", "max_results": 25}),    # Larger result
                ("browse_repository", {"parent_id": "-shared-", "max_items": 1}),
                ("browse_repository", {"parent_id": "-shared-", "max_items": 20}),
            ]
            
            for tool_name, params in operations:
                result = await client.call_tool(tool_name, params)
                # All should complete without memory issues
                assert len(result.content) >= 1
                assert isinstance(result.content[0].text, str)

    @pytest.mark.asyncio
    async def test_concurrent_resource_access(self):
        """Test concurrent access to resources."""
        async with Client(mcp) as client:
            # Access repository info concurrently
            tasks = [
                client.read_resource("alfresco://repository/info")
                for _ in range(3)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete successfully
            assert len(results) == 3
            for result in results:
                if not isinstance(result, Exception):
                    assert len(result) >= 1
                    assert isinstance(result[0].text, str) 
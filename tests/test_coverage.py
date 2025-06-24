"""
Code coverage tests for Alfresco MCP Server.
These tests ensure maximum code coverage by testing edge cases and error paths.
"""
import pytest
import os
import tempfile
from unittest.mock import patch, Mock, AsyncMock
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


@pytest.mark.unit
class TestCodeCoverage:
    """Tests designed to maximize code coverage."""
    
    @pytest.mark.asyncio
    async def test_ensure_connection_success(self, fastmcp_client):
        """Test ensure_connection function success path."""
        with patch('alfresco_mcp_server.fastmcp_server.alfresco_factory', None), \
             patch('alfresco_mcp_server.fastmcp_server.auth_util', None), \
             patch('alfresco_mcp_server.config.AlfrescoConfig') as mock_config_class, \
             patch('python_alfresco_api.client_factory.ClientFactory') as mock_factory_class, \
             patch('python_alfresco_api.auth_util.AuthUtil') as mock_auth_class:
            
            # Setup mocks
            mock_config = Mock()
            mock_config.alfresco_url = "http://localhost:8080"
            mock_config.username = "admin"
            mock_config.password = "admin"
            mock_config.verify_ssl = False
            mock_config.timeout = 30
            mock_config_class.return_value = mock_config
            
            mock_factory = Mock()
            mock_factory_class.return_value = mock_factory
            
            mock_auth = AsyncMock()
            mock_auth_class.return_value = mock_auth
            
            # Import and call ensure_connection 
            from alfresco_mcp_server.fastmcp_server import ensure_connection
            
            # The function should complete without error when mocks are set up
            try:
                await ensure_connection()
                # If we get here, the function completed successfully
                assert True
            except Exception as e:
                # Should not raise an exception with proper mocks
                pytest.fail(f"ensure_connection raised unexpected exception: {e}")
    
    @pytest.mark.asyncio
    async def test_ensure_connection_already_initialized(self, fastmcp_client):
        """Test ensure_connection when already initialized."""
        with patch('alfresco_mcp_server.fastmcp_server.alfresco_factory', Mock()), \
             patch('alfresco_mcp_server.fastmcp_server.auth_util', Mock()):
            
            from alfresco_mcp_server.fastmcp_server import ensure_connection
            
            # Should return early since factory and auth_util are set
            await ensure_connection()
            # No exception should be raised
    
    @pytest.mark.asyncio
    async def test_search_models_import_error(self, fastmcp_client):
        """Test search functionality when search models can't be imported."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory, \
             patch('alfresco_mcp_server.fastmcp_server.search_models', None):
            
            search_client = AsyncMock()
            mock_factory.create_search_client.return_value = search_client
            
            # This should handle the case where search_models is None
            result = await fastmcp_client.call_tool("search_content", {
                "query": "test",
                "max_results": 10
            })
            
            assert len(result) == 1
            # Should handle gracefully
    
    @pytest.mark.asyncio
    async def test_all_error_paths(self, fastmcp_client):
        """Test error paths in all tools to maximize coverage."""
        
        # Test each tool with connection failure
        tools_to_test = [
            ("search_content", {"query": "test", "max_results": 10}),
            ("upload_document", {"filename": "test.txt", "content_base64": "dGVzdA=="}),
            ("download_document", {"node_id": "test-123"}),
            ("checkout_document", {"node_id": "test-123"}),
            ("checkin_document", {"node_id": "test-123"}),
            ("delete_node", {"node_id": "test-123"}),
            ("get_node_properties", {"node_id": "test-123"}),
            ("update_node_properties", {"node_id": "test-123", "name": "new_name"}),
            ("create_folder", {"folder_name": "Test Folder"})
        ]
        
        for tool_name, args in tools_to_test:
            with patch('alfresco_mcp_server.fastmcp_server.ensure_connection',
                      side_effect=Exception("Connection error")):
                
                result = await fastmcp_client.call_tool(tool_name, args)
                assert len(result) == 1
                assert any(keyword in result[0].text for keyword in [
                    "failed", "Error", "error"
                ])
    
    @pytest.mark.asyncio
    async def test_base64_edge_cases(self, fastmcp_client):
        """Test base64 handling edge cases."""
        # Test various invalid base64 strings
        invalid_base64_cases = [
            "not_base64_at_all",
            "invalid base64 with spaces",
            "YWJjZA===",  # Too many padding characters
            "",  # Empty string
            "x",  # Too short
        ]
        
        for invalid_b64 in invalid_base64_cases:
            result = await fastmcp_client.call_tool("upload_document", {
                "filename": "test.txt",
                "content_base64": invalid_b64
            })
            
            # Should handle gracefully
            assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_search_edge_cases(self, fastmcp_client):
        """Test search with various edge case inputs."""
        edge_cases = [
            {"query": " ", "max_results": 10},  # Whitespace only
            {"query": "test", "max_results": 1},  # Minimum results
            {"query": "test", "max_results": 100},  # Maximum results
            {"query": "a" * 1000, "max_results": 10},  # Very long query
        ]
        
        for case in edge_cases:
            result = await fastmcp_client.call_tool("search_content", case)
            assert len(result) == 1
            # Should not crash


@pytest.mark.unit
class TestResourcesCoverage:
    """Tests for resource functionality coverage."""
    
    @pytest.mark.asyncio
    async def test_all_resource_sections(self, fastmcp_client):
        """Test all supported resource sections."""
        sections = ["info", "health", "stats", "config"]
        
        for section in sections:
            uri = f"alfresco://repository/{section}"
            result = await fastmcp_client.read_resource(uri)
            
            assert len(result) > 0
            # Should return valid JSON
            import json
            try:
                data = json.loads(result[0].text)
                assert isinstance(data, dict)
            except json.JSONDecodeError:
                pytest.fail(f"Resource {section} did not return valid JSON")
    
    @pytest.mark.asyncio
    async def test_resource_error_cases(self, fastmcp_client):
        """Test resource error handling."""
        # Test unknown section
        with patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory, \
             patch('alfresco_mcp_server.fastmcp_server.auth_util') as mock_auth:
            
            mock_auth.is_authenticated.return_value = False
            
            result = await fastmcp_client.read_resource("alfresco://repository/unknown")
            assert len(result) > 0
            # Should handle unknown section gracefully


@pytest.mark.unit
class TestPromptsCoverage:
    """Tests for prompt functionality coverage."""
    
    @pytest.mark.asyncio
    async def test_prompt_all_analysis_types(self, fastmcp_client):
        """Test prompt with all analysis types."""
        analysis_types = ["summary", "detailed", "trends", "compliance"]
        
        for analysis_type in analysis_types:
            result = await fastmcp_client.get_prompt("search_and_analyze", {
                "query": "test documents",
                "analysis_type": analysis_type
            })
            
            assert len(result.messages) > 0
            prompt_text = result.messages[0].content.text
            assert "test documents" in prompt_text
            assert analysis_type in prompt_text.lower()
    
    @pytest.mark.asyncio
    async def test_prompt_edge_cases(self, fastmcp_client):
        """Test prompt with edge case inputs."""
        edge_cases = [
            {"query": "", "analysis_type": "summary"},  # Empty query
            {"query": "test", "analysis_type": ""},  # Empty analysis type
            {"query": "a" * 500, "analysis_type": "summary"},  # Very long query
        ]
        
        for case in edge_cases:
            result = await fastmcp_client.get_prompt("search_and_analyze", case)
            assert len(result.messages) > 0
            # Should handle gracefully


@pytest.mark.unit
class TestConfigurationCoverage:
    """Tests for configuration and environment handling."""
    
    def test_config_environment_variables(self):
        """Test configuration with various environment variable combinations."""
        with patch.dict(os.environ, {
            'ALFRESCO_URL': 'http://test:8080',
            'ALFRESCO_USERNAME': 'testuser',
            'ALFRESCO_PASSWORD': 'testpass',
            'ALFRESCO_VERIFY_SSL': 'true',
            'ALFRESCO_TIMEOUT': '60'
        }):
            from alfresco_mcp_server.config import AlfrescoConfig
            config = AlfrescoConfig()
            
            assert config.alfresco_url == 'http://test:8080'
            assert config.username == 'testuser'
            assert config.password == 'testpass'
            assert config.verify_ssl == True
            assert config.timeout == 60
    
    def test_config_defaults(self):
        """Test configuration with default values."""
        # Clear environment variables by removing them completely
        env_vars = ['ALFRESCO_URL', 'ALFRESCO_USERNAME', 'ALFRESCO_PASSWORD', 
                   'ALFRESCO_VERIFY_SSL', 'ALFRESCO_TIMEOUT']
        
        # Remove variables instead of setting to empty string
        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars:
                os.environ.pop(var, None)
                
            from alfresco_mcp_server.config import AlfrescoConfig
            config = AlfrescoConfig()
            
            # Should use defaults
            assert config.alfresco_url == 'http://localhost:8080'
            assert config.username == 'admin'
            assert config.password == 'admin'
            assert config.verify_ssl == False
            assert config.timeout == 30


@pytest.mark.unit
class TestMainEntryPoint:
    """Tests for main entry points and CLI handling."""
    
    def test_main_function_coverage(self):
        """Test main function argument parsing."""
        from alfresco_mcp_server.fastmcp_server import main
        
        # Test with different argument combinations
        test_args = [
            [],
            ['--transport', 'stdio'],
            ['--transport', 'http', '--port', '8001'],
            ['--log-level', 'DEBUG'],
        ]
        
        for args in test_args:
            with patch('sys.argv', ['fastmcp_server.py'] + args), \
                 patch('alfresco_mcp_server.fastmcp_server.mcp.run') as mock_run:
                
                try:
                    main()
                    mock_run.assert_called_once()
                except SystemExit:
                    # Expected for help or invalid args
                    pass


@pytest.mark.unit
class TestAsyncContextManagers:
    """Tests for async context managers and cleanup."""
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test FastMCP client context manager."""
        # Test that client properly connects and disconnects
        async with Client(mcp) as client:
            assert client.is_connected()
            
            # Test basic functionality
            tools = await client.list_tools()
            assert len(tools) >= 9
        
        # Client should be disconnected after context
        # Note: FastMCP handles this internally


@pytest.mark.unit
class TestExceptionHandling:
    """Tests for comprehensive exception handling."""
    
    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self, fastmcp_client):
        """Test handling of network timeouts."""
        import asyncio
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection',
                  side_effect=asyncio.TimeoutError("Network timeout")):
            
            result = await fastmcp_client.call_tool("search_content", {
                "query": "test",
                "max_results": 10
            })
            
            assert len(result) == 1
            assert "failed" in result[0].text.lower()
    
    @pytest.mark.asyncio 
    async def test_authentication_failure_simulation(self, fastmcp_client):
        """Test handling of authentication failures."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection',
                  side_effect=Exception("Authentication failed")):
            
            result = await fastmcp_client.call_tool("get_node_properties", {
                "node_id": "test-123"
            })
            
            assert len(result) == 1
            assert "failed" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, fastmcp_client):
        """Test handling of malformed Alfresco responses."""
        with patch('alfresco_mcp_server.fastmcp_server.ensure_connection'), \
             patch('alfresco_mcp_server.fastmcp_server.alfresco_factory') as mock_factory:
            
            # Setup mock to return malformed data
            search_client = AsyncMock()
            search_client.search.return_value = "not a proper response object"
            mock_factory.create_search_client.return_value = search_client
            
            result = await fastmcp_client.call_tool("search_content", {
                "query": "test",
                "max_results": 10
            })
            
            assert len(result) == 1
            # Should handle gracefully without crashing 
"""
Pytest configuration and shared fixtures for Alfresco MCP Server tests.
Provides configuration for unit tests, integration tests, and code coverage.
"""
import pytest
import pytest_asyncio
import asyncio
import os
import httpx
import tempfile
import shutil
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock, patch

# Test markers
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, mocked)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires live Alfresco)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_alfresco_factory():
    """Mock Alfresco client factory for unit tests."""
    factory = MagicMock()
    
    # Mock search client
    search_client = AsyncMock()
    search_client.search = AsyncMock()
    factory.create_search_client.return_value = search_client
    
    # Mock core client  
    core_client = AsyncMock()
    core_client.get_node = AsyncMock()
    core_client.create_node = AsyncMock()
    core_client.update_node = AsyncMock()
    core_client.delete_node = AsyncMock()
    core_client.get_node_content = AsyncMock()
    factory.create_core_client.return_value = core_client
    
    return factory


@pytest.fixture
def mock_auth_util():
    """Mock authentication utility for unit tests."""
    auth_util = AsyncMock()
    auth_util.ensure_authenticated = AsyncMock()
    auth_util.get_auth_headers = AsyncMock(return_value={"Authorization": "Bearer mock-token"})
    auth_util.is_authenticated.return_value = True
    return auth_util


@pytest_asyncio.fixture
async def fastmcp_client():
    """FastMCP in-memory client for testing."""
    from fastmcp import Client
    from alfresco_mcp_server.fastmcp_server import mcp
    
    async with Client(mcp) as client:
        yield client


@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client for integration tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def alfresco_config():
    """Alfresco configuration for tests."""
    return {
        "url": os.getenv("ALFRESCO_URL", "http://localhost:8080"),
        "username": os.getenv("ALFRESCO_USERNAME", "admin"),
        "password": os.getenv("ALFRESCO_PASSWORD", "admin"),
        "verify_ssl": os.getenv("ALFRESCO_VERIFY_SSL", "false").lower() == "true"
    }


@pytest.fixture
def sample_documents():
    """Sample document data for testing."""
    import base64
    
    return {
        "text_doc": {
            "filename": "test_document.txt",
            "content": "This is a test document for MCP server testing.",
            "content_base64": base64.b64encode(
                "This is a test document for MCP server testing.".encode()
            ).decode(),
            "mime_type": "text/plain"
        },
        "json_doc": {
            "filename": "test_data.json",
            "content": '{"test": "data", "numbers": [1, 2, 3]}',
            "content_base64": base64.b64encode(
                '{"test": "data", "numbers": [1, 2, 3]}'.encode()
            ).decode(),
            "mime_type": "application/json"
        }
    }


@pytest.fixture
def mock_search_results():
    """Mock search results for testing."""
    from types import SimpleNamespace
    
    def create_mock_entry(name, node_id, is_folder=False):
        entry = SimpleNamespace()
        entry.entry = SimpleNamespace()
        entry.entry.name = name
        entry.entry.id = node_id
        entry.entry.isFolder = is_folder
        entry.entry.modifiedAt = "2024-01-15T10:30:00Z"
        entry.entry.createdByUser = {"displayName": "Test User"}
        entry.entry.content = {"sizeInBytes": 1024} if not is_folder else None
        entry.entry.path = {"name": "/Company Home/Test"}
        return entry
    
    results = SimpleNamespace()
    results.list = SimpleNamespace()
    results.list.entries = [
        create_mock_entry("Test Document 1.pdf", "doc-123", False),
        create_mock_entry("Test Folder", "folder-456", True),
        create_mock_entry("Test Document 2.txt", "doc-789", False)
    ]
    
    return results


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--integration"):
        # Only run integration tests
        skip_unit = pytest.mark.skip(reason="Integration test run - skipping unit tests")
        for item in items:
            if "integration" not in item.keywords:
                item.add_marker(skip_unit)
    else:
        # Skip integration tests by default
        skip_integration = pytest.mark.skip(reason="Integration tests require --integration flag")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires live Alfresco server)"
    )
    parser.addoption(
        "--performance",
        action="store_true", 
        default=False,
        help="Run performance benchmarks"
    )


@pytest.fixture
def check_alfresco_available(alfresco_config):
    """Check if Alfresco server is available for integration tests."""
    def _check():
        try:
            response = httpx.get(
                f"{alfresco_config['url']}/alfresco/api/-default-/public/alfresco/versions/1/probes/-ready-",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False
    
    return _check 
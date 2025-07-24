"""
Connection utilities for Alfresco MCP Server.
Handles client creation and connection management.
"""
import logging
import os
from typing import Optional


logger = logging.getLogger(__name__)

# Global connection cache
_master_client = None
_client_factory = None

def get_alfresco_config() -> dict:
    """Get Alfresco configuration from environment variables."""
    return {
        'alfresco_url': os.getenv('ALFRESCO_URL', 'http://localhost:8080'),
        'username': os.getenv('ALFRESCO_USERNAME', 'admin'),
        'password': os.getenv('ALFRESCO_PASSWORD', 'admin'),
        'verify_ssl': os.getenv('ALFRESCO_VERIFY_SSL', 'false').lower() == 'true',
        'timeout': int(os.getenv('ALFRESCO_TIMEOUT', '30'))
    }


async def ensure_connection():
    """Ensure we have a working connection to Alfresco using python-alfresco-api."""
    global _master_client, _client_factory
    
    if _master_client is None:
        try:
            # Import here to avoid circular imports
            from python_alfresco_api import ClientFactory
            
            config = get_alfresco_config()
            
            logger.info(">> Creating Alfresco clients...")
            
            # Use ClientFactory to create authenticated client (original Sunday pattern)
            factory = ClientFactory(
                base_url=config['alfresco_url'],
                username=config['username'],
                password=config['password'],
                verify_ssl=config['verify_ssl'],
                timeout=config['timeout']
            )
            
            # Store the factory globally for other functions to use
            _client_factory = factory
            
            _master_client = factory.create_master_client()
            logger.info("Master client created successfully")
                        
            # Test connection - use method that initializes and gets
            try:
                # Use ensure_httpx_client to initialize, then test simple call
                _master_client.core.ensure_httpx_client()
                logger.info("Connection test successful!")
            except Exception as conn_error:
                logger.warning(f"Connection test failed: {conn_error}")
            
        except Exception as e:
            logger.error(f"ERROR: Failed to create clients: {str(e)}")
            raise e
    
    return _master_client


def get_connection():
    """Get the cached connection without async (for sync operations)."""
    return _master_client


async def get_search_client():
    """Get the search client for search operations (using master_client for auth compatibility)."""
    master_client = await ensure_connection()
    # Return master_client which has simple_search access and working authentication
    return master_client


async def get_core_client():
    """Get the core client for core operations (using master_client for auth compatibility)."""
    master_client = await ensure_connection()
    # Return the actual core client that has nodes, folders, etc.
    return master_client.core


async def get_client_factory():
    """Get the client factory for advanced operations."""
    await ensure_connection()
    if not _client_factory:
        raise RuntimeError("Connection not initialized. Call ensure_connection() first.")
    return _client_factory


def get_search_utils():
    """Get the search_utils module from python-alfresco-api."""
    try:
        from python_alfresco_api.utils import search_utils
        return search_utils
    except ImportError as e:
        logger.error(f"Failed to import search_utils: {e}")
        raise


def get_node_utils():
    """Get the node_utils module from python-alfresco-api."""
    try:
        from python_alfresco_api.utils import node_utils
        return node_utils
    except ImportError as e:
        logger.error(f"Failed to import node_utils: {e}")
        raise
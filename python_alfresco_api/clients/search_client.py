from typing import Dict, Any, Optional

class AlfrescoSearchClient:
    """
    Individual client for Alfresco SEARCH API.

    Features:
    - Uses generated HTTP client internally
    - Automatic authentication with AuthUtil
    - Pydantic model integration
    - Both sync and async methods
    """

    def __init__(
        self,
        base_url: str,
        auth_util: Optional[Any] = None,
        verify_ssl: bool = True,
        timeout: int = 30
    ):
        """
        Initialize search client.

        Args:
            base_url: Base URL of Alfresco instance
            auth_util: Optional AuthUtil instance for authentication
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.auth_util = auth_util
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        # Initialize the generated client
        self._init_generated_client()

    def _init_generated_client(self) -> None:
        """Initialize the generated HTTP client"""
        try:
            from python_alfresco_api.raw_clients.alfresco_search_client.search_client.client import Client
            self.client = Client(base_url=self.base_url)
            self._client_available = True
        except ImportError as e:
            print(f"Generated client not available for search: {e}")
            self.client = None
            self._client_available = False

    def is_available(self) -> bool:
        """Check if the generated client is available"""
        return self._client_available

    async def _ensure_auth(self) -> None:
        """Ensure authentication before API calls"""
        if self.auth_util:
            await self.auth_util.ensure_authenticated()

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about this client"""
        return {
            "api": "search",
            "base_url": self.base_url,
            "authenticated": self.auth_util.is_authenticated() if self.auth_util else False,
            "client_available": self._client_available
        }

    async def search(self, search_request):
        """
        Perform search using the raw client.
        
        Args:
            search_request: SearchRequest object
            
        Returns:
            Search results
        """
        await self._ensure_auth()
        
        try:
            # Import the raw client search function
            from python_alfresco_api.raw_clients.alfresco_search_client.search_client.api.search.search import sync as search_sync
            
            # Get auth headers if available
            headers = {}
            if self.auth_util:
                headers = await self.auth_util.get_auth_headers()
            
            # Set up client with headers
            client_with_auth = self.client.with_headers(headers)
            
            # Call the raw search function
            response = search_sync(client=client_with_auth, body=search_request)
            return response
            
        except Exception as e:
            raise Exception(f"Search failed: {e}") 
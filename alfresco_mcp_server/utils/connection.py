"""
Connection utilities for Alfresco MCP Server.
Handles client creation and connection management.
"""
import contextvars
import hashlib
import logging
import os
from typing import Optional


logger = logging.getLogger(__name__)

# Shared service-account connection (used only when caller passthrough is off).
_master_client = None
_client_factory = None

# Request/task-local connection. Never cache an authenticated user's client
# globally or use a privileged service-account client as a fallback.
_caller_session = contextvars.ContextVar("alfresco_caller_session", default=None)


def _caller_passthrough_enabled() -> bool:
    return os.getenv("ALFRESCO_AUTH_USE_CALLER_TOKEN", "false").lower() == "true"


def _get_caller_bearer() -> str:
    """Read the *validated* FastMCP access token of the current MCP request.

    The caller must have passed MCP JWT authentication first. We do not
    retrieve an unverified Authorization header from an arbitrary request.
    """
    if os.getenv("MCP_TRANSPORT_AUTH", "false").lower() != "true":
        raise PermissionError("Per-user bearer passthrough requires MCP_TRANSPORT_AUTH=true")
    try:
        from fastmcp.server.dependencies import get_access_token
        verified = get_access_token()
    except (ImportError, RuntimeError, LookupError):
        verified = None
    raw_token = getattr(verified, "token", None)
    if not isinstance(raw_token, str) or not raw_token:
        raise PermissionError("No validated user access token for this MCP request")
    return raw_token


def _ensure_caller_connection():
    """Construct/isolate an Alfresco client per authenticated MCP identity."""
    from python_alfresco_api import ClientFactory

    config = get_alfresco_config()
    if config["auth_method"] != "oauth2":
        raise RuntimeError("Caller bearer passthrough requires ALFRESCO_AUTH_METHOD=oauth2")
    bearer = _get_caller_bearer()
    # Only a hash is retained for matching a session within the current task.
    key = hashlib.sha256(bearer.encode("utf-8")).hexdigest()
    cached = _caller_session.get()
    if cached is not None and cached[0] == key:
        return cached[2]

    # Do not hand a caller's token to a utility with service-account client
    # credentials or refresh tokens: on expiry it must fail, not escalate.
    caller_config = dict(config)
    caller_config["oauth2"] = dict(config["oauth2"])
    caller_config["oauth2"].update({
        "access_token": bearer,
        "refresh_token": None,
        "client_secret": None,
        "token_endpoint": None,
        "grant_type": "refresh_token",
    })
    auth_util = _build_auth_util(caller_config)
    factory = ClientFactory(
        base_url=config["alfresco_url"],
        auth_util=auth_util,
        verify_ssl=config["verify_ssl"],
        timeout=config["timeout"],
    )
    master = factory.create_master_client()
    master.core.ensure_httpx_client()
    _caller_session.set((key, factory, master))
    return master


def get_alfresco_config() -> dict:
    """Get Alfresco configuration from environment variables."""
    return {
        'alfresco_url': os.getenv('ALFRESCO_URL', 'http://localhost:8080'),
        'auth_method': os.getenv('ALFRESCO_AUTH_METHOD', 'basic').lower(),  # basic | ticket | oauth2
        'username': os.getenv('ALFRESCO_USERNAME', 'admin'),
        'password': os.getenv('ALFRESCO_PASSWORD', 'admin'),
        # A login ticket obtained elsewhere. With auth_method=ticket this replaces
        # username/password entirely instead of being fetched from them.
        'ticket': os.getenv('ALFRESCO_TICKET', ''),
        'verify_ssl': os.getenv('ALFRESCO_VERIFY_SSL', 'true').lower() == 'true',
        'timeout': int(os.getenv('ALFRESCO_TIMEOUT', '30')),
        'oauth2': {
            'client_id': os.getenv('ALFRESCO_OAUTH2_CLIENT_ID'),
            'client_secret': os.getenv('ALFRESCO_OAUTH2_CLIENT_SECRET'),
            'token_endpoint': os.getenv('ALFRESCO_OAUTH2_TOKEN_ENDPOINT'),
            'grant_type': os.getenv('ALFRESCO_OAUTH2_GRANT_TYPE', 'client_credentials'),
            'scope': os.getenv('ALFRESCO_OAUTH2_SCOPE'),
            'access_token': os.getenv('ALFRESCO_OAUTH2_ACCESS_TOKEN'),
            'refresh_token': os.getenv('ALFRESCO_OAUTH2_REFRESH_TOKEN'),
        },
    }


def _build_auth_util(config: dict):
    """Build a python-alfresco-api auth util for the configured auth_method.

    Returns None for basic auth (ClientFactory builds its own from username/password).
    - ticket: either a caller-supplied login ticket (ALFRESCO_TICKET) used as-is, or one
      TicketAuthUtil self-fetches from username/password. Either way the wire format is
      Authorization: Basic base64(ticket).
    - oauth2: OAuth2AuthUtil (client_credentials/refresh, or a pre-obtained access_token → Bearer),
      e.g. against Alfresco Identity Service / Keycloak.
    """
    method = config.get('auth_method', 'basic')
    if method == 'ticket':
        from python_alfresco_api.auth_util import TicketAuthUtil
        ticket = config.get('ticket')
        if ticket:
            logger.info(">> Using Alfresco ticket authentication (caller-supplied ticket)")
            return TicketAuthUtil(
                base_url=config['alfresco_url'], ticket=ticket,
                verify_ssl=config['verify_ssl'], timeout=config['timeout'],
            )
        logger.info(">> Using Alfresco ticket authentication (acquired from username/password)")
        return TicketAuthUtil(
            config['username'], config['password'],
            base_url=config['alfresco_url'],
            verify_ssl=config['verify_ssl'], timeout=config['timeout'],
        )
    if method == 'oauth2':
        from python_alfresco_api.auth_util import OAuth2AuthUtil
        o = config.get('oauth2', {}) or {}
        logger.info(">> Using Alfresco OAuth2 (Bearer) authentication")
        return OAuth2AuthUtil(
            base_url=config['alfresco_url'],
            client_id=o.get('client_id', ''),
            client_secret=o.get('client_secret'),
            token_endpoint=o.get('token_endpoint'),
            grant_type=o.get('grant_type', 'client_credentials'),
            scope=o.get('scope'),
            access_token=o.get('access_token'),
            refresh_token=o.get('refresh_token'),
            verify_ssl=config['verify_ssl'], timeout=config['timeout'],
            load_env=False,
        )
    return None  # basic


async def ensure_connection():
    """Ensure we have a working connection to Alfresco using python-alfresco-api."""
    global _master_client, _client_factory

    if _caller_passthrough_enabled():
        return _ensure_caller_connection()

    if _master_client is None:
        try:
            # Import here to avoid circular imports
            from python_alfresco_api import ClientFactory
            
            config = get_alfresco_config()
            
            logger.info(f">> Creating Alfresco clients (auth_method={config['auth_method']})...")

            # Build the auth util for the configured method; basic -> None (factory uses user/pass).
            auth_util = _build_auth_util(config)
            if auth_util is not None:
                factory = ClientFactory(
                    base_url=config['alfresco_url'],
                    auth_util=auth_util,
                    verify_ssl=config['verify_ssl'],
                    timeout=config['timeout']
                )
            else:
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
    """Get the appropriate cached connection for the current identity."""
    if _caller_passthrough_enabled():
        session = _caller_session.get()
        return session[2] if session else None
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
    if _caller_passthrough_enabled():
        session = _caller_session.get()
        if session is None:
            raise RuntimeError("No authenticated caller's Alfresco client")
        return session[1]
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
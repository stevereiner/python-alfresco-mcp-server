"""
MCP Server for Alfresco using FastMCP 3
Modular implementation with separated concerns and self-contained tools
"""
import logging
import os
from fastmcp import FastMCP, Context

# Search tools imports
from .tools.search.search_content import search_content_impl
from .tools.search.advanced_search import advanced_search_impl
from .tools.search.search_by_metadata import search_by_metadata_impl
from .tools.search.cmis_search import cmis_search_impl

# Core tools imports
from .tools.core.browse_repository import browse_repository_impl
from .tools.core.upload_document import upload_document_impl
from .tools.core.download_document import download_document_impl
from .tools.core.create_folder import create_folder_impl
from .tools.core.get_node_properties import get_node_properties_impl
from .tools.core.update_node_properties import update_node_properties_impl
from .tools.core.delete_node import delete_node_impl
from .tools.core.checkout_document import checkout_document_impl
from .tools.core.checkin_document import checkin_document_impl
from .tools.core.cancel_checkout import cancel_checkout_impl

# Runtime discovery is provider-driven; importing does not call Alfresco.
from .tools.runtime_discovery import (
    list_alfresco_operations_impl,
    describe_alfresco_operation_impl,
    invoke_alfresco_operation_impl,
    refresh_alfresco_discovery_impl,
)

# Resource imports
from .resources.repository_resources import (
    get_repository_info_impl
)

# Prompt imports
from .prompts.search_and_analyze import search_and_analyze_impl

# Configure logging
logging.basicConfig(level=logging.INFO)

# Reduce verbosity of noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def _build_transport_auth():
    """Optionally secure the MCP transport itself with OAuth2/JWT bearer validation.

    Enabled by env MCP_TRANSPORT_AUTH=true (applies to HTTP/SSE transports only; stdio ignores
    it). Validates RS256 bearer tokens from an OIDC IdP (e.g. Keycloak) via its JWKS; a client
    (including MCP Inspector) must send `Authorization: Bearer <token>`. Defaults target the local
    Keycloak realm used for Alfresco identity-service.

    NOTE: this is a DISTINCT layer from how the server authenticates TO Alfresco
    (ALFRESCO_AUTH_METHOD / ALFRESCO_OAUTH2_*) — this one gates who may call the MCP server.
    """
    if os.getenv("MCP_TRANSPORT_AUTH", "false").strip().lower() not in ("1", "true", "yes", "on"):
        return None
    from fastmcp.server.auth.providers.jwt import JWTVerifier
    jwks_uri = os.getenv(
        "MCP_AUTH_JWKS_URI",
        "http://host.docker.internal:8091/realms/alfresco/protocol/openid-connect/certs",
    )
    # The MCP SDK enforces HTTPS for the issuer URL (localhost/127.0.0.1 excepted). Our local
    # Keycloak issues an http://host.docker.internal issuer, which the SDK rejects — so by default
    # we leave issuer unset (token signature is still verified against the JWKS, so only genuine
    # Keycloak-signed tokens pass; the iss claim just isn't additionally checked). With an HTTPS
    # IdP in production, set MCP_AUTH_ISSUER to enable strict issuer validation.
    issuer = os.getenv("MCP_AUTH_ISSUER") or None
    audience = os.getenv("MCP_AUTH_AUDIENCE") or None  # unset = don't validate aud
    logger.info(f">> MCP transport auth ENABLED (jwks_uri={jwks_uri}, issuer={issuer}, audience={audience})")
    return JWTVerifier(jwks_uri=jwks_uri, issuer=issuer, audience=audience)


# Initialize MCP server (optionally with transport-level OAuth2/JWT bearer auth)
mcp = FastMCP("MCP Server for Alfresco Content Services", auth=_build_transport_auth())

# ================== RUNTIME ALFRESCO API DISCOVERY ==================

@mcp.tool
async def list_alfresco_operations(
    query: str = "", source: str = "", refresh: bool = False
) -> dict:
    """List currently discovered Alfresco operations (read-only discovery)."""
    return await list_alfresco_operations_impl(query, source, refresh)


@mcp.tool
async def describe_alfresco_operation(operation_id: str) -> dict:
    """Inspect a discovered operation and its known parameter contract."""
    return await describe_alfresco_operation_impl(operation_id)


@mcp.tool
async def invoke_alfresco_operation(
    operation_id: str, arguments: dict | None = None
) -> dict:
    """Invoke an explicitly enabled, validated runtime-discovered operation."""
    return await invoke_alfresco_operation_impl(operation_id, arguments or {})


@mcp.tool
async def refresh_alfresco_discovery() -> dict:
    """Refresh the runtime catalog from configured Alfresco discovery providers."""
    return await refresh_alfresco_discovery_impl()


# An optional feature branch may contribute extra runtime tools. This
# dependency stays one-way: the foundation works before extensions land.
def _register_optional_runtime_tools():
    from importlib import import_module

    try:
        extension = import_module("alfresco_mcp_server.tools.action_tools")
    except ModuleNotFoundError as exc:
        if exc.name != "alfresco_mcp_server.tools.action_tools":
            raise
    else:
        extension.register_action_tools(mcp)


_register_optional_runtime_tools()

# ================== SEARCH TOOLS ==================

@mcp.tool
async def search_content(
    query: str, 
    max_results: int = 25,
    node_type: str = "",
    ctx: Context = None
) -> str:
    """Search for content in Alfresco using AFTS query language."""
    return await search_content_impl(query, max_results, node_type, ctx)

@mcp.tool
async def advanced_search(
    query: str, 
    sort_field: str = "cm:modified",
    sort_ascending: bool = False,
    max_results: int = 25,
    ctx: Context = None
) -> str:
    """Advanced search with sorting and filtering capabilities."""
    return await advanced_search_impl(query, sort_field, sort_ascending, max_results, ctx)

@mcp.tool
async def search_by_metadata(
    term: str = "",
    creator: str = "",
    content_type: str = "",
    max_results: int = 25,
    ctx: Context = None
) -> str:
    """Search for content in Alfresco by metadata fields."""
    return await search_by_metadata_impl(term, creator, content_type, max_results, ctx)

@mcp.tool
async def cmis_search(
    cmis_query: str = "SELECT * FROM cmis:document WHERE cmis:contentStreamMimeType = 'application/pdf'",
    max_results: int = 25,
    ctx: Context = None
) -> str:
    """Search using CMIS SQL syntax. Default query searches for PDF documents."""
    return await cmis_search_impl(cmis_query, max_results, ctx)

# ================== CORE TOOLS ==================

@mcp.tool
async def browse_repository(
    parent_id: str = "-my-",
    max_items: int = 25,
    ctx: Context = None
) -> str:
    """Browse the Alfresco repository structure."""
    return await browse_repository_impl(parent_id, max_items, ctx)

@mcp.tool
async def upload_document(
    file_path: str = "",
    base64_content: str = "",
    parent_id: str = "-shared-",
    description: str = "",
    ctx: Context = None
) -> str:
    """Upload a document to Alfresco."""
    return await upload_document_impl(file_path, base64_content, parent_id, description, ctx)

@mcp.tool
async def download_document(
    node_id: str,
    save_to_disk: bool = True,
    attachment: bool = True,
    destination_dir: str | None = None,
    ctx: Context = None
) -> str:
    """Download a document from Alfresco repository.

    Args:
        node_id: The Alfresco node ID to download
        save_to_disk: Save file to disk (default: True)
        attachment: Download as attachment (default: True)
        destination_dir: Optional custom destination folder (default: ~/Downloads)
    """
    return await download_document_impl(node_id, save_to_disk, attachment, destination_dir, ctx)

@mcp.tool
async def create_folder(
    folder_name: str, 
    parent_id: str = "-shared-", 
    description: str = "",
    ctx: Context = None
) -> str:
    """Create a new folder in Alfresco."""
    return await create_folder_impl(folder_name, parent_id, description, ctx)

@mcp.tool
async def get_node_properties(node_id: str, ctx: Context = None) -> str:
    """Get metadata and properties of a document or folder."""
    return await get_node_properties_impl(node_id, ctx)

@mcp.tool
async def update_node_properties(
    node_id: str,
    name: str = "",
    title: str = "",
    description: str = "",
    author: str = "",
    ctx: Context = None
) -> str:
    """Update metadata and properties of a document or folder."""
    return await update_node_properties_impl(node_id, name, title, description, author, ctx)

@mcp.tool
async def delete_node(
    node_id: str, 
    permanent: bool = False,
    ctx: Context = None
) -> str:
    """Delete a document or folder from Alfresco."""
    return await delete_node_impl(node_id, permanent, ctx)

# ================== CHECKOUT/CHECKIN TOOLS ==================

@mcp.tool
async def checkout_document(
    node_id: str, 
    download_for_editing: bool = True,
    ctx: Context = None
) -> str:
    """Check out a document for editing using Alfresco REST API."""
    return await checkout_document_impl(node_id, download_for_editing, ctx)

@mcp.tool
async def checkin_document(
    node_id: str, 
    comment: str = "", 
    major_version: bool = False,
    file_path: str = "",
    new_name: str = "",
    ctx: Context = None
) -> str:
    """Check in a document after editing using Alfresco REST API."""
    return await checkin_document_impl(node_id, comment, major_version, file_path, new_name, ctx)

@mcp.tool
async def cancel_checkout(
    node_id: str,
    ctx: Context = None
) -> str:
    """Cancel checkout of a document, discarding any working copy."""
    return await cancel_checkout_impl(node_id, ctx)

# ================== RESOURCES ==================

@mcp.resource("alfresco://repository/info", description="📊 Live Alfresco repository information including version, edition, and connection status")
async def repository_info() -> str:
    """Get Alfresco repository information using Discovery Client."""
    return await get_repository_info_impl()

@mcp.tool
async def get_repository_info_tool(ctx: Context = None) -> str:
    """Get Alfresco repository information using Discovery Client (as tool instead of resource)."""
    return await get_repository_info_impl()


# ================== PROMPTS ==================

@mcp.prompt(description="🔎 Generate comprehensive search and analysis steps for Alfresco documents with customizable analysis types")
async def search_and_analyze(query: str, analysis_type: str = "summary") -> str:
    """Generate comprehensive search and analysis prompts for Alfresco documents."""
    return await search_and_analyze_impl(query, analysis_type)

# ================== MAIN ENTRY POINT ==================

def main():
    """Main entry point for the FastMCP 3 Alfresco server."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MCP Server for Alfresco using python-alfresco-api"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport method (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP/SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE transport (default: 8000)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info(">> Starting MCP Server for Alfresco")
    logger.info(">> Hierarchical structure: tools/{core,search}, resources, prompts, utils")
    
    # Run server with specified transport
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)

if __name__ == "__main__":
    main() 
"""
MCP Server for Alfresco using FastMCP 2.0
Modular implementation with separated concerns and self-contained tools
"""
import logging
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

# Initialize MCP server
mcp = FastMCP("MCP Server for Alfresco Content Services")

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
    ctx: Context = None
) -> str:
    """Download a document from Alfresco repository."""
    return await download_document_impl(node_id, save_to_disk, attachment, ctx)

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
    """Main entry point for the FastMCP 2.0 Alfresco server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server for Alfresco 2.0")
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
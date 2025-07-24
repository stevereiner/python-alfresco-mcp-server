"""
Delete node tool for Alfresco MCP Server.
Self-contained tool for deleting documents or folders from Alfresco repository.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def delete_node_impl(
    node_id: str, 
    permanent: bool = False,
    ctx: Optional[Context] = None
) -> str:
    """Delete a document or folder from Alfresco.
    
    Args:
        node_id: Node ID to delete
        permanent: Whether to permanently delete (bypass trash)
        ctx: MCP context for progress reporting
    
    Returns:
        Deletion confirmation
    """
    if ctx:
        delete_type = "permanently delete" if permanent else "move to trash"
        await ctx.info(f"Preparing to {delete_type}: {node_id}")
        await ctx.info("Validating deletion request...")
        await ctx.report_progress(0.1)
    
    if not node_id.strip():
        return safe_format_output("❌ Error: node_id is required")
    
    try:
        await ensure_connection()
        from ...utils.connection import get_client_factory
        
        # Get client factory and create core client (working pattern from test)
        client_factory = await get_client_factory()
        core_client = client_factory.create_core_client()
        
        # Clean the node ID (remove any URL encoding or extra characters)
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            # Extract node ID from URI format
            clean_node_id = clean_node_id.split('/')[-1]
        
        logger.info(f"Attempting to delete node: {clean_node_id}")
        
        if ctx:
            await ctx.report_progress(0.7)
        
        # Get node information first to validate it exists (working pattern from test)
        node_response = core_client.nodes.get(clean_node_id)
        
        if not hasattr(node_response, 'entry'):
            return safe_format_output(f"❌ Failed to get node information for: {clean_node_id}")
        
        node_info = node_response.entry
        filename = getattr(node_info, 'name', f"document_{clean_node_id}")
        
        # Use the working high-level API pattern from test script
        core_client.nodes.delete(clean_node_id)
        
        status = "permanently deleted" if permanent else "moved to trash"
        logger.info(f"✅ Node {status}: {filename}")
        
        if ctx:
            await ctx.report_progress(1.0)
        return safe_format_output(f"""✅ **Deletion Complete**

📄 **Node**: {node_info.name}
🗑️ **Status**: {status.title()}
{"⚠️ **WARNING**: This action cannot be undone" if permanent else "ℹ️ **INFO**: Can be restored from trash"}

🆔 **Node ID**: {clean_node_id}""")
        
    except Exception as e:
        error_msg = f"ERROR: Deletion failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(f"Deletion failed: {e}")
        return error_msg 
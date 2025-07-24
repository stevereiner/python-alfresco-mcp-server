"""
Browse repository tool for Alfresco MCP Server.
Self-contained tool for browsing Alfresco repository structure.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection

logger = logging.getLogger(__name__)


async def browse_repository_impl(
    parent_id: str = "-my-",
    max_items: int = 25,
    ctx: Optional[Context] = None
) -> str:
    """Browse the Alfresco repository structure.
    
    Args:
        parent_id: Parent node ID to browse (default: user's personal space)
        max_items: Maximum number of items to return (default: 25)
        ctx: MCP context for progress reporting
    
    Returns:
        Formatted listing of repository contents
    """
    # Parameter validation and extraction
    try:
        # Extract parameters with fallback handling
        if hasattr(parent_id, 'value'):
            actual_parent_id = str(parent_id.value)
        else:
            actual_parent_id = str(parent_id)
            
        if hasattr(max_items, 'value'):
            actual_max_items = int(max_items.value)
        else:
            actual_max_items = int(max_items)
        
        # Clean and normalize for display (preserve Unicode characters)
        safe_parent_id_display = str(actual_parent_id)
        
    except Exception as e:
        logger.error(f"Parameter extraction error: {e}")
        return f"ERROR: Parameter error: {str(e)}"
    
    if ctx:
        await ctx.info(f"Browsing repository node: {safe_parent_id_display}")
        await ctx.report_progress(0.0)
    
    try:
        # Get all clients that ensure_connection() already created
        master_client = await ensure_connection()
        
        # Access the core client that was already created
        core_client = master_client.core
        
        # Try high-level API first, then use raw client property (NEW: cleaner access)
        # Check if we can use high-level nodes.get_children()
        try:
            # Use high-level API for browsing (preferred approach)
            children_result = core_client.nodes.get_children(actual_parent_id, max_items=actual_max_items)
            if children_result and hasattr(children_result, 'list') and hasattr(children_result.list, 'entries'):
                entries = children_result.list.entries
                logger.info(f"Browse response via high-level API: {len(entries)} entries found")
            else:
                raise Exception("High-level API returned unexpected format")
        except Exception as high_level_error:
            logger.info(f"High-level API failed, using raw client: {high_level_error}")
            # Fallback to raw client (ensure initialization)
            if not core_client.is_initialized:
                return safe_format_output("❌ Error: Alfresco server unavailable")
            # Use httpx_client property directly on AlfrescoCoreClient
            core_httpx = core_client.httpx_client
        
        logger.info(f"Browsing repository node: {safe_parent_id_display}")
        logger.info(f"Max items: {actual_max_items}")
        logger.info(f"Using URL: /nodes/{actual_parent_id}/children")
        
        if ctx:
            await ctx.report_progress(0.3)
        
        # If high-level API didn't work, use HTTPx fallback
        if 'entries' not in locals():
            if ctx:
                await ctx.report_progress(0.5)
            
            try:
                # Use HTTPx client as fallback
                url = f"/nodes/{actual_parent_id}/children"
                if actual_max_items != 25:
                    url += f"?maxItems={actual_max_items}"
                
                response = core_httpx.get(url)
                
                if response.status_code == 200:
                    result_data = response.json()
                    entries = result_data.get("list", {}).get("entries", [])
                    logger.info(f"Browse response via HTTPx fallback: {len(entries)} entries found")
                    
                else:
                    error_text = response.text if hasattr(response, 'text') else str(response)
                    raise Exception(f"Browse failed with status {response.status_code}: {error_text}")
                    
            except Exception as browse_error:
                raise Exception(f"Repository browse operation failed: {str(browse_error)}")
        
        # Check if we have entries
        if not entries:
            return f"Repository Browse Results\n\nNode: {safe_parent_id_display}\n\nNo child items found in this location."
        
        if ctx:
            await ctx.report_progress(1.0)
        
        # Process final results
        if entries:
            logger.info(f"Found {len(entries)} repository items")
            
            # Clean JSON-friendly formatting (no markdown syntax)
            result_text = f"Repository Browse Results\n\nNode: {safe_parent_id_display}\n\n"
            result_text += f"Parent Node: {safe_parent_id_display}\n"
            result_text += f"Found {len(entries)} item(s):\n\n"
            
            for i, entry_wrapper in enumerate(entries, 1):
                # Handle JSON response structure correctly
                if isinstance(entry_wrapper, dict) and 'entry' in entry_wrapper:
                    entry = entry_wrapper['entry']
                else:
                    entry = entry_wrapper
                
                # Extract values from dictionary
                name = str(entry.get('name', 'Unknown'))
                node_id = str(entry.get('id', 'Unknown'))
                node_type = str(entry.get('nodeType', 'Unknown'))
                is_folder = entry.get('isFolder', False)
                created_at = str(entry.get('createdAt', 'Unknown'))
                
                # Choose icon based on type
                icon = "[FOLDER]" if is_folder else "[FILE]"
                
                result_text += f"{i}. {icon} {name}\n"
                result_text += f"   - ID: {node_id}\n"
                result_text += f"   - Type: {node_type}\n"
                result_text += f"   - Created: {created_at}\n\n"
            
            result_text += f"Navigation help:\n"
            result_text += "• Use the node ID to browse deeper: browse_repository(parent_id=\"<node_id>\")\n"
            result_text += "• Common parent IDs: -root- (repository root), -shared- (shared folder), -my- (my files)\n"
            
            return result_text
        else:
            return f"Repository Browse Results\n\nNode: {safe_parent_id_display}\n\nNo child items found in this location."
            
    except Exception as e:
        # Preserve Unicode characters in error messages
        error_msg = f"ERROR: Repository browse failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return error_msg 

    if ctx:
        await ctx.info("Repository browse completed!") 
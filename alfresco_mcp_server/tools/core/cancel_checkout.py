"""
Cancel checkout tool implementation for Alfresco MCP Server.
Handles canceling document checkout with cleanup and unlock management.
"""
import logging
import pathlib
import json
from datetime import datetime
from fastmcp import Context

from ...utils.connection import get_core_client
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def cancel_checkout_impl(
    node_id: str,
    ctx: Context = None
) -> str:
    """Cancel checkout of a document, discarding any working copy.
    
    Args:
        node_id: Original node ID that was checked out
        ctx: MCP context for progress reporting
    
    Returns:
        Cancellation confirmation and cleanup status
    """
    if ctx:
        await ctx.info(f"Cancelling checkout for: {node_id}")
        await ctx.report_progress(0.1)
    
    if not node_id.strip():
        return safe_format_output("❌ Error: node_id is required")
    
    try:
        logger.info(f"Starting cancel checkout: node {node_id}")
        core_client = await get_core_client()
        
        # Clean the node ID
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            clean_node_id = clean_node_id.split('/')[-1]
        
        if ctx:
            await ctx.info("Checking node status...")
            await ctx.report_progress(0.3)
        
        # Get node information to validate using high-level core client
        node_response = core_client.nodes.get(node_id=clean_node_id)
        
        if not hasattr(node_response, 'entry'):
            return f"ERROR: Failed to get node information for: {clean_node_id}"
        
        node_info = node_response.entry
        filename = getattr(node_info, 'name', f"document_{clean_node_id}")
        
        if ctx:
            await ctx.info(">> Performing Alfresco unlock using high-level client...")
            await ctx.report_progress(0.5)
        
        # Use high-level core client unlock method
        try:
            logger.info(f"Attempting to unlock document: {clean_node_id}")
            unlock_response = core_client.versions.cancel_checkout(node_id=clean_node_id)
            if unlock_response and hasattr(unlock_response, 'entry'):
                api_status = "✅ Document unlocked in Alfresco"
            else:
                api_status = "✅ Document unlocked in Alfresco"
            logger.info(f"Document unlocked successfully: {clean_node_id}")
        except Exception as unlock_error:
            error_str = str(unlock_error)
            if "404" in error_str:
                # Document might not be locked
                api_status = "ℹ️ Document was not locked in Alfresco"
                logger.info(f"Document was not locked: {clean_node_id}")
            elif "405" in error_str:
                # Server doesn't support lock/unlock APIs
                api_status = "WARNING: Server doesn't support lock/unlock APIs (treating as unlocked)"
                logger.warning(f"Server doesn't support unlock API for {clean_node_id}")
            else:
                api_status = f"WARNING: Alfresco unlock failed: {error_str}"
                logger.error(f"Failed to unlock document {clean_node_id}: {error_str}")
        
        if ctx:
            await ctx.info("Cleaning up local files...")
            await ctx.report_progress(0.7)
        
        # Clean up local checkout tracking
        downloads_dir = pathlib.Path.home() / "Downloads"
        checkout_dir = downloads_dir / "checkout"
        checkout_manifest_path = checkout_dir / ".checkout_manifest.json"
        
        checkout_data = {}
        cleanup_status = [api_status]
        
        if checkout_manifest_path.exists():
            try:
                with open(checkout_manifest_path, 'r') as f:
                    checkout_data = json.load(f)
            except:
                checkout_data = {}
        
        # Check if this node is tracked in local checkouts
        if 'checkouts' in checkout_data and clean_node_id in checkout_data['checkouts']:
            checkout_info = checkout_data['checkouts'][clean_node_id]
            checkout_filename = checkout_info['local_file']
            checkout_file_path = checkout_dir / checkout_filename
            
            # Remove local checkout file
            try:
                if checkout_file_path.exists():
                    checkout_file_path.unlink()
                    cleanup_status.append("🗑️ Local checkout file removed")
                    logger.info(f"Removed local checkout file: {checkout_file_path}")
                else:
                    cleanup_status.append("ℹ️ Local checkout file already removed")
            except Exception as e:
                cleanup_status.append(f"WARNING: Could not remove local file: {e}")
                logger.warning(f"Failed to remove local file {checkout_file_path}: {e}")
            
            # Remove from tracking
            del checkout_data['checkouts'][clean_node_id]
            
            # Update manifest
            try:
                with open(checkout_manifest_path, 'w') as f:
                    json.dump(checkout_data, f, indent=2)
                cleanup_status.append(">> Checkout tracking updated")
            except Exception as e:
                cleanup_status.append(f"WARNING: Could not update tracking: {e}")
        else:
            cleanup_status.append("ℹ️ No local checkout tracking found")
        
        if ctx:
            await ctx.info("Document unlocked!")
            await ctx.report_progress(1.0)
        
        # Clean JSON-friendly formatting (no markdown syntax)
        result = f"🔓 Document Unlocked\n\n"
        result += f">> Document: {filename}\n"
        result += f"ID: Node ID: {clean_node_id}\n"
        result += f"🕒 Unlocked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        result += f"🧹 Cleanup Status:\n"
        
        for status in cleanup_status:
            result += f"   {status}\n"
        
        result += f"\nINFO: Note: Document is now available for others to edit."
        result += f"\nWARNING: Important: Any unsaved changes in the local file have been discarded."
        
        return safe_format_output(result)
        
    except Exception as e:
        error_msg = f"❌ Cancel checkout failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(f"Cancel checkout failed: {e}")
        return safe_format_output(error_msg) 
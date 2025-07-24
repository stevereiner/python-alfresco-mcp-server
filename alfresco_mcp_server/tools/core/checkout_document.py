"""
Checkout document tool implementation for Alfresco MCP Server.
Handles document checkout with lock management and local file download.
"""
import logging
import os
import pathlib
import json
import httpx
from datetime import datetime
from fastmcp import Context
from ...utils.connection import get_core_client
from ...config import config
from ...utils.json_utils import safe_format_output


logger = logging.getLogger(__name__)


async def checkout_document_impl(
    node_id: str, 
    download_for_editing: bool = True,
    ctx: Context = None
) -> str:
    """Check out a document for editing using Alfresco REST API.
    
    Args:
        node_id: Document node ID to check out
        download_for_editing: If True, downloads file to checkout folder for editing (default, AI-friendly).
                            If False, just creates working copy in Alfresco (testing mode)
        ctx: MCP context for progress reporting
    
    Returns:
        Checkout confirmation with file path and editing instructions if download_for_editing=True,
        or working copy details if False
    """
    if ctx:
        await ctx.info(safe_format_output(f">> Checking out document: {node_id}"))
        await ctx.info(safe_format_output("Validating node ID..."))
        await ctx.report_progress(0.1)
    
    if not node_id.strip():
        return safe_format_output("❌ Error: node_id is required")
    
    try:
        logger.info(f"Starting checkout: node {node_id}")
        core_client = await get_core_client()
        
        if ctx:
            await ctx.info(safe_format_output("Connecting to Alfresco..."))
            await ctx.report_progress(0.2)
        
        # Clean the node ID (remove any URL encoding or extra characters)
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            # Extract node ID from URI format
            clean_node_id = clean_node_id.split('/')[-1]
        
        if ctx:
            await ctx.info(safe_format_output("Getting node information..."))
            await ctx.report_progress(0.3)
        
        # Get node information first to validate it exists using high-level core client
        node_response = core_client.nodes.get(node_id=clean_node_id)
        
        if not hasattr(node_response, 'entry'):
            return safe_format_output(f"❌ Failed to get node information for: {clean_node_id}")
        
        node_info = node_response.entry
        filename = getattr(node_info, 'name', f"document_{clean_node_id}")
        
        if ctx:
            await ctx.info(safe_format_output(">> Performing Alfresco lock using core client..."))
            await ctx.report_progress(0.5)
        
        # Use core client directly since it inherits from AuthenticatedClient
        lock_status = "unlocked"
        try:
            logger.info(f"Attempting to lock document: {clean_node_id}")
            
            # Use the high-level wrapper method that handles the body internally
            logger.info(f"Using AlfrescoCoreClient versions.checkout method...")
            
            # Use the hierarchical API: versions.checkout 
            lock_response = core_client.versions.checkout(
                node_id=clean_node_id
            )
            logger.info(f"✅ Used lock_node_sync method successfully")
            
            if lock_response and hasattr(lock_response, 'entry'):
                lock_status = "locked"
            else:
                lock_status = "locked"  # Assume success if no error
            
            logger.info(f"Document locked successfully: {clean_node_id}")
                
        except Exception as lock_error:
            error_str = str(lock_error)
            if "423" in error_str or "already locked" in error_str.lower():
                logger.warning(f"Document already locked: {clean_node_id}")
                return safe_format_output(f"❌ Document is already locked by another user: {error_str}")
            elif "405" in error_str:
                # Server doesn't support lock API - continue without locking
                lock_status = "no-lock-api"
                logger.warning(f"Server doesn't support lock API for {clean_node_id}")
                if ctx:
                    await ctx.info(safe_format_output("WARNING: Server doesn't support lock API - proceeding without lock"))
            elif "multiple values for keyword argument" in error_str:
                logger.error(f"Parameter conflict in lock_node_sync: {error_str}")
                return safe_format_output(f"❌ Internal client error - parameter conflict: {error_str}")
            else:
                logger.error(f"Failed to lock document {clean_node_id}: {error_str}")
                return safe_format_output(f"❌ Document cannot be locked: {error_str}")
        
        # Document is now locked, we'll download the current content
        working_copy_id = clean_node_id  # With lock API, we work with the same node ID
        
        if ctx:
            if lock_status == "locked":
                await ctx.info(safe_format_output(f"SUCCESS: Document locked in Alfresco!"))
            else:
                await ctx.info(safe_format_output(f"Document prepared for editing (no lock support)"))
            await ctx.report_progress(0.7)
        
        if download_for_editing:
            try:
                if ctx:
                    await ctx.info(safe_format_output("Downloading current content..."))
                    await ctx.report_progress(0.8)
                
                # Get content using authenticated HTTP client from core client (ensure initialization)
                if not core_client.is_initialized:
                    return safe_format_output("❌ Error: Alfresco server unavailable")
                # Use httpx_client property directly on AlfrescoCoreClient
                http_client = core_client.httpx_client
                
                # Build correct content URL based on config
                if config.alfresco_url.endswith('/alfresco/api/-default-/public'):
                    # Full API path provided
                    content_url = f"{config.alfresco_url}/alfresco/versions/1/nodes/{clean_node_id}/content"
                elif config.alfresco_url.endswith('/alfresco/api'):
                    # Base API path provided
                    content_url = f"{config.alfresco_url}/-default-/public/alfresco/versions/1/nodes/{clean_node_id}/content"
                else:
                    # Base server URL provided
                    content_url = f"{config.alfresco_url}/alfresco/api/-default-/public/alfresco/versions/1/nodes/{clean_node_id}/content"
                
                response = http_client.get(content_url)
                response.raise_for_status()
                
                # Save to Downloads/checkout folder
                downloads_dir = pathlib.Path.home() / "Downloads"
                checkout_dir = downloads_dir / "checkout"
                checkout_dir.mkdir(parents=True, exist_ok=True)
                
                # Create unique filename with node ID
                safe_filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
                local_filename = f"{safe_filename}_{clean_node_id}"
                local_path = checkout_dir / local_filename
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Downloaded for editing: {filename} -> {local_path}")
                # Update checkout tracking with actual working copy ID
                checkout_manifest_path = checkout_dir / ".checkout_manifest.json"
                checkout_data = {}
                
                if checkout_manifest_path.exists():
                    try:
                        with open(checkout_manifest_path, 'r') as f:
                            checkout_data = json.load(f)
                    except:
                        checkout_data = {}
                
                if 'checkouts' not in checkout_data:
                    checkout_data['checkouts'] = {}
                
                checkout_time = datetime.now().isoformat()
                
                checkout_data['checkouts'][clean_node_id] = {
                    'original_node_id': clean_node_id,
                    'locked_node_id': clean_node_id,  # Same as original since we lock, not checkout
                    'local_file': local_filename,
                    'checkout_time': checkout_time,
                    'original_filename': filename
                }
                
                # Save manifest
                with open(checkout_manifest_path, 'w') as f:
                    json.dump(checkout_data, f, indent=2)
                
                if ctx:
                    await ctx.info(safe_format_output("SUCCESS: Checkout completed!"))
                    await ctx.report_progress(1.0)
                
                # Format file size
                file_size = len(response.content)
                if file_size < 1024:
                    size_str = f"{file_size} bytes"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                
                if lock_status == "locked":
                    result = f"🔒 Document Checked Out Successfully!\n\n"
                    result += f"📄 Name: {filename}\n"
                    result += f"🆔 Node ID: {clean_node_id}\n"
                    result += f"📏 Size: {size_str}\n"
                    result += f"💾 Downloaded to: {local_path}\n"
                    result += f"🔒 Lock Status: {lock_status}\n"
                    result += f"🕒 Checkout Time: {checkout_time}\n\n"
                    result += f"Next steps:\n"
                    result += f"   1. Edit the document at: {local_path}\n"
                    result += f"   2. Save your changes\n"
                    result += f"   3. Use checkin_document tool to upload changes\n\n"
                    result += f"The document is now locked in Alfresco to prevent conflicts.\n"
                    result += f"Other users cannot edit it until you check it back in or cancel the checkout."
                    
                    return safe_format_output(result)
                else:
                                    result = f"📥 **Document downloaded for editing!**\n\n"
                status_msg = "ℹ️ **Status**: Downloaded for editing (server doesn't support locks)"
                important_msg = "ℹ️ **Note**: Server doesn't support locking - multiple users may edit simultaneously."
                
                result += f">> **Downloaded to**: `{local_path}`\n"
                result += f">> **Original**: {filename}\n"
                result += f">> **Size**: {size_str}\n"
                result += f"{status_msg}\n"
                result += f"🔗 **Node ID**: {clean_node_id}\n"
                result += f"🕒 **Downloaded at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                result += f">> **Instructions**:\n"
                result += f"1. Open the file in your preferred application (Word, Excel, etc.)\n"
                result += f"2. Make your edits and save the file\n"
                result += f"3. When finished, use `checkin_document` to upload your changes\n\n"
                result += f"{important_msg}"
                
                return safe_format_output(result)
            except Exception as e:
                error_msg = f"❌ Checkout failed: {str(e)}"
                if ctx:
                    await ctx.error(safe_format_output(error_msg))
                logger.error(f"Checkout failed: {e}")
                return safe_format_output(error_msg)
        else:
            # Testing mode - just return lock status
            if lock_status == "locked":
                return f"SUCCESS: Document locked successfully for testing. Node ID: {clean_node_id}, Status: LOCKED"
            else:
                return f"WARNING: Document prepared for editing (no lock support). Node ID: {clean_node_id}"
        
    except Exception as e:
        error_msg = f"❌ Checkout failed: {str(e)}"
        if ctx:
            await ctx.error(safe_format_output(error_msg))
        logger.error(f"Checkout failed: {e}")
        return safe_format_output(error_msg) 
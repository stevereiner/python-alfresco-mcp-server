"""
Checkin document tool implementation for Alfresco MCP Server.
Handles document checkin with versioning and cleanup management.
"""
import logging
import os
import pathlib
import json
import urllib.parse
from io import BytesIO
from datetime import datetime
from fastmcp import Context

from ...utils.connection import get_core_client
from ...config import config
from ...utils.json_utils import safe_format_output
from python_alfresco_api.raw_clients.alfresco_core_client.core_client.types import File
from python_alfresco_api.raw_clients.alfresco_core_client.core_client.api.nodes.update_node_content import sync as update_node_content_sync

logger = logging.getLogger(__name__)


async def checkin_document_impl(
    node_id: str, 
    comment: str = "", 
    major_version: bool = False,
    file_path: str = "",
    new_name: str = "",
    ctx: Context = None
) -> str:
    """Check in a document after editing using Alfresco REST API.
    
    Args:
        node_id: Original node ID to check in (not working copy)
        comment: Check-in comment (default: empty)
        major_version: Whether to create a major version (default: False = minor version)
        file_path: Specific file path to upload (if empty, auto-detects from checkout folder)
        new_name: Optional new name for the file during checkin (default: keep original name)
        ctx: MCP context for progress reporting
    
    Returns:
        Check-in confirmation with version details and cleanup status
    """
    if ctx:
        await ctx.info(f"Checking in document: {node_id}")
        await ctx.info("Validating parameters...")
        await ctx.report_progress(0.1)
    
    if not node_id.strip():
        return safe_format_output("❌ Error: node_id is required")
    
    try:
        logger.info(f"Starting checkin: node {node_id}")
        core_client = await get_core_client()
        
        # Clean the node ID
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            clean_node_id = clean_node_id.split('/')[-1]
        
        if ctx:
            await ctx.info("Finding checkout file...")
            await ctx.report_progress(0.2)
        
        # Find the file to upload
        checkout_file_path = None
        checkout_data = {}
        working_copy_id = None
        
        if file_path:
            # Use specific file path provided - handle quotes and path expansion
            cleaned_file_path = file_path.strip().strip('"').strip("'")
            
            # Handle macOS/Unix path expansion (~/Documents, etc.)
            if cleaned_file_path.startswith('~'):
                cleaned_file_path = os.path.expanduser(cleaned_file_path)
            
            checkout_file_path = pathlib.Path(cleaned_file_path)
            if not checkout_file_path.exists():
                return safe_format_output(f"❌ Specified file not found: {cleaned_file_path} (cleaned from: {file_path})")
            
            # Linux-specific: Check file permissions
            if not os.access(checkout_file_path, os.R_OK):
                return safe_format_output(f"❌ File not readable (permission denied): {cleaned_file_path}")
        else:
            # Auto-detect from checkout folder
            downloads_dir = pathlib.Path.home() / "Downloads"
            checkout_dir = downloads_dir / "checkout"
            checkout_manifest_path = checkout_dir / ".checkout_manifest.json"
            
            if checkout_manifest_path.exists():
                try:
                    with open(checkout_manifest_path, 'r') as f:
                        checkout_data = json.load(f)
                except:
                    checkout_data = {}
            
            if 'checkouts' in checkout_data and clean_node_id in checkout_data['checkouts']:
                checkout_info = checkout_data['checkouts'][clean_node_id]
                checkout_filename = checkout_info['local_file']
                locked_node_id = checkout_info.get('locked_node_id', clean_node_id)  # Updated for lock API
                checkout_file_path = checkout_dir / checkout_filename
                
                if not checkout_file_path.exists():
                    return safe_format_output(f"❌ Checkout file not found: {checkout_file_path}. File may have been moved or deleted.")
            else:
                return safe_format_output(f"❌ No locked document found for node {clean_node_id}. Use checkout_document first, or specify file_path manually.")
        
        if ctx:
            await ctx.info(f"Uploading file: {checkout_file_path.name}")
            await ctx.report_progress(0.4)
        
        # Read the file content
        with open(checkout_file_path, 'rb') as f:
            file_content = f.read()
        
        logger.info(f"Checkin file: {checkout_file_path.name} ({len(file_content)} bytes)")
        # Get original node info using high-level core client
        node_response = core_client.nodes.get(node_id=clean_node_id)
        if not hasattr(node_response, 'entry'):
            return safe_format_output(f"❌ Failed to get node information for: {clean_node_id}")
        
        node_info = node_response.entry
        original_filename = getattr(node_info, 'name', f"document_{clean_node_id}")
        
        if ctx:
            await ctx.info("Uploading new content with versioning using high-level API...")
            await ctx.report_progress(0.7)
        
        # **USE HIGH-LEVEL API: update_node_content.sync()**
        # Use new name if provided, otherwise keep original filename
        final_filename = new_name.strip() if new_name.strip() else original_filename
        
        # Create File object with content
        file_obj = File(
            payload=BytesIO(file_content),
            file_name=final_filename,
            mime_type="application/octet-stream"
        )
        
        # Use high-level update_node_content API instead of manual httpx
        try:
            version_type = "major" if major_version else "minor"
            logger.info(f"Updating content for {clean_node_id} ({version_type} version)")
            # Ensure raw client is initialized before using it
            if not core_client.is_initialized:
                return safe_format_output("❌ Error: Alfresco server unavailable")
            # Use high-level update_node_content API
            content_response = update_node_content_sync(
                node_id=clean_node_id,
                client=core_client.raw_client,
                body=file_obj,
                major_version=major_version,
                comment=comment if comment else None,
                name=new_name.strip() if new_name.strip() else None
            )
            
            if not content_response:
                return safe_format_output(f"❌ Failed to update document content using high-level API")
            
            logger.info(f"Content updated successfully for {clean_node_id}")
            
            # CRITICAL: Unlock the document after successful content update to complete checkin
            try:
                logger.info(f"Unlocking document after successful checkin: {clean_node_id}")
                unlock_response = core_client.versions.cancel_checkout(node_id=clean_node_id)
                logger.info(f"Document unlocked successfully after checkin: {clean_node_id}")
            except Exception as unlock_error:
                error_str = str(unlock_error)
                if "404" in error_str:
                    logger.info(f"Document was not locked (already unlocked): {clean_node_id}")
                elif "405" in error_str:
                    logger.warning(f"Server doesn't support unlock APIs: {clean_node_id}")
                else:
                    logger.error(f"Failed to unlock document after checkin: {clean_node_id} - {error_str}")
                    # Don't fail the entire checkin if unlock fails - content was updated successfully
                
        except Exception as api_error:
            return safe_format_output(f"❌ Failed to update document content: {str(api_error)}")
        
        # Get updated node info to show version details using high-level core client
        updated_node_response = core_client.nodes.get(node_id=clean_node_id)
        updated_node = updated_node_response.entry if hasattr(updated_node_response, 'entry') else {}
        
        # Extract version using multiple access methods (same as get_node_properties)
        new_version = 'Unknown'
        if hasattr(updated_node, 'properties') and updated_node.properties:
            try:
                # Try to_dict() method first
                if hasattr(updated_node.properties, 'to_dict'):
                    props_dict = updated_node.properties.to_dict()
                    new_version = props_dict.get('cm:versionLabel', 'Unknown')
                    logger.info(f"Version found via to_dict(): {new_version}")
                # Try direct attribute access
                elif hasattr(updated_node.properties, 'cm_version_label') or hasattr(updated_node.properties, 'cm:versionLabel'):
                    new_version = getattr(updated_node.properties, 'cm_version_label', getattr(updated_node.properties, 'cm:versionLabel', 'Unknown'))
                    logger.info(f"Version found via attributes: {new_version}")
                # Try dict-like access
                elif hasattr(updated_node.properties, '__getitem__'):
                    new_version = updated_node.properties.get('cm:versionLabel', 'Unknown') if hasattr(updated_node.properties, 'get') else updated_node.properties['cm:versionLabel'] if 'cm:versionLabel' in updated_node.properties else 'Unknown'
                    logger.info(f"Version found via dict access: {new_version}")
                else:
                    logger.warning(f"Version properties - type: {type(updated_node.properties)}, methods: {dir(updated_node.properties)}")
            except Exception as version_error:
                logger.error(f"Error extracting version: {version_error}")
                new_version = 'Unknown'
        else:
            logger.warning("No properties found for version extraction")
        
        if ctx:
            await ctx.info("Cleaning up checkout tracking...")
            await ctx.report_progress(0.9)
        
        # Clean up checkout tracking
        cleanup_status = "ℹ️  No checkout tracking to clean up"
        if checkout_data and 'checkouts' in checkout_data and clean_node_id in checkout_data['checkouts']:
            del checkout_data['checkouts'][clean_node_id]
            
            checkout_manifest_path = pathlib.Path.home() / "Downloads" / "checkout" / ".checkout_manifest.json"
            with open(checkout_manifest_path, 'w') as f:
                json.dump(checkout_data, f, indent=2)
            
            # Optionally remove the checkout file
            try:
                checkout_file_path.unlink()
                cleanup_status = "🗑️  Local checkout file cleaned up"
            except:
                cleanup_status = "WARNING:  Local checkout file cleanup failed"
        
        if ctx:
            await ctx.info("Checkin completed: Content updated + Document unlocked + Version created!")
            await ctx.report_progress(1.0)
        
        # Format file size
        file_size = len(file_content)
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        # Clean JSON-friendly formatting (no markdown syntax)
        return safe_format_output(f"""✅ Document checked in successfully!

📄 Document: {final_filename}
🔢 New Version: {new_version} ({version_type})
📝 Comment: {comment if comment else '(no comment)'}
📊 File Size: {size_str}
🔗 Node ID: {clean_node_id}
{f"📝 Renamed: {original_filename} → {final_filename}" if new_name.strip() else ""}

{cleanup_status}

Next Steps:
🔓 Document is now UNLOCKED and available for others to edit
✅ New version has been created with your changes
✅ You can continue editing by using checkout_document again

Status: Content updated → Document unlocked → Checkin complete!""")
        
    except Exception as e:
        logger.error(f"Checkin failed: {str(e)}")
        return safe_format_output(f"❌ Checkin failed: {str(e)}") 
"""
Get node properties tool for Alfresco MCP Server.
Self-contained tool for retrieving document/folder metadata and properties.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection, get_core_client

logger = logging.getLogger(__name__)


async def get_node_properties_impl(node_id: str, ctx: Optional[Context] = None) -> str:
    """Get metadata and properties of a document or folder.
    
    Args:
        node_id: Node ID to get properties for
        ctx: MCP context for progress reporting
    
    Returns:
        Formatted node properties and metadata
    """
    if ctx:
        await ctx.info(f"Getting properties for: {node_id}")
        await ctx.report_progress(0.1)
    
    if not node_id.strip():
        return "ERROR: node_id is required"
    
    try:
        # Ensure connection and get core client
        await ensure_connection()
        core_client = await get_core_client()
        
        # Clean the node ID (remove any URL encoding or extra characters)
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            # Extract node ID from URI format
            clean_node_id = clean_node_id.split('/')[-1]
        
        logger.info(f"Getting properties for node: {clean_node_id}")
        
        if ctx:
            await ctx.report_progress(0.5)
        
        # Get node metadata using core client
        node_response = core_client.nodes.get(
            node_id=clean_node_id,
            include=["properties", "permissions", "path"]
        )
        
        if not hasattr(node_response, 'entry'):
            return f"ERROR: Failed to get node information for: {clean_node_id}"
        
        node_info = node_response.entry
        
        # Extract basic properties - use correct Python attribute names
        filename = getattr(node_info, 'name', 'Unknown')
        node_type_raw = getattr(node_info, 'node_type', 'Unknown')
        created_at = getattr(node_info, 'created_at', 'Unknown')
        modified_at = getattr(node_info, 'modified_at', 'Unknown')
        
        # Clean up node_type display - convert enum to string
        node_type = 'Unknown'
        if node_type_raw != 'Unknown':
            if hasattr(node_type_raw, 'value'):
                node_type = node_type_raw.value  # For enum objects
            else:
                node_type = str(node_type_raw)  # For string objects
        
        # Extract creator and modifier information - use correct attribute names
        creator = 'Unknown'
        modifier = 'Unknown'
        if hasattr(node_info, 'created_by_user') and node_info.created_by_user:
            creator = getattr(node_info.created_by_user, 'display_name', 'Unknown')
        if hasattr(node_info, 'modified_by_user') and node_info.modified_by_user:
            modifier = getattr(node_info.modified_by_user, 'display_name', 'Unknown')
        
        # Extract size information - use correct attribute names
        size_str = 'Unknown'
        if hasattr(node_info, 'content') and node_info.content:
            size_bytes = getattr(node_info.content, 'size_in_bytes', 0)
            if size_bytes > 0:
                if size_bytes > 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                elif size_bytes > 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes} bytes"
        
        # Extract MIME type - use correct attribute names
        mime_type = 'Unknown'
        if hasattr(node_info, 'content') and node_info.content:
            mime_type = getattr(node_info.content, 'mime_type', 'Unknown')
        
        # Extract path information - use correct attribute names
        path = 'Unknown'
        if hasattr(node_info, 'path') and node_info.path:
            path = getattr(node_info.path, 'name', 'Unknown')
        
        # Extract custom properties - try multiple access methods
        title = 'Unknown'
        description = 'Unknown'
        author = 'Unknown'
        if hasattr(node_info, 'properties') and node_info.properties:
            try:
                # Try to_dict() method first
                if hasattr(node_info.properties, 'to_dict'):
                    props_dict = node_info.properties.to_dict()
                    title = props_dict.get('cm:title', 'Unknown')
                    description = props_dict.get('cm:description', 'Unknown') 
                    author = props_dict.get('cm:author', 'Unknown')
                    logger.info(f"Properties found via to_dict(): title={title}, description={description}, author={author}")
                # Try direct attribute access
                elif hasattr(node_info.properties, 'cm_title') or hasattr(node_info.properties, 'cm:title'):
                    title = getattr(node_info.properties, 'cm_title', getattr(node_info.properties, 'cm:title', 'Unknown'))
                    description = getattr(node_info.properties, 'cm_description', getattr(node_info.properties, 'cm:description', 'Unknown'))
                    author = getattr(node_info.properties, 'cm_author', getattr(node_info.properties, 'cm:author', 'Unknown'))
                    logger.info(f"Properties found via attributes: title={title}, description={description}, author={author}")
                # Try dict-like access
                elif hasattr(node_info.properties, '__getitem__'):
                    title = node_info.properties.get('cm:title', 'Unknown') if hasattr(node_info.properties, 'get') else node_info.properties['cm:title'] if 'cm:title' in node_info.properties else 'Unknown'
                    description = node_info.properties.get('cm:description', 'Unknown') if hasattr(node_info.properties, 'get') else node_info.properties['cm:description'] if 'cm:description' in node_info.properties else 'Unknown'
                    author = node_info.properties.get('cm:author', 'Unknown') if hasattr(node_info.properties, 'get') else node_info.properties['cm:author'] if 'cm:author' in node_info.properties else 'Unknown'
                    logger.info(f"Properties found via dict access: title={title}, description={description}, author={author}")
                else:
                    logger.warning(f"Properties object type: {type(node_info.properties)}, available methods: {dir(node_info.properties)}")
            except Exception as props_error:
                logger.error(f"Error accessing properties: {props_error}")
        else:
            logger.warning("No properties found on node_info")
        
        # Determine if it's a folder and if it's locked - use correct attribute names
        is_folder = 'Yes' if node_type == 'cm:folder' else 'No'
        is_locked = 'Unknown'
        if hasattr(node_info, 'is_locked'):
            is_locked = 'Yes' if node_info.is_locked else 'No'
        
        # Version information - use correct attribute names
        version = 'Unknown'
        if hasattr(node_info, 'properties') and node_info.properties:
            if hasattr(node_info.properties, 'to_dict'):
                props_dict = node_info.properties.to_dict()
                version = props_dict.get('cm:versionLabel', 'Unknown')
        
        logger.info(f"Retrieved properties for: {filename}")
        
        if ctx:
            await ctx.report_progress(1.0)
        
        # Clean JSON-friendly formatting (no markdown syntax)
        # Only show properties that exist and have meaningful values
        result = f"Node Properties for: {filename}\n\n"
        result += f"Node ID: {clean_node_id}\n"
        result += f"Name: {filename}\n"
        
        # Only show properties that exist and aren't "Unknown"
        if path and path != 'Unknown':
            result += f"Path: {path}\n"
        if node_type and node_type != 'Unknown':
            result += f"Type: {node_type}\n"
        if created_at and created_at != 'Unknown':
            result += f"Created: {created_at}\n"
        if modified_at and modified_at != 'Unknown':
            result += f"Modified: {modified_at}\n"
        if creator and creator != 'Unknown':
            result += f"Creator: {creator}\n"
        if modifier and modifier != 'Unknown':
            result += f"Modifier: {modifier}\n"
        if size_str and size_str != 'Unknown':
            result += f"Size: {size_str}\n"
        if mime_type and mime_type != 'Unknown':
            result += f"MIME Type: {mime_type}\n"
        if title and title != 'Unknown':
            result += f"Title: {title}\n"
        if description and description != 'Unknown':
            result += f"Description: {description}\n"
        if author and author != 'Unknown':
            result += f"Author: {author}\n"
        if is_folder and is_folder != 'Unknown':
            result += f"Is Folder: {is_folder}\n"
        if is_locked and is_locked != 'Unknown':
            result += f"Is Locked: {is_locked}\n"
        if version and version != 'Unknown':
            result += f"Version: {version}\n"
        
        return result
        
    except Exception as e:
        error_msg = f"ERROR: Failed to get properties: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(f"Get properties failed: {e}")
        return error_msg 
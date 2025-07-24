"""
Update node properties tool for Alfresco MCP Server.
Self-contained tool for updating document/folder metadata and properties.
"""
import logging
import os
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection, get_core_client

logger = logging.getLogger(__name__)


async def update_node_properties_impl(
    node_id: str,
    name: str = "",
    title: str = "",
    description: str = "",
    author: str = "",
    ctx: Optional[Context] = None
) -> str:
    """Update metadata and properties of a document or folder.
    
    Args:
        node_id: Node ID to update (required)
        name: New name for the node (optional)
        title: Document title (cm:title) (optional)
        description: Document description (cm:description) (optional)
        author: Document author (cm:author) (optional)
        ctx: MCP context for progress reporting
    
    Returns:
        Update confirmation with changes made
    """
    if ctx:
        await ctx.info(f"Updating properties for: {node_id}")
        await ctx.report_progress(0.1)
    
    if not node_id.strip():
        return "ERROR: node_id is required"
    
    if not any([name, title, description, author]):
        return "ERROR: At least one property (name, title, description, or author) must be provided"
    
    try:
        # Ensure connection and get core client
        await ensure_connection()
        core_client = await get_core_client()
        
        # Clean the node ID (remove any URL encoding or extra characters)
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            # Extract node ID from URI format
            clean_node_id = clean_node_id.split('/')[-1]
        
        logger.info(f"Updating properties for node: {clean_node_id}")
        
        if ctx:
            await ctx.report_progress(0.3)
        
        # Get node information first to validate it exists
        try:
            node_response = core_client.nodes.get(node_id=clean_node_id)
            if not hasattr(node_response, 'entry'):
                return f"ERROR: Failed to get node information for: {clean_node_id}"
            
            node_info = node_response.entry
            current_name = getattr(node_info, 'name', f"document_{clean_node_id}")
            
        except Exception as get_error:
            return f"ERROR: Failed to validate node {clean_node_id}: {str(get_error)}"
        
        if ctx:
            await ctx.report_progress(0.5)
        
        # Prepare updates for actual API call
        properties_updates = {}
        if title and title.strip():
            properties_updates['cm:title'] = title.strip()
        if description and description.strip():
            properties_updates['cm:description'] = description.strip()
        if author and author.strip():
            properties_updates['cm:author'] = author.strip()
        
        # Import the UpdateNodeRequest model
        try:
            from python_alfresco_api.clients.core.nodes.models import UpdateNodeRequest
        except ImportError:
            return "ERROR: Failed to import UpdateNodeRequest model"
        
        # Prepare update request
        update_request = UpdateNodeRequest()
        
        if name and name.strip():
            update_request.name = name.strip()
        if properties_updates:
            update_request.properties = properties_updates
            
        if ctx:
            await ctx.report_progress(0.7)
        
        # Use the core client's update method
        try:
            updated_node = core_client.nodes.update(
                node_id=clean_node_id,
                request=update_request
            )
            logger.info("Node properties updated successfully")
            
        except Exception as update_error:
            logger.error(f"Update failed: {update_error}")
            return f"ERROR: Update failed: {str(update_error)}"

        if ctx:
            await ctx.report_progress(1.0)
        
        changes = []
        if name:
            changes.append(f"- Name: {name}")
        if title:
            changes.append(f"- Title: {title}")
        if description:
            changes.append(f"- Description: {description}")
        if author:
            changes.append(f"- Author: {author}")
        
        updated_properties = "\n".join(changes)
        
        # Clean JSON-friendly formatting (no markdown syntax)
        return f"Node Updated Successfully\n\nNode ID: {clean_node_id}\nUpdated Properties:\n{updated_properties}\nUpdate completed successfully"
        
    except Exception as e:
        error_msg = f"ERROR: Update failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(f"Update failed: {e}")
        return error_msg 
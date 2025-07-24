"""
Create folder tool for Alfresco MCP Server.
Self-contained tool for creating folders in Alfresco repository.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def create_folder_impl(
    folder_name: str, 
    parent_id: str = "-shared-", 
    description: str = "",
    ctx: Optional[Context] = None
) -> str:
    """Create a new folder in Alfresco.
    
    Args:
        folder_name: Name of the new folder
        parent_id: Parent folder ID (default: shared folder)
        description: Folder description
        ctx: MCP context for progress reporting
    
    Returns:
        Folder creation confirmation with details
    """
    if ctx:
        await ctx.info(f">> Creating folder '{folder_name}' in {parent_id}")
        await ctx.info("Validating folder parameters...")
        await ctx.report_progress(0.0)
    
    if not folder_name.strip():
        return safe_format_output("❌ Error: folder_name is required")
    
    try:
        # Ensure connection and get client factory (working pattern from test)
        await ensure_connection()
        from ...utils.connection import get_client_factory
        
        # Get client factory and create core client (working pattern from test)
        client_factory = await get_client_factory()
        core_client = client_factory.create_core_client()
        
        if ctx:
            await ctx.info("Creating folder in Alfresco...")
            await ctx.report_progress(0.5)
        
        logger.info(f"Creating folder '{folder_name}' in parent {parent_id}")
        
        # Prepare properties
        properties = {"cm:title": folder_name}
        if description:
            properties["cm:description"] = description
        
        logger.info(f"Using high-level API: core_client.nodes.create_folder()")
        
        # Use the working high-level API pattern from test script
        folder_response = core_client.nodes.create_folder(
            name=folder_name,
            parent_id=parent_id,
            properties=properties
        )
        
        if folder_response and hasattr(folder_response, 'entry'):
            entry = folder_response.entry
            logger.info("✅ Folder created successfully")
            
            # Extract folder details from response
            folder_id = getattr(entry, 'id', 'Unknown')
            folder_name_response = getattr(entry, 'name', folder_name)
            created_at = getattr(entry, 'createdAt', 'Unknown')
            node_type = getattr(entry, 'nodeType', 'cm:folder')
        else:
            raise Exception(f"Failed to create folder - invalid response from core client")
        
        if ctx:
            await ctx.info("Processing folder creation response...")
            await ctx.report_progress(0.9)
        
        if ctx:
            await ctx.info("Folder created!")
            await ctx.report_progress(1.0)
            await ctx.info(f"SUCCESS: Folder '{folder_name_response}' created successfully")
            
        # Clean JSON-friendly formatting (no markdown syntax)
        return safe_format_output(f"""✅ Folder Created Successfully!

📁 Name: {folder_name_response}
🆔 Folder ID: {folder_id}
📍 Parent: {parent_id}
📅 Created: {created_at}
🏷️ Type: {node_type}
📝 Description: {description or 'None'}""")
        
    except Exception as e:
        error_msg = f"❌ Folder creation failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(f"Folder creation failed: {e}")
        return safe_format_output(error_msg) 
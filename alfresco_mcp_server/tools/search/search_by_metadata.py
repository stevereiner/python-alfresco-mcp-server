"""
Search by metadata tool for Alfresco MCP Server.
Each tool is self-contained with its own validation, business logic, and env handling.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def search_by_metadata_impl(
    term: str = "",
    creator: str = "",
    content_type: str = "",
    max_results: int = 25,
    ctx: Optional[Context] = None
) -> str:
    """Search for content in Alfresco by metadata fields.
    
    Args:
        term: Search term to include (primary search parameter)
        creator: Creator username to filter by
        content_type: Content type to filter by (e.g., "cm:content", "cm:folder")
        max_results: Maximum number of results to return (default: 25)
        ctx: MCP context for progress reporting
    
    Returns:
        Formatted search results with metadata
    """
    # Parameter validation and extraction
    try:
        # Extract parameters with fallback handling
        if hasattr(creator, 'value'):
            actual_creator = str(creator.value)
        else:
            actual_creator = str(creator)
            
        if hasattr(content_type, 'value'):
            actual_content_type = str(content_type.value)
        else:
            actual_content_type = str(content_type)
            
        if hasattr(term, 'value'):
            actual_term = str(term.value)
        else:
            actual_term = str(term)
            
        if hasattr(max_results, 'value'):
            actual_max_results = int(max_results.value)
        else:
            actual_max_results = int(max_results)
        
        # Clean and normalize for display (preserve Unicode characters)
        safe_creator_display = str(actual_creator)
        safe_content_type_display = str(actual_content_type)
        safe_term_display = str(actual_term)
        
    except Exception as e:
        logger.error(f"Parameter extraction error: {e}")
        return f"ERROR: Parameter error: {str(e)}"
    
    if ctx:
        await ctx.info(safe_format_output(f"Searching by metadata in Alfresco..."))
        await ctx.report_progress(0.0)
    
    try:
        # Get all clients that ensure_connection() already created
        master_client = await ensure_connection()
        
        # Import search_utils
        from python_alfresco_api.utils import search_utils
        
        # Access the search client that was already created
        search_client = master_client.search
        
        logger.info(f"Searching Alfresco by metadata - creator: '{safe_creator_display}', type: '{safe_content_type_display}', term: '{safe_term_display}'")
        
        if ctx:
            await ctx.report_progress(0.3)
        
        # Build query using search_utils.build_query() utility
        search_query = search_utils.build_query(
            term=actual_term if actual_term.strip() else None,
            content_type=actual_content_type if actual_content_type.strip() else None,
            creator=actual_creator if actual_creator.strip() else None
        )
        
        # If no parameters provided, search everything
        if not search_query or search_query.strip() == "":
            search_query = "*"
        
        # Execute search using existing search client
        if ctx:
            await ctx.report_progress(0.5)
        
        try:
            # Use correct working pattern: search_utils.simple_search with existing search_client
            search_results = search_utils.simple_search(search_client, search_query, max_items=actual_max_results)
            
            if not search_results or not hasattr(search_results, 'list_'):
                return safe_format_output(f"ERROR: Search failed - invalid response from Alfresco")
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return safe_format_output(f"ERROR: Search failed: {str(e)}")
        
        # Process results using correct pattern
        entries = []
        if hasattr(search_results, 'list_') and search_results.list_ and hasattr(search_results.list_, 'entries'):
            entries = search_results.list_.entries if search_results.list_ else []
        
        if ctx:
            await ctx.report_progress(1.0)
        
        # Process final results
        if entries:
            logger.info(f"Found {len(entries)} search results")
            result_text = f"Found {len(entries)} item(s) matching the metadata criteria:\n\n"
            
            for i, entry in enumerate(entries, 1):
                # Debug: Log the entry structure
                logger.debug(f"Entry {i} type: {type(entry)}, content: {entry}")
                
                # Handle different possible entry structures
                node = None
                if isinstance(entry, dict):
                    if 'entry' in entry:
                        node = entry['entry']
                    elif 'name' in entry:  # Direct node structure
                        node = entry
                    else:
                        logger.warning(f"Unknown entry structure: {entry}")
                        continue
                elif hasattr(entry, 'entry'):  # ResultSetRowEntry object
                    node = entry.entry
                else:
                    logger.warning(f"Entry is not a dict or ResultSetRowEntry: {type(entry)}")
                    continue
                
                if node:
                    # Handle both dict and ResultNode objects
                    if isinstance(node, dict):
                        name = str(node.get('name', 'Unknown'))
                        node_id = str(node.get('id', 'Unknown'))
                        node_type_actual = str(node.get('nodeType', 'Unknown'))
                        created_at = str(node.get('createdAt', 'Unknown'))
                    else:
                        # ResultNode object - access attributes directly
                        name = str(getattr(node, 'name', 'Unknown'))
                        node_id = str(getattr(node, 'id', 'Unknown'))
                        node_type_actual = str(getattr(node, 'node_type', 'Unknown'))
                        created_at = str(getattr(node, 'created_at', 'Unknown'))
                    
                    # Clean JSON-friendly formatting (no markdown syntax)
                    # Apply safe formatting to individual fields to prevent emoji encoding issues
                    safe_name = safe_format_output(name)
                    safe_node_id = safe_format_output(node_id)
                    safe_node_type = safe_format_output(node_type_actual)
                    safe_created_at = safe_format_output(created_at)
                    
                    result_text += f"{i}. {safe_name}\n"
                    result_text += f"   - ID: {safe_node_id}\n"
                    result_text += f"   - Type: {safe_node_type}\n"
                    result_text += f"   - Created: {safe_created_at}\n\n"
        
            return safe_format_output(result_text)
        else:
            # Simple "0" for zero results as requested
            return "0"
        
    except Exception as e:
        # Preserve Unicode characters in error messages
        error_msg = f"ERROR: Metadata search failed: {str(e)}"
        if ctx:
            await ctx.error(safe_format_output(error_msg))
        return safe_format_output(error_msg) 

    if ctx:
        await ctx.info(safe_format_output("Metadata search completed!")) 
"""
Advanced search tool for Alfresco MCP Server.
Each tool is self-contained with its own validation, business logic, and env handling.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def advanced_search_impl(
    query: str, 
    sort_field: str = "cm:modified",
    sort_ascending: bool = False,
    max_results: int = 25,
    ctx: Optional[Context] = None
) -> str:
    """Advanced search with sorting and filtering capabilities.
    
    Args:
        query: Search query string (supports Alfresco Full Text Search syntax)
        sort_field: Field to sort by (default: cm:modified)
        sort_ascending: Sort order (default: False for descending)
        max_results: Maximum number of results to return (default: 25)
        ctx: MCP context for progress reporting
    
    Returns:
        Formatted search results with metadata, sorted as requested
    """
    # Parameter validation and extraction
    try:
        # Extract parameters with fallback handling
        if hasattr(query, 'value'):
            actual_query = str(query.value)
        else:
            actual_query = str(query)
            
        if hasattr(sort_field, 'value'):
            actual_sort_field = str(sort_field.value)
        else:
            actual_sort_field = str(sort_field)
            
        if hasattr(sort_ascending, 'value'):
            actual_sort_ascending = bool(sort_ascending.value)
        else:
            actual_sort_ascending = bool(sort_ascending)
            
        if hasattr(max_results, 'value'):
            actual_max_results = int(max_results.value)
        else:
            actual_max_results = int(max_results)
        
        # Clean and normalize for display (preserve Unicode characters)
        safe_query_display = str(actual_query)
        safe_sort_field_display = str(actual_sort_field)
        
    except Exception as e:
        logger.error(f"Parameter extraction error: {e}")
        return f"ERROR: Parameter error: {str(e)}"
    
    if ctx:
        await ctx.info(safe_format_output(f"Advanced search for '{safe_query_display}' with sorting..."))
        await ctx.report_progress(0.0)
    
    try:
        # Get all clients that ensure_connection() already created
        master_client = await ensure_connection()
        
        # Import search_utils
        from python_alfresco_api.utils import search_utils
        
        # Access the search client that was already created
        search_client = master_client.search
        
        logger.debug(f"Advanced search for: '{safe_query_display}', sort: {safe_sort_field_display} ({'asc' if actual_sort_ascending else 'desc'})")
        
        if ctx:
            await ctx.report_progress(0.3)
        
        # Use search_utils.advanced_search() utility with existing search_client
        if ctx:
            await ctx.report_progress(0.5)
        
        try:
            # Use search_utils.advanced_search() with existing search_client that has working authentication
            search_results = search_utils.advanced_search(
                search_client,
                actual_query,
                max_items=actual_max_results,
                sort_by=actual_sort_field,
                sort_ascending=actual_sort_ascending
            )
            
            if not search_results:
                logger.debug("Advanced search returned None, attempting fallback to simple search")
                search_results = search_utils.simple_search(search_client, actual_query, max_items=actual_max_results)
                
            # Check for different possible SearchResult structures
            if not search_results:
                logger.error(f"No search results returned")
                return safe_format_output(f"ERROR: Advanced search failed - no results returned")
                
            # Try to get entries from different possible structures
            entries = []
            
            if hasattr(search_results, 'list') and search_results.list and hasattr(search_results.list, 'entries'):
                entries = search_results.list.entries if search_results.list else []
                logger.debug(f"Found entries using list attribute: {len(entries)}")
            elif hasattr(search_results, 'list_') and search_results.list_ and hasattr(search_results.list_, 'entries'):
                entries = search_results.list_.entries if search_results.list_ else []
                logger.debug(f"Found entries using list_ attribute: {len(entries)}")
            elif hasattr(search_results, 'entries'):
                entries = search_results.entries
                logger.debug(f"Found entries using direct entries attribute: {len(entries)}")
            elif hasattr(search_results, 'results'):
                entries = search_results.results
                logger.debug(f"Found entries using results attribute: {len(entries)}")
            else:
                logger.error(f"SearchResult structure not recognized")
                return safe_format_output(f"ERROR: Advanced search failed - unknown SearchResult structure")
                
        except Exception as e:
            logger.error(f"Advanced search failed: {e}")
            # Try fallback to simple search
            try:
                logger.debug("Attempting fallback to simple search after advanced search error")
                search_results = search_utils.simple_search(search_client, actual_query, max_items=actual_max_results)
                if not search_results:
                    return safe_format_output(f"ERROR: Both advanced and simple search failed: {str(e)}")
                # Extract entries from simple search result
                entries = []
                if hasattr(search_results, 'list_') and search_results.list_ and hasattr(search_results.list_, 'entries'):
                    entries = search_results.list_.entries if search_results.list_ else []
                    logger.debug(f"Fallback simple search found {len(entries)} results")
                else:
                    return safe_format_output(f"ERROR: Both advanced and simple search failed: {str(e)}")
            except Exception as fallback_error:
                logger.error(f"Fallback simple search also failed: {fallback_error}")
                return safe_format_output(f"ERROR: Advanced search failed: {str(e)}")
        
        if ctx:
            await ctx.report_progress(1.0)
        
        # Process final results
        if entries:
            logger.info(f"Found {len(entries)} search results")
            result_text = f"Found {len(entries)} item(s) matching '{safe_query_display}':\n\n"
            
            for i, entry in enumerate(entries, 1):
                # Handle different possible entry structures
                node = None
                if isinstance(entry, dict):
                    if 'entry' in entry:
                        node = entry['entry']
                    elif 'name' in entry:  # Direct node structure
                        node = entry
                    else:
                        logger.debug(f"Unknown entry structure: {entry}")
                        continue
                elif hasattr(entry, 'entry'):  # ResultSetRowEntry object
                    node = entry.entry
                else:
                    logger.debug(f"Entry is not a dict or ResultSetRowEntry: {type(entry)}")
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
        error_msg = f"ERROR: Advanced search failed: {str(e)}"
        if ctx:
            await ctx.error(safe_format_output(error_msg))
        return safe_format_output(error_msg) 
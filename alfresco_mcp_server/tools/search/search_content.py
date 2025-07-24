"""
Content search tool for Alfresco MCP Server.
Each tool is self-contained with its own validation, business logic, and env handling.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def search_content_impl(
    search_query: str,
    max_results: int = 25,
    node_type: str = "cm:content",
    ctx: Optional[Context] = None
) -> str:
    """Search for content in Alfresco repository.
    
    Args:
        search_query: Search query string
        max_results: Maximum number of results to return (default: 25)
        node_type: Type of nodes to search for (default: "cm:content" - searches documents)
        ctx: MCP context for progress reporting
    
    Returns:
        Formatted search results
    """
    # Parameter validation and extraction
    try:
        # Extract parameters with fallback handling
        if hasattr(search_query, 'value'):
            actual_query = str(search_query.value)
        else:
            actual_query = str(search_query)
            
        if hasattr(max_results, 'value'):
            actual_max_results = int(max_results.value)
        else:
            actual_max_results = int(max_results)
            
        if hasattr(node_type, 'value'):
            actual_node_type = str(node_type.value)
        else:
            actual_node_type = str(node_type)
        
        # Default to cm:content if empty
        if not actual_node_type.strip():
            actual_node_type = "cm:content"
        
        # Clean and normalize for display (prevent Unicode encoding issues)
        safe_query_display = safe_format_output(str(actual_query))
        safe_node_type_display = safe_format_output(str(actual_node_type))
        
    except Exception as e:
        logger.error(f"Parameter extraction error: {e}")
        return safe_format_output(f"ERROR: Parameter error: {str(e)}")
    
    if not actual_query.strip():
        return """Content Search Tool

Usage: Provide a search query to search Alfresco repository content.

Example searches:
- admin (finds items with 'admin' in name or content)
- name:test* (finds items with names starting with 'test')
- modified:[2024-01-01 TO 2024-12-31] (finds items modified in 2024)
- TYPE:"cm:content" (finds all documents)
- TYPE:"cm:folder" (finds all folders)

Search uses AFTS (Alfresco Full Text Search) syntax for flexible content discovery.
By default, searches for documents (cm:content) unless a different type is specified.
"""
    
    if ctx:
        await ctx.info(safe_format_output(f"Content search for: '{safe_query_display}'"))
        await ctx.report_progress(0.0)
    
    try:
        # Get all clients that ensure_connection() already created
        master_client = await ensure_connection()
        
        # Import search_utils
        from python_alfresco_api.utils import search_utils
        
        # Access the search client that was already created
        search_client = master_client.search
        
        logger.info(f"Content search for: '{safe_query_display}', type: '{safe_node_type_display}'")
        
        if ctx:
            await ctx.report_progress(0.3)
        
        # Build search query to include node_type filter
        final_query = actual_query
        
        # Add node_type filter if not already in query
        has_type_in_query = "TYPE:" in final_query.upper()
        if not has_type_in_query:
            if final_query == "*":
                final_query = f'TYPE:"{actual_node_type}"'
            else:
                final_query = f'({final_query}) AND TYPE:"{actual_node_type}"'
        
        # Use the correct working pattern: search_utils.simple_search with existing search_client
        try:
            search_results = search_utils.simple_search(search_client, final_query, max_items=actual_max_results)
            
            if search_results and hasattr(search_results, 'list_'):
                entries_list = search_results.list_.entries if search_results.list_  else []
                logger.info(f"Found {len(entries_list)} content search results")
                
                if ctx:
                    await ctx.report_progress(1.0)
                
                if not entries_list:
                    return "0"
                
                result_text = f"Found {len(entries_list)} item(s) matching the search query:\n\n"
                
                for i, entry in enumerate(entries_list, 1):
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
                return safe_format_output(f"ERROR: Content search failed - invalid response from Alfresco")
                
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return safe_format_output(f"ERROR: Content search failed: {str(e)}")
        
    except Exception as e:
        # Preserve Unicode characters in error messages
        error_msg = f"ERROR: Content search failed: {str(e)}"
        if ctx:
            await ctx.error(safe_format_output(error_msg))
        return safe_format_output(error_msg)

    if ctx:
        await ctx.info(safe_format_output("Content search completed!")) 
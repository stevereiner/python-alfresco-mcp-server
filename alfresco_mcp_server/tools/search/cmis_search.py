"""
CMIS search tool for Alfresco MCP Server.
Each tool is self-contained with its own validation, business logic, and env handling.
"""
import logging
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def cmis_search_impl(
    cmis_query: str,
    max_results: int = 25,
    ctx: Optional[Context] = None
) -> str:
    """Search using CMIS SQL syntax.
    
    Args:
        cmis_query: CMIS SQL query string
        max_results: Maximum number of results to return (default: 25)
        ctx: MCP context for progress reporting
    
    Returns:
        Formatted search results from CMIS query
    """
    # Parameter validation and extraction
    try:
        # Extract parameters with fallback handling
        if hasattr(cmis_query, 'value'):
            actual_query = str(cmis_query.value)
        else:
            actual_query = str(cmis_query)
            
        if hasattr(max_results, 'value'):
            actual_max_results = int(max_results.value)
        else:
            actual_max_results = int(max_results)
        
        # Clean and normalize for display (preserve Unicode characters)
        safe_query_display = str(actual_query)
        
    except Exception as e:
        logger.error(f"Parameter extraction error: {e}")
        return f"ERROR: Parameter error: {str(e)}"
    
    if not actual_query.strip():
        return """CMIS Search Tool

Usage: Provide a CMIS SQL query to search Alfresco repository.

Example CMIS queries:
- SELECT * FROM cmis:document WHERE cmis:name LIKE 'test%'
- SELECT * FROM cmis:folder WHERE CONTAINS('project')
- SELECT * FROM cmis:document WHERE cmis:creationDate > '2024-01-01T00:00:00.000Z'
- SELECT * FROM cmis:document WHERE cmis:contentStreamMimeType = 'application/pdf'

CMIS provides precise SQL queries for exact matching and filtering.
"""
    
    if ctx:
        await ctx.info(safe_format_output(f"CMIS search for: '{safe_query_display}'"))
        await ctx.report_progress(0.0)
    
    try:
        # Get all clients that ensure_connection() already created
        master_client = await ensure_connection()
        
        # Access the search client that was already created (same as other search tools)
        search_client = master_client.search
        
        logger.info(f"CMIS search for: '{safe_query_display}'")
        
        if ctx:
            await ctx.report_progress(0.3)
        
        # Use same pattern as other search tools but with CMIS language
        try:
            # Import the SearchRequest model for CMIS queries
            from python_alfresco_api.raw_clients.alfresco_search_client.search_client.models import SearchRequest, RequestQuery, RequestPagination, RequestQueryLanguage
            from python_alfresco_api.raw_clients.alfresco_search_client.search_client.types import UNSET
            
            # Create CMIS search request (same pattern as search_utils.simple_search but with CMIS language)
            request_query = RequestQuery(
                query=actual_query,
                language=RequestQueryLanguage.CMIS  # Use CMIS instead of AFTS
            )
            
            request_pagination = RequestPagination(
                max_items=actual_max_results,
                skip_count=0
            )
            
            search_request = SearchRequest(
                query=request_query,
                paging=request_pagination,
                include=UNSET
            )
            
            # Use same pattern as search_utils.simple_search
            search_results = search_client.search.search(search_request)
            
            if search_results and hasattr(search_results, 'list_'):
                entries_list = search_results.list_.entries if search_results.list_ else []
                logger.info(f"Found {len(entries_list)} CMIS search results")
                
                if ctx:
                    await ctx.report_progress(1.0)
                
                if not entries_list:
                    return "0"
                
                result_text = f"Found {len(entries_list)} item(s) matching the CMIS query:\n\n"
                
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
                            node_type = str(node.get('nodeType', 'Unknown'))
                            created_at = str(node.get('createdAt', 'Unknown'))
                        else:
                            # ResultNode object - access attributes directly
                            name = str(getattr(node, 'name', 'Unknown'))
                            node_id = str(getattr(node, 'id', 'Unknown'))
                            node_type = str(getattr(node, 'node_type', 'Unknown'))
                            created_at = str(getattr(node, 'created_at', 'Unknown'))
                        
                        # Clean JSON-friendly formatting (no markdown syntax)
                        # Apply safe formatting to individual fields to prevent emoji encoding issues
                        safe_name = safe_format_output(name)
                        safe_node_id = safe_format_output(node_id)
                        safe_node_type = safe_format_output(node_type)
                        safe_created_at = safe_format_output(created_at)
                        
                        result_text += f"{i}. {safe_name}\n"
                        result_text += f"   - ID: {safe_node_id}\n"
                        result_text += f"   - Type: {safe_node_type}\n"
                        result_text += f"   - Created: {safe_created_at}\n\n"
                
                return safe_format_output(result_text)
            else:
                return safe_format_output(f"ERROR: CMIS search failed - invalid response from Alfresco")
                
        except Exception as e:
            logger.error(f"CMIS search failed: {e}")
            return safe_format_output(f"ERROR: CMIS search failed: {str(e)}")
        
    except Exception as e:
        # Preserve Unicode characters in error messages
        error_msg = f"ERROR: CMIS search failed: {str(e)}"
        if ctx:
            await ctx.error(safe_format_output(error_msg))
        return safe_format_output(error_msg)

    if ctx:
        await ctx.info(safe_format_output("CMIS search completed!")) 
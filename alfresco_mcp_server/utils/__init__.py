# Utilities module for Alfresco MCP Server

from .connection import (
    get_alfresco_config,
    get_connection,
    get_search_utils,
    get_node_utils,
)

from .file_type_analysis import (
    detect_file_extension_from_content,
    analyze_content_type,
)

from .json_utils import (
    make_json_safe,
    safe_format_output,
    escape_unicode_for_json,
)

__all__ = [
    # Connection utilities
    "get_alfresco_config",
    "get_connection", 
    "get_search_utils",
    "get_node_utils",
    # File type analysis
    "detect_file_extension_from_content",
    "analyze_content_type",
    # JSON utilities
    "make_json_safe",
    "safe_format_output",
    "escape_unicode_for_json",
] 
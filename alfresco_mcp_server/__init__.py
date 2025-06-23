"""
Alfresco MCP Server

Model Context Protocol server for Alfresco Content Services.
Provides AI-native access to Alfresco content management operations.
"""

__version__ = "0.1.0"
__title__ = "Alfresco MCP Server"
__description__ = "Model Context Protocol server for Alfresco Content Services"

from .server import AlfrescoMCPServer
from .config import AlfrescoConfig

__all__ = ["AlfrescoMCPServer", "AlfrescoConfig"] 
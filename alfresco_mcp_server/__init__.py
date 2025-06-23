"""
MCP Server for Alfresco

Model Context Protocol server for Alfresco Content Services.
Provides AI-native access to Alfresco content management operations.
"""

__version__ = "1.0.0"
__title__ = "MCP Server for Alfresco"
__description__ = "Model Context Protocol server for Alfresco Content Services"

from .config import AlfrescoConfig

__all__ = ["AlfrescoConfig"] 
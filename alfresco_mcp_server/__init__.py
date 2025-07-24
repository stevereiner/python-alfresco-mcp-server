"""
MCP Server for Alfresco

Model Context Protocol server for Alfresco Content Services.
Provides AI-native access to Alfresco content management and search operations.
"""

__version__ = "1.1.0"
__title__ = "MCP Server for Alfresco"
__description__ = "Model Context Protocol server for Alfresco Content Services"

from .config import AlfrescoConfig, load_config

# Import subpackages to make them available
from . import tools
from . import resources  
from . import prompts
from . import utils

__all__ = [
    "AlfrescoConfig", 
    "load_config",
    "tools",
    "resources", 
    "prompts",
    "utils",
] 
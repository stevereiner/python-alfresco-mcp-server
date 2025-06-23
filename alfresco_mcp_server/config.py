"""
Configuration management for MCP Server for Alfresco.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class AlfrescoConfig(BaseModel):
    """Configuration for MCP Server for Alfresco."""
    
    # Alfresco server connection
    alfresco_url: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_URL", "http://localhost:8080"),
        description="Alfresco server URL"
    )
    
    # Authentication
    username: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_USERNAME", "admin"),
        description="Alfresco username"
    )
    
    password: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_PASSWORD", "admin"),
        description="Alfresco password"
    )
    
    # Connection settings
    verify_ssl: bool = Field(
        default_factory=lambda: os.getenv("ALFRESCO_VERIFY_SSL", "false").lower() == "true",
        description="Verify SSL certificates"
    )
    
    timeout: int = Field(
        default_factory=lambda: int(os.getenv("ALFRESCO_TIMEOUT", "30")),
        description="Request timeout in seconds"
    )
    
    # MCP Server settings
    server_name: str = Field(
        default="python-alfresco-mcp-server",
        description="MCP server name"
    )
    
    server_version: str = Field(
        default="1.0.0",
        description="MCP server version"
    )
    
    # FastAPI settings (for HTTP transport)
    fastapi_host: str = Field(
        default_factory=lambda: os.getenv("FASTAPI_HOST", "localhost"),
        description="FastAPI host"
    )
    
    fastapi_port: int = Field(
        default_factory=lambda: int(os.getenv("FASTAPI_PORT", "8000")),
        description="FastAPI port"
    )
    
    fastapi_prefix: str = Field(
        default_factory=lambda: os.getenv("FASTAPI_PREFIX", "/mcp"),
        description="FastAPI URL prefix"
    )
    
    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level"
    )
    
    # Content settings
    max_file_size: int = Field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "100000000")),  # 100MB
        description="Maximum file size for uploads in bytes"
    )
    
    allowed_extensions: list[str] = Field(
        default_factory=lambda: [
            ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", 
            ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif", 
            ".zip", ".xml", ".json", ".csv"
        ],
        description="Allowed file extensions for uploads"
    )
    
    class Config:
        env_prefix = "ALFRESCO_"
        case_sensitive = False
        
    def model_post_init(self, __context) -> None:
        """Normalize URLs after initialization."""
        if self.alfresco_url.endswith("/"):
            self.alfresco_url = self.alfresco_url.rstrip("/")


def load_config() -> AlfrescoConfig:
    """Load configuration from environment variables and defaults."""
    return AlfrescoConfig() 
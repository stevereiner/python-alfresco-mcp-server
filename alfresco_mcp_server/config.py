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
    
    # Authentication method: basic | ticket | oauth2
    auth_method: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_AUTH_METHOD", "basic").lower(),
        description="Alfresco auth method: basic | ticket | oauth2"
    )

    # Authentication (basic / ticket)
    username: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_USERNAME", "admin"),
        description="Alfresco username"
    )

    password: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_PASSWORD", "admin"),
        description="Alfresco password"
    )

    ticket: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_TICKET"),
        description="Pre-obtained Alfresco login ticket; with auth_method=ticket it is "
                    "used as-is instead of being fetched from username/password"
    )

    # OAuth2 (auth_method=oauth2) — Alfresco Identity Service / any OIDC IdP
    oauth2_client_id: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_CLIENT_ID"),
        description="OAuth2 client id"
    )
    oauth2_client_secret: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_CLIENT_SECRET"),
        description="OAuth2 client secret"
    )
    oauth2_token_endpoint: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_TOKEN_ENDPOINT"),
        description="OAuth2 token endpoint URL"
    )
    oauth2_grant_type: str = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_GRANT_TYPE", "client_credentials"),
        description="OAuth2 grant type: client_credentials | refresh_token"
    )
    oauth2_scope: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_SCOPE"),
        description="OAuth2 scope"
    )
    oauth2_access_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_ACCESS_TOKEN"),
        description="Pre-obtained OAuth2 access token (optional)"
    )
    oauth2_refresh_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("ALFRESCO_OAUTH2_REFRESH_TOKEN"),
        description="OAuth2 refresh token (optional)"
    )
    
    # Connection settings
    verify_ssl: bool = Field(
        default_factory=lambda: os.getenv("ALFRESCO_VERIFY_SSL", "true").lower() == "true",
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

# Global config instance for import
config = load_config() 
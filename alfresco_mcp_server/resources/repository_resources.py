"""
Repository resources for Alfresco MCP Server.
Self-contained resources for repository information, health, stats, and configuration.
Returns data or indicates when unavailable.
"""
import json
import logging
import os

from python_alfresco_api.client_factory import ClientFactory
from ..utils.connection import ensure_connection, get_client_factory
from ..utils.json_utils import safe_format_output
    
logger = logging.getLogger(__name__)


async def get_repository_info_impl() -> str:
    """Get Alfresco repository information using Discovery API.
    Returns comprehensive repository details or connection status.
    """
    try:
        await ensure_connection()
        client_factory: ClientFactory = await get_client_factory()
        
        logger.info("Getting repository information via Discovery API")
        
        # Use the working pattern from test script - high-level API
        discovery_client = client_factory.create_discovery_client()
        
        # Check if discovery client has the discovery attribute (working pattern from test)
        if not hasattr(discovery_client, 'discovery'):
            logger.warning("Discovery client does not have discovery attribute")
            return safe_format_output(f"""⚠️ **Repository Information - Discovery Client Unavailable**

**Status**: Discovery client initialization failed

**Available Information**:
🔗 **Server**: {os.getenv('ALFRESCO_URL', 'http://localhost:8080')}
👤 **Connected as**: {os.getenv('ALFRESCO_USERNAME', 'admin')}
❌ **Discovery API**: Client not available

**Note**: This could indicate:
- Authentication issues
- Network connectivity problems
- Server configuration issues

**Recommendation**: Check connection settings and server status.""")
        
        # Get repository information using high-level Discovery API (working pattern from test)
        repo_info = discovery_client.discovery.get_repository_information()
        
        # Handle None response (HTTP 501 - Discovery API disabled)
        if repo_info is None:
            logger.warning("Discovery API is disabled on this Alfresco instance (returned None)")
            return safe_format_output(f"""⚠️ **Repository Information - Discovery API Disabled**

**Status**: Discovery API is disabled on this Alfresco instance (HTTP 501)

**Available Information**:
🔗 **Server**: {os.getenv('ALFRESCO_URL', 'http://localhost:8080')}
👤 **Connected as**: {os.getenv('ALFRESCO_USERNAME', 'admin')}
✅ **Core API**: Available (connection successful)
❌ **Discovery API**: Disabled by administrator

**Note**: The Discovery API provides detailed repository information including:
- Version and edition details
- License information and entitlements  
- Installed modules and their versions
- Repository status and capabilities

**Administrator Action Required**: To enable Discovery API, the Alfresco administrator needs to:
1. Enable the Discovery API in the repository configuration
2. Restart the Alfresco service
3. Ensure proper permissions are configured

**Alternative**: Use Core API tools for basic repository operations.""")
        
        if repo_info and hasattr(repo_info, 'entry'):
            entry = repo_info.entry
            repository = getattr(entry, 'repository', {})
            
            # Build comprehensive repository information
            result = "🏢 **Alfresco Repository Information**\n\n"
            
            # Repository ID and Edition
            repo_id = getattr(repository, 'id', 'Unknown')
            edition = getattr(repository, 'edition', 'Unknown')
            logger.info(f"✅ Retrieved repository info: {edition} edition")
            result += f"🆔 **Repository ID**: {repo_id}\n"
            result += f"🏷️ **Edition**: {edition}\n\n"
            
            # Version Information
            version_info = getattr(repository, 'version', {})
            if hasattr(version_info, 'major'):
                result += "📦 **Version Details**:\n"
                result += f"   • Major: {getattr(version_info, 'major', 'Unknown')}\n"
                result += f"   • Minor: {getattr(version_info, 'minor', 'Unknown')}\n"
                result += f"   • Patch: {getattr(version_info, 'patch', 'Unknown')}\n"
                result += f"   • Hotfix: {getattr(version_info, 'hotfix', 'Unknown')}\n"
                result += f"   • Schema: {getattr(version_info, 'schema', 'Unknown')}\n"
                result += f"   • Label: {getattr(version_info, 'label', 'Unknown')}\n"
                result += f"   • Display: {getattr(version_info, 'display', 'Unknown')}\n\n"
            
            # Repository Status
            status_info = getattr(repository, 'status', {})
            if hasattr(status_info, 'is_read_only'):
                result += "STATUS **Repository Status**:\n"
                result += f"   • Read Only: {'Yes' if getattr(status_info, 'is_read_only', False) else 'No'}\n"
                result += f"   • Audit Enabled: {'Yes' if getattr(status_info, 'is_audit_enabled', False) else 'No'}\n"
                result += f"   • Quick Share Enabled: {'Yes' if getattr(status_info, 'is_quick_share_enabled', False) else 'No'}\n"
                result += f"   • Thumbnail Generation: {'Yes' if getattr(status_info, 'is_thumbnail_generation_enabled', False) else 'No'}\n\n"
            
            # License Information
            license_info = getattr(repository, 'license', {})
            if hasattr(license_info, 'issued_at'):
                result += "📄 **License Information**:\n"
                result += f"   • Issued At: {getattr(license_info, 'issued_at', 'Unknown')}\n"
                result += f"   • Expires At: {getattr(license_info, 'expires_at', 'Unknown')}\n"
                result += f"   • Remaining Days: {getattr(license_info, 'remaining_days', 'Unknown')}\n"
                result += f"   • Holder: {getattr(license_info, 'holder', 'Unknown')}\n"
                result += f"   • Mode: {getattr(license_info, 'mode', 'Unknown')}\n"
                
                # License Entitlements
                entitlements = getattr(license_info, 'entitlements', {})
                if hasattr(entitlements, 'max_users'):
                    result += f"   • Max Users: {getattr(entitlements, 'max_users', 'Unknown')}\n"
                    result += f"   • Max Documents: {getattr(entitlements, 'max_docs', 'Unknown')}\n"
                    result += f"   • Cluster Enabled: {'Yes' if getattr(entitlements, 'is_cluster_enabled', False) else 'No'}\n"
                    result += f"   • Cryptodoc Enabled: {'Yes' if getattr(entitlements, 'is_cryptodoc_enabled', False) else 'No'}\n"
                result += "\n"
            
            # Modules Information
            modules = getattr(repository, 'modules', [])
            if modules and len(modules) > 0:
                result += f"🧩 **Installed Modules** ({len(modules)} total):\n"
                for i, module in enumerate(modules[:10], 1):  # Show first 10 modules
                    module_id = getattr(module, 'id', 'Unknown')
                    module_title = getattr(module, 'title', 'Unknown')
                    module_version = getattr(module, 'version', 'Unknown')
                    module_state = getattr(module, 'install_state', 'Unknown')
                    result += f"   {i}. **{module_title}** (ID: {module_id})\n"
                    result += f"      • Version: {module_version}\n"
                    result += f"      • State: {module_state}\n"
                    
                    install_date = getattr(module, 'install_date', None)
                    if install_date:
                        result += f"      • Installed: {install_date}\n"
                    result += "\n"
                
                if len(modules) > 10:
                    result += f"   *... and {len(modules) - 10} more modules*\n\n"
            
            # Connection Details
            result += "🔗 **Connection Details**:\n"
            result += f"   • Server: {os.getenv('ALFRESCO_URL', 'http://localhost:8080')}\n"
            result += f"   • Connected as: {os.getenv('ALFRESCO_USERNAME', 'admin')}\n"
            result += f"   • Data Source: Discovery API (High-Level)\n"
            
            return safe_format_output(result)
        
    except Exception as discovery_error:
        error_str = str(discovery_error)
        
        # Check if Discovery API is disabled (501 error)
        if "501" in error_str or "Discovery is disabled" in error_str:
            logger.warning("Discovery API is disabled on this Alfresco instance")
            return safe_format_output(f"""WARNING: **Repository Information - Discovery API Disabled**

**Status**: Discovery API is disabled on this Alfresco instance (HTTP 501)

**Available Information**:
🔗 **Server**: {os.getenv('ALFRESCO_URL', 'http://localhost:8080')}
👤 **Connected as**: {os.getenv('ALFRESCO_USERNAME', 'admin')}
✅ **Core API**: Available (connection successful)
❌ **Discovery API**: Disabled by administrator

**Note**: The Discovery API provides detailed repository information including:
- Version and edition details
- License information and entitlements  
- Installed modules and their versions
- Repository status and capabilities

**Administrator Action Required**: To enable Discovery API, the Alfresco administrator needs to:
1. Enable the Discovery API in the repository configuration
2. Restart the Alfresco service
3. Ensure proper permissions are configured

**Alternative**: Use Core API tools for basic repository operations.""")
        else:
            # Other Discovery API errors
            logger.error(f"Discovery API failed: {error_str}")
            return safe_format_output(f"""ERROR: **Repository Information Unavailable**

**Error**: Discovery API failed
**Details**: {error_str}

🔗 **Server**: {os.getenv('ALFRESCO_URL', 'http://localhost:8080')}
👤 **Connected as**: {os.getenv('ALFRESCO_USERNAME', 'admin')}

**Possible Causes**:
- Discovery API endpoint not available
- Insufficient permissions
- Network connectivity issues
- Repository service issues
**Recommendation**: Check server logs and verify Discovery API availability.""")

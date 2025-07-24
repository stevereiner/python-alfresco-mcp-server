"""
Download document tool for Alfresco MCP Server.
Self-contained tool for downloading documents from Alfresco repository.
"""
import logging
import httpx
import base64
import os
import pathlib
from datetime import datetime
from typing import Optional
from fastmcp import Context
from ...utils.connection import get_core_client
from ...config import config
from ...utils.file_type_analysis import analyze_content_type
from ...utils.json_utils import safe_format_output

logger = logging.getLogger(__name__)


async def download_document_impl(
    node_id: str, 
    save_to_disk: bool = True,
    attachment: bool = True,
    ctx: Optional[Context] = None
) -> str:
    """Download a document from Alfresco repository.
    
    Args:
        node_id: Node ID of the document to download
        save_to_disk: If True, saves file to Downloads folder (default, AI-friendly). 
                     If False, returns base64 content (testing/debugging)
        attachment: If True, downloads as attachment (default). If False, opens for preview in browser
        ctx: MCP context for progress reporting
    
    Returns:
        File path and confirmation if save_to_disk=True, or base64 content if False
    """
    if ctx:
        await ctx.info(f"Downloading document: {node_id}")
        await ctx.report_progress(0.0)
    
    try:
        logger.info(f"Starting download: node {node_id}")
        core_client = await get_core_client()
        
        if ctx:
            await ctx.info("Getting node information...")
            await ctx.report_progress(0.3)
        
        # Clean the node ID (remove any URL encoding or extra characters)
        clean_node_id = node_id.strip()
        if clean_node_id.startswith('alfresco://'):
            # Extract node ID from URI format
            clean_node_id = clean_node_id.split('/')[-1]
        
        # Get node information first to validate it exists and get filename
        node_response = core_client.nodes.get(node_id=clean_node_id)
        
        if not hasattr(node_response, 'entry'):
            return safe_format_output(f"❌ Failed to get node information for: {clean_node_id}")
        
        node_info = node_response.entry
        filename = getattr(node_info, 'name', f"document_{clean_node_id}")
        node_type = getattr(node_info, 'node_type', 'Unknown')
        
        # Check if it's actually a file
        is_file = getattr(node_info, 'is_file', False)
        if not is_file:
            return safe_format_output(f"❌ Node {clean_node_id} is not a file (it's a {node_type})")
        
        # Clean filename - strip whitespace and remove invalid characters for file paths
        filename = filename.strip()
        # Remove newlines and other control characters
        filename = filename.replace('\n', '').replace('\r', '').replace('\t', '')
        # Remove or replace invalid Windows filename characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Ensure filename is not empty
        if not filename or filename == '_':
            filename = f"document_{clean_node_id}"
        
        if ctx:
            await ctx.info(f"Downloading content for: {filename}")
            await ctx.report_progress(0.7)
        
        # Get file content using authenticated HTTP client from core client
        # Build correct content URL based on config
        if config.alfresco_url.endswith('/alfresco/api/-default-/public'):
            # Full API path provided
            content_url = f"{config.alfresco_url}/alfresco/versions/1/nodes/{clean_node_id}/content"
        elif config.alfresco_url.endswith('/alfresco/api'):
            # Base API path provided
            content_url = f"{config.alfresco_url}/-default-/public/alfresco/versions/1/nodes/{clean_node_id}/content"
        else:
            # Base server URL provided
            content_url = f"{config.alfresco_url}/alfresco/api/-default-/public/alfresco/versions/1/nodes/{clean_node_id}/content"
        
        # Use the authenticated HTTP client from core client (ensure initialization)
        if not core_client.is_initialized:
            return safe_format_output("❌ Error: Alfresco server unavailable")
        # Use httpx_client property directly on AlfrescoCoreClient
        http_client = core_client.httpx_client
        
        # Add attachment parameter if specified
        params = {}
        if not attachment:
            params['attachment'] = 'false'
        
        logger.debug(f"Downloading content from: {content_url}")
        response = http_client.get(content_url, params=params)
        response.raise_for_status()
        content_bytes = response.content
        logger.info(f"Downloaded {len(content_bytes)} bytes for {filename}")
        
        if ctx:
            await ctx.report_progress(0.9)
        
        file_size = len(content_bytes)
        # Fix: ContentInfo object doesn't have .get() method - access mime_type attribute directly
        mime_type = 'application/octet-stream'
        if hasattr(node_info, 'content') and node_info.content:
            mime_type = getattr(node_info.content, 'mime_type', 'application/octet-stream')
        
        if save_to_disk:
            # AI-Client friendly: Save file to Downloads folder with content-aware handling
            
            # Create Downloads directory if it doesn't exist
            downloads_dir = pathlib.Path.home() / "Downloads"
            downloads_dir.mkdir(exist_ok=True)
            
            # Content-aware file handling
            file_extension = pathlib.Path(filename).suffix.lower()
            content_type_info = analyze_content_type(filename, mime_type, content_bytes)
            
            # Create smart filename with content type organization
            if content_type_info['category'] != 'other':
                category_dir = downloads_dir / content_type_info['category']
                category_dir.mkdir(exist_ok=True)
                downloads_dir = category_dir
            
            # Create unique filename with node ID to avoid conflicts
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                safe_filename = f"{name_parts[0]}_{clean_node_id}.{name_parts[1]}"
            else:
                safe_filename = f"{filename}_{clean_node_id}"
            
            file_path = downloads_dir / safe_filename
            
            # Write file to disk
            with open(file_path, 'wb') as f:
                f.write(content_bytes)
            
            logger.info(f"File saved: {filename} -> {file_path}")
            if ctx:
                await ctx.info(f"File saved to: {file_path}")
                await ctx.report_progress(1.0)
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            download_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Clean JSON-friendly formatting (no markdown syntax)
            result = f"📥 Document Downloaded Successfully!\n\n"
            result += f"📄 Name: {filename}\n"
            result += f"🆔 Node ID: {clean_node_id}\n"
            result += f"📏 Size: {size_str}\n"
            result += f"📄 MIME Type: {mime_type}\n"
            result += f"💾 Saved to: {file_path}\n"
            result += f"📁 Directory: {downloads_dir}\n"
            result += f"🕒 Downloaded: {download_time}\n\n"
            result += f"File saved to your Downloads folder for easy access.\n"
            result += f"You can now open, edit, or move the file as needed.\n"
            
            if content_type_info['category'] and content_type_info['category'].strip():
                result += f"📝 **Content Type**: {content_type_info['category']}\n"
            
            # Content-aware suggestions
            if content_type_info['suggestions']:
                result += f"**Content-Aware Suggestions:**\n"
                for suggestion in content_type_info['suggestions']:
                    result += f"   {suggestion}\n"
                result += "\n"
            
            result += f"**Organized in**: {content_type_info['category']} folder\n"
            result += f"**Tip**: File is automatically organized by content type for easier management!"
            
            return safe_format_output(result)
        else:
            # Testing/debugging mode: Return base64 content
            base64_content = base64.b64encode(content_bytes).decode('ascii')
            
            result = f"**Downloaded: {filename}**\n\n"
            result += f"- **Node ID**: {clean_node_id}\n"
            result += f"- **Size**: {file_size} bytes\n"
            result += f"- **MIME Type**: {mime_type}\n\n"
            result += f"**Base64 Content**:\n```\n{base64_content[:200]}{'...' if len(base64_content) > 200 else ''}\n```\n"
            result += f"\n*Note: Content is base64 encoded. Full content length: {len(base64_content)} characters*"
            
            return safe_format_output(result)
        
    except Exception as e:
        error_msg = f"❌ Failed to download document {node_id}: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return safe_format_output(error_msg) 
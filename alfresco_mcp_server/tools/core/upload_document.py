"""
Upload document tool for Alfresco MCP Server.
Self-contained tool for uploading documents to Alfresco repository.
"""
import logging
import os
import base64
import tempfile
from typing import Optional
from fastmcp import Context

from ...utils.connection import ensure_connection, get_core_client
from ...utils.json_utils import safe_format_output
from ...utils.file_type_analysis import detect_file_extension_from_content

logger = logging.getLogger(__name__)


# Add this TEMPORARILY to your MCP server code:
def create_and_upload_file_share_style_temp(
    core_client,
    file_path,
    parent_id="-my-",
    filename=None,
    description=None,
    custom_title=None
):
    """
    TEMPORARY: Share-style upload until next python-alfresco-api release.
    Creates version 1.0 with full path as title (for real files) or custom title (for base64).
    """
    from pathlib import Path
    from python_alfresco_api.utils import content_utils
    
    file_path_obj = Path(file_path)
    upload_filename = filename or file_path_obj.name
    
    # Build properties with appropriate title
    if custom_title:
        # Use custom title for base64 uploads (just filename, not temp path)
        properties = {"cm:title": custom_title}
    else:
        # Use full path for real file uploads (Share-style behavior)
        properties = {"cm:title": str(file_path_obj)}
    
    if description:
        properties["cm:description"] = description
    
    # Use existing content_utils.upload_file (already in current package)
    return content_utils.upload_file(
        core_client=core_client,
        file_path=file_path_obj,
        parent_id=parent_id,
        filename=upload_filename,
        description=description,
        properties=properties,
        auto_rename=True
    )


async def upload_document_impl(
    file_path: str = "",
    base64_content: str = "",
    parent_id: str = "-shared-",
    description: str = "",
    ctx: Optional[Context] = None
) -> str:
    """Upload a document to Alfresco using Share-style behavior.
    
    Args:
        file_path: Path to the file to upload (alternative to base64_content)
        base64_content: Base64 encoded file content (alternative to file_path)
        parent_id: Parent folder ID (default: shared folder)
        description: Document description (optional)
        ctx: MCP context for progress reporting
    
    Note:
        - Uploads as version 1.0 (matching Alfresco Share behavior)
        - Uses full file path as title (matching Alfresco Share behavior)
        - Original filename is preserved automatically
        - For base64 uploads: content type detection and auto-naming
        - Cross-platform support: Windows paths with quotes, macOS ~/path expansion, Linux XDG directories
        - File extension detection works on all platforms (including macOS hidden extensions)
        - Linux filesystem case-sensitivity and permission handling
    
    Returns:
        Upload confirmation with document details
    """
    if ctx:
        if file_path:
            await ctx.info(f">> Uploading document from '{file_path}' to {parent_id}")
        else:
            await ctx.info(f">> Uploading base64 content to {parent_id}")
        await ctx.info("Validating file and parameters...")
        await ctx.report_progress(0.1)
    
    # Determine upload mode and validate
    use_base64 = bool(base64_content.strip())
    use_file_path = bool(file_path.strip())
    
    if not use_base64 and not use_file_path:
        return "ERROR: Must provide either file_path or base64_content"
    
    if use_base64 and use_file_path:
        return "ERROR: Cannot use both file_path and base64_content - choose one"
    
    # Variables for upload
    actual_file_path = None
    temp_file_path = None
    final_filename = None
    
    try:
        if use_file_path:
            # Handle file path upload - cross-platform path handling
            cleaned_file_path = file_path.strip().strip('"').strip("'")
            
            # Handle macOS/Unix path expansion (~/Documents, etc.)
            if cleaned_file_path.startswith('~'):
                cleaned_file_path = os.path.expanduser(cleaned_file_path)
            
            abs_file_path = os.path.abspath(cleaned_file_path)
            
            if not os.path.exists(abs_file_path):
                if os.path.exists(cleaned_file_path):
                    abs_file_path = cleaned_file_path
                else:
                    return f"ERROR: File not found: {cleaned_file_path} (cleaned from: {file_path})"
            
            if not os.path.isfile(abs_file_path):
                return f"ERROR: Path is not a file: {abs_file_path}"
            
            # Linux-specific: Check file permissions
            if not os.access(abs_file_path, os.R_OK):
                return f"ERROR: File not readable (permission denied): {abs_file_path}"
                
            actual_file_path = abs_file_path
            final_filename = os.path.basename(abs_file_path)
            
        else:
            # Handle base64 content upload - create temporary file
            try:
                file_content = base64.b64decode(base64_content)
                
                # Detect content type and create appropriate filename
                detected_extension = detect_file_extension_from_content(file_content)
                final_filename = f"uploaded_document{detected_extension or ''}"
                
                # Create temporary file with decoded content
                temp_fd, temp_file_path = tempfile.mkstemp(suffix=f"_{final_filename}")
                try:
                    with os.fdopen(temp_fd, 'wb') as temp_file:
                        temp_file.write(file_content)
                    actual_file_path = temp_file_path
                except Exception:
                    os.close(temp_fd)  # Close if writing failed
                    raise
                
            except Exception as decode_error:
                return f"ERROR: Invalid base64 content or file creation failed: {str(decode_error)}"
        
        if not actual_file_path:
            return "ERROR: No valid file path available for upload"
            
    except Exception as validation_error:
        return f"ERROR: Validation failed: {str(validation_error)}"
    
    try:
        # Ensure connection and get core client
        await ensure_connection()
        core_client = await get_core_client()
        
        if not core_client.is_initialized:
            return safe_format_output("❌ Error: Alfresco server unavailable")
        
        if ctx:
            await ctx.info("Creating and uploading document using Share-style approach...")
            await ctx.report_progress(0.5)
        
        logger.debug(f"Uploading '{final_filename}' to parent {parent_id} using Share-style function")
        
        # Determine title based on upload type
        custom_title = None
        if use_base64:
            # For base64 uploads, use just the filename as title (not temp file path)
            custom_title = final_filename
        # For file path uploads, let Share-style function use full path as title
        
        # Use Share-style upload function
        result = create_and_upload_file_share_style_temp(
            core_client=core_client,
            file_path=actual_file_path,
            parent_id=parent_id,
            filename=final_filename,
            description=description or None,
            custom_title=custom_title
        )
        
        # Extract essential info
        if hasattr(result, 'entry') and result.entry:
            node_id = getattr(result.entry, 'id', 'Unknown')
            node_name = getattr(result.entry, 'name', final_filename)
            logger.info(f"Upload completed: {node_name} -> {node_id}")
        else:
            logger.info(f"Upload completed successfully")
        
        if ctx:
            await ctx.info("Upload completed successfully!")
            await ctx.report_progress(1.0)

        # Format result for MCP with clean JSON-friendly output
        title_info = custom_title if custom_title else "Full file path"
        upload_type = "Base64 content" if use_base64 else "File path"
        
        success_result = f"""SUCCESS: Document Uploaded Successfully!

Name: {final_filename}
Parent: {parent_id}
Title: {title_info}
Description: {description or 'N/A'}
Upload Type: {upload_type}

Details: {result}

✨ Share-Style Upload: Version 1.0, proper title handling for upload type
✨ File path uploads: Full path as title (matching Alfresco Share)
✨ Base64 uploads: Clean filename as title (no temp file paths)"""
        
        return success_result
        
    except Exception as e:
        error_msg = f"ERROR: Document upload failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(f"Document upload failed: {e}")
        return error_msg
        
    finally:
        # Clean up temporary file if created
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {cleanup_error}") 
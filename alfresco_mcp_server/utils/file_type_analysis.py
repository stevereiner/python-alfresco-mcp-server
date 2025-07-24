"""
File type analysis utility for Alfresco MCP Server.
Provides content type analysis and suggestions for different file types.
"""
import pathlib
import mimetypes
from typing import Dict, List, Optional


def detect_file_extension_from_content(content: bytes) -> Optional[str]:
    """Detect file type from content and return appropriate extension.
    
    Args:
        content: Raw file content bytes
        
    Returns:
        File extension (e.g., '.pdf', '.txt', '.jpg') or None if unknown
    """
    if not content:
        return None
    
    # Check for common file signatures (magic numbers)
    if content.startswith(b'%PDF'):
        return '.pdf'
    elif content.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    elif content.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
        return '.gif'
    elif content.startswith(b'PK\x03\x04') or content.startswith(b'PK\x05\x06') or content.startswith(b'PK\x07\x08'):
        # ZIP-based formats (could be .zip, .docx, .xlsx, .pptx, etc.)
        # For simplicity, assume .zip unless we detect Office formats
        if b'word/' in content[:1024] or b'xl/' in content[:1024] or b'ppt/' in content[:1024]:
            # Likely Office document but hard to determine exact type
            return '.zip'  # Conservative choice
        return '.zip'
    elif content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        # Microsoft Office old format
        return '.doc'  # Could also be .xls, .ppt but .doc is most common
    elif content.startswith(b'<?xml') or content.startswith(b'\xef\xbb\xbf<?xml'):
        return '.xml'
    elif content.startswith(b'<!DOCTYPE html') or content.startswith(b'<html'):
        return '.html'
    elif content.startswith(b'{\n') or content.startswith(b'{"') or content.startswith(b'[\n') or content.startswith(b'[{'):
        return '.json'
    else:
        # Try to detect if it's text content
        try:
            # Try to decode as UTF-8 text
            text_content = content.decode('utf-8')
            # Check if it contains mostly printable characters
            printable_chars = sum(1 for c in text_content if c.isprintable() or c.isspace())
            if len(text_content) > 0 and printable_chars / len(text_content) > 0.8:
                return '.txt'
        except (UnicodeDecodeError, UnicodeError):
            pass
    
    # Unknown binary format
    return None


def analyze_content_type(filename: str, mime_type: str, content: bytes) -> dict:
    """Analyze file type and provide relevant suggestions.
    
    Args:
        filename: Name of the file
        mime_type: MIME type of the file
        content: File content as bytes
        
    Returns:
        Dictionary with category, suggestions, and file_size
    """
    file_size = len(content)
    
    # Get case-insensitive filename for macOS/Windows compatibility
    filename_lower = filename.lower()
    
    # Determine file category based on MIME type and extension
    if mime_type.startswith('image/'):
        category = 'images'
        suggestions = [
            "Can be used for thumbnails and previews",
            "Consider image optimization for web use"
        ]
    elif mime_type.startswith('video/') or mime_type.startswith('audio/'):
        category = 'media'
        suggestions = [
            "Large files may need streaming support",
            "Consider format compatibility for playback"
        ]
    elif mime_type in ['application/pdf', 'application/msword', 
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        category = 'documents'
        suggestions = [
            "PDF files support full-text search",
            ">> Consider using text extraction for searchable content",
            "Can be previewed in most browsers"
        ]
    elif mime_type in ['application/vnd.ms-excel',
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        category = 'documents'
        suggestions = [
            ">> Excel spreadsheet - can be opened with Excel or LibreOffice Calc",
            ">> May contain tracked changes or comments"
        ]
    elif mime_type in ['application/vnd.ms-powerpoint',
                      'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
        category = 'documents'
        suggestions = [
            "Presentation files support slide previews",
            "Consider extracting slide content for search"
        ]
    elif mime_type.startswith('text/') or 'javascript' in mime_type or 'json' in mime_type:
        if filename_lower.endswith(('.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb')):
            category = 'code'
            suggestions = [
                "Source code files support syntax highlighting",
                ">> Check contents before extraction for security",
                "Can be indexed for code search"
            ]
        else:
            category = 'documents'
            suggestions = [
                ">> Review for security before execution",
                ">> May require specific runtime environment"
            ]
    elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/gzip']:
        category = 'archives'
        suggestions = [
            "Archive contents can be extracted and indexed",
            ">> Check contents before extraction for security",
            "May contain multiple file types"
        ]
    else:
        category = 'other'
        suggestions = [
            "Unknown file type - review content manually",
            "Consider file format documentation"
        ]
    
    # Add size-based suggestions
    if file_size > 100 * 1024 * 1024:  # > 100MB
        suggestions.append("WARNING: Large file - consider network and storage impact")
    
    # Add security suggestions for executable files (case-insensitive for cross-platform)
    executable_extensions = (
        '.exe', '.bat', '.sh', '.com', '.scr',  # Windows & shell scripts
        '.app', '.dmg', '.pkg',                 # macOS
        '.deb', '.rpm', '.run', '.bin', '.appimage'  # Linux
    )
    if filename_lower.endswith(executable_extensions):
        suggestions = [
            "WARNING: Executable file - scan for security before running",
            "Consider sandboxed execution environment"
        ]
        category = 'executable'
    
    return {
        'category': category,
        'suggestions': suggestions,
        'file_size': file_size
    } 
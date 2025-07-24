"""
JSON utilities for Alfresco MCP Server.
Handles proper Unicode emoji encoding for MCP protocol transport.
"""
import json
import logging


logger = logging.getLogger(__name__)


def make_json_safe(text: str) -> str:
    """
    Make text JSON-safe for MCP protocol transport.
    Properly encodes Unicode emojis to prevent character map errors.
    
    Args:
        text: Input text that may contain Unicode emojis
        
    Returns:
        JSON-safe text with properly encoded Unicode characters
    """
    if not text:
        return text
        
    try:
        # Ensure proper Unicode normalization
        import unicodedata
        normalized = unicodedata.normalize('NFC', text)
        
        # Test if it can be safely JSON serialized
        json.dumps(normalized)
        return normalized
        
    except (UnicodeError, TypeError) as e:
        logger.warning(f"Unicode encoding issue, falling back to ASCII: {e}")
        # Fall back to ASCII-safe version with emoji descriptions
        return text.encode('ascii', errors='ignore').decode('ascii')


def safe_format_output(text: str) -> str:
    """
    Format output text to be safe for MCP JSON transport.
    Replaces emojis with text equivalents to prevent character map errors.
    
    Args:
        text: Text to format
        
    Returns:
        Safely formatted text with emojis replaced
    """
    if not text:
        return text
        
    try:
        # Define emoji replacements for common ones used in the tools
        emoji_replacements = {
            '🔗': '[LINK]',
            '🔓': '[UNLOCKED]', 
            '📄': '[DOCUMENT]',
            '🆔': '[ID]',
            '📏': '[SIZE]',
            '💾': '[SAVED]',
            '🔒': '[LOCKED]',
            '🕒': '[TIME]',
            '📥': '[DOWNLOAD]',
            'ℹ️': '[INFO]',
            '⚠️': '[WARNING]',
            '👤': '[USER]',
            '✅': '[SUCCESS]',
            '❌': '[ERROR]',
            '🏷️': '[TAG]',
            '🧩': '[MODULE]',
            '📁': '[FOLDER]',
            '📍': '[LOCATION]',
            '📅': '[DATE]',
            '📝': '[NOTE]',
            '🔢': '[VERSION]',
            '📊': '[SIZE]',
            '🗑️': '[DELETE]',
            '🔍': '[SEARCH]',
            '📤': '[UPLOAD]',
            '🧹': '[CLEANUP]',
            '🏢': '[REPOSITORY]',
            '🔧': '[TOOL]',
            '📦': '[PACKAGE]'
        }
        
        # Replace emojis with text equivalents
        safe_text = text
        for emoji, replacement in emoji_replacements.items():
            safe_text = safe_text.replace(emoji, replacement)
        
        # Test if the result is JSON-safe
        test_json = json.dumps(safe_text, ensure_ascii=True)
        json.loads(test_json)
        
        return safe_text
        
    except Exception as e:
        logger.warning(f"JSON formatting issue: {e}")
        try:
            # Ultimate fallback: remove all non-ASCII characters
            ascii_text = text.encode('ascii', errors='ignore').decode('ascii')
            return ascii_text
        except Exception as fallback_error:
            logger.error(f"ASCII fallback failed: {fallback_error}")
            return "Error: Text encoding failed"


def escape_unicode_for_json(text: str) -> str:
    """
    Alternative approach: explicitly escape Unicode characters for JSON.
    Use this if the regular approach doesn't work.
    
    Args:
        text: Input text with Unicode characters
        
    Returns:
        Text with Unicode characters escaped for JSON
    """
    if not text:
        return text
        
    try:
        # Use json.dumps to properly escape Unicode, then remove the quotes
        escaped = json.dumps(text, ensure_ascii=False)
        # Remove the surrounding quotes added by json.dumps
        if escaped.startswith('"') and escaped.endswith('"'):
            escaped = escaped[1:-1]
        return escaped
        
    except Exception as e:
        logger.warning(f"Unicode escaping failed: {e}")
        return text 
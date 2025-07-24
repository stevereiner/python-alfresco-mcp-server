# MCP Testing Guide - Base64 Examples and Utilities

## Base64 Example Strings

### Simple Examples
```
"SGVsbG8gV29ybGQ="           # "Hello World"
"VGVzdCBkb2N1bWVudA=="       # "Test document"
"U2FtcGxlIGNvbnRlbnQ="       # "Sample content"
```

### Document Content Examples
```python
# Text document
text_content = "This is a test document for MCP server testing."
text_base64 = "VGhpcyBpcyBhIHRlc3QgZG9jdW1lbnQgZm9yIE1DUCBzZXJ2ZXIgdGVzdGluZy4="

# JSON document  
json_content = '{"test": "data", "numbers": [1, 2, 3]}'
json_base64 = "eyJ0ZXN0IjogImRhdGEiLCAibnVtYmVycyI6IFsxLCAyLCAzXX0="
```

## Base64 Generation Functions

### Simple Generator Function
```python
import base64

def generate_base64(text_content):
    """Convert text to base64 string."""
    return base64.b64encode(text_content.encode('utf-8')).decode('utf-8')

def decode_base64(base64_string):
    """Decode base64 string to text."""
    return base64.b64decode(base64_string).decode('utf-8')

# Examples
text = "Hello World"
encoded = generate_base64(text)  # "SGVsbG8gV29ybGQ="
decoded = decode_base64(encoded)  # "Hello World"
```

### Document Generator for MCP Testing
```python
import base64
import json
import time
import uuid

def generate_test_document(filename, content_type="text"):
    """Generate a test document with base64 encoding for MCP upload."""
    
    if content_type == "text":
        content = f"""Test Document - {filename}
        
Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
Document ID: {uuid.uuid4()}
Type: MCP Test Document

This is a sample document created for testing the Alfresco MCP server.
It contains structured content for validation purposes.

Sections:
1. Header information
2. Timestamp data
3. Unique identifier
4. Content body
5. Footer notes

End of document.
"""
    elif content_type == "json":
        content = json.dumps({
            "document_id": str(uuid.uuid4()),
            "filename": filename,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "content_type": "test_data",
            "test_data": {
                "numbers": [1, 2, 3, 4, 5],
                "strings": ["hello", "world", "test"],
                "nested": {
                    "level1": {
                        "level2": "deep_value"
                    }
                }
            }
        }, indent=2)
    
    content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    return {
        "filename": filename,
        "content": content,
        "content_base64": content_base64,
        "size": len(content),
        "encoded_size": len(content_base64)
    }

# Usage examples
text_doc = generate_test_document("test_file.txt", "text")
json_doc = generate_test_document("test_data.json", "json")
```

### Batch Document Generator
```python
def generate_batch_documents(count=5, prefix="batch_doc"):
    """Generate multiple test documents for batch operations."""
    
    documents = []
    session_id = str(uuid.uuid4())[:8]
    
    for i in range(count):
        content = f"""Batch Document {i+1}
        
Session ID: {session_id}
Document Index: {i+1} of {count}
Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
Unique ID: {uuid.uuid4()}

This is batch document number {i+1} created for testing 
concurrent operations and bulk uploads in the MCP server.

Content sections:
- Document metadata
- Sequential numbering
- Timestamp information
- Unique identification

Processing notes:
- Part of batch operation
- Sequential creation
- Automated generation
"""
        
        doc = {
            "filename": f"{prefix}_{session_id}_{i+1:03d}.txt",
            "content": content,
            "content_base64": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "description": f"Batch document {i+1} from session {session_id}"
        }
        documents.append(doc)
    
    return documents

# Generate 5 test documents
batch_docs = generate_batch_documents(5)
```

## MCP Upload Examples

### Single Document Upload
```json
{
  "filename": "test_document.txt",
  "content_base64": "VGhpcyBpcyBhIHRlc3QgZG9jdW1lbnQgZm9yIE1DUCBzZXJ2ZXIgdGVzdGluZy4=",
  "parent_id": "-root-",
  "description": "Test upload via MCP Inspector"
}
```

### JSON Document Upload
```json
{
  "filename": "test_data.json", 
  "content_base64": "eyJ0ZXN0IjogImRhdGEiLCAibnVtYmVycyI6IFsxLCAyLCAzXX0=",
  "parent_id": "-root-",
  "description": "JSON test data"
}
```

## Validation Functions

### Base64 Validation
```python
import re

def validate_base64(base64_string):
    """Validate base64 string format."""
    try:
        # Check format
        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', base64_string):
            return False, "Invalid base64 characters"
        
        # Test decode
        decoded = base64.b64decode(base64_string, validate=True)
        return True, f"Valid base64 ({len(decoded)} bytes)"
        
    except Exception as e:
        return False, f"Decode error: {str(e)}"

# Test validation
valid, message = validate_base64("SGVsbG8gV29ybGQ=")
print(f"Validation: {valid}, Message: {message}")
```

### Content Size Calculation
```python
def calculate_base64_size(text_content):
    """Calculate the base64 encoded size before encoding."""
    original_bytes = len(text_content.encode('utf-8'))
    base64_bytes = ((original_bytes + 2) // 3) * 4
    return {
        "original_size": original_bytes,
        "base64_size": base64_bytes,
        "size_increase": f"{((base64_bytes / original_bytes - 1) * 100):.1f}%"
    }

# Example
size_info = calculate_base64_size("Hello World")
print(size_info)
# {'original_size': 11, 'base64_size': 16, 'size_increase': '45.5%'}
```

## Quick Reference

### Common Test Strings
```python
TEST_STRINGS = {
    "hello": "SGVsbG8gV29ybGQ=",
    "test": "dGVzdA==", 
    "sample": "c2FtcGxl",
    "document": "ZG9jdW1lbnQ=",
    "content": "Y29udGVudA==",
    "data": "ZGF0YQ==",
    "file": "ZmlsZQ==",
    "upload": "dXBsb2Fk"
}
```

### Usage in MCP Inspector
1. **Generate content**: Use the generator functions above
2. **Copy base64**: Use the `content_base64` field from generated documents  
3. **Test upload**: Paste into MCP Inspector's upload_document tool
4. **Validate**: Check successful upload in Alfresco

### File Size Limits
- **Small files**: < 1MB (recommended for testing)
- **Medium files**: 1-10MB (stress testing)  
- **Large files**: > 10MB (may require chunking)

Remember: Base64 encoding increases file size by approximately 33%, so plan accordingly for upload limits. 
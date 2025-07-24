# Alfresco MCP Server Examples

This directory contains practical examples demonstrating how to use the Alfresco MCP Server's **15 tools** across search, core operations, and workflow management in different scenarios.

## 📋 Available Examples

### 🚀 Quick Start Examples
- [`quick_start.py`](quick_start.py) - Basic server setup and first tool call

### 🔧 Transport Examples  
- [`transport_examples.py`](transport_examples.py) - All transport protocols (STDIO, HTTP, SSE)

### 🛠️ Tool Usage Examples
- [`document_lifecycle.py`](document_lifecycle.py) - Complete document management workflow
- [`batch_operations.py`](batch_operations.py) - Bulk document processing

### 📊 Additional Examples
- [`error_handling.py`](error_handling.py) - Error handling patterns

### 📖 Documentation Summary
- [`examples_summary.md`](examples_summary.md) - Overview of all examples and documentation

## 🎯 Getting Started

1. **Install Dependencies**: Ensure you have the server installed
2. **Set Up Alfresco**: Configure your Alfresco connection
3. **Run Examples**: Each example is self-contained and well-documented

## 🔧 Prerequisites

```bash
# Install the package
pip install -e .

# Set environment variables
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"  
export ALFRESCO_PASSWORD="admin"
```

## 📖 Example Structure

Each example includes:
- ✅ **Clear documentation** of what it demonstrates
- ✅ **Step-by-step comments** explaining each operation
- ✅ **Error handling** best practices
- ✅ **Expected output** descriptions
- ✅ **Practical use cases** and scenarios

## 🚀 Running Examples

```bash
# Quick start example
python examples/quick_start.py

# Document lifecycle workflow
python examples/document_lifecycle.py

# Transport protocols demonstration
python examples/transport_examples.py

# Batch operations and performance
python examples/batch_operations.py

# Error handling patterns
python examples/error_handling.py
```

## 💡 Tips

- Start with `quick_start.py` for your first experience
- Check `error_handling.py` for production-ready patterns
- Use `batch_operations.py` for performance optimization insights
- Explore `transport_examples.py` for different connection methods
- Review `examples_summary.md` for documentation overview 
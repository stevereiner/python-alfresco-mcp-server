# Alfresco MCP Server Examples

This directory contains practical examples demonstrating how to use the Alfresco MCP Server in different scenarios.

## 📋 Available Examples

### 🚀 Quick Start Examples
- [`quick_start.py`](quick_start.py) - Basic server setup and first tool call
- [`basic_client.py`](basic_client.py) - Simple client connection examples

### 🔧 Transport Examples  
- [`stdio_example.py`](stdio_example.py) - Standard MCP protocol usage
- [`http_example.py`](http_example.py) - HTTP transport usage
- [`sse_example.py`](sse_example.py) - Server-Sent Events transport

### 🛠️ Tool Usage Examples
- [`search_examples.py`](search_examples.py) - Document search scenarios
- [`document_lifecycle.py`](document_lifecycle.py) - Complete document management workflow
- [`folder_management.py`](folder_management.py) - Folder operations
- [`batch_operations.py`](batch_operations.py) - Bulk document processing

### 📊 Advanced Examples
- [`error_handling.py`](error_handling.py) - Robust error handling patterns
- [`performance_examples.py`](performance_examples.py) - Performance optimization techniques
- [`integration_examples.py`](integration_examples.py) - Integration with other systems

### 🔍 Resource and Prompt Examples
- [`resource_usage.py`](resource_usage.py) - Using MCP resources for repository info
- [`prompt_examples.py`](prompt_examples.py) - Working with analysis prompts

### ⚙️ Configuration Examples
- [`config_examples.py`](config_examples.py) - Different configuration setups
- [`environment_setup.py`](environment_setup.py) - Environment variable configurations

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
# Basic client example
python examples/basic_client.py

# Document lifecycle workflow
python examples/document_lifecycle.py

# Performance testing
python examples/performance_examples.py
```

## 💡 Tips

- Start with `quick_start.py` for your first experience
- Check `error_handling.py` for production-ready patterns
- Use `performance_examples.py` for optimization insights
- Refer to `integration_examples.py` for system integration 
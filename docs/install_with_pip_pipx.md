# Installation with pip and pipx

This guide covers traditional Python package installation methods (pip and pipx) for Python Alfresco MCP Server. For modern UV/UVX installation (recommended), see the [main README](../README.md).

## 🛠️ Installation Options

### Option 1: pipx (Recommended for Traditional Methods)

pipx automatically creates isolated environments for each tool while making commands globally available - eliminates dependency conflicts while providing system-wide access.

```bash
# First install pipx if you don't have it (one-time setup)
pip install pipx

# Install python-alfresco-mcp-server in isolated environment
pipx install python-alfresco-mcp-server

# Test that installation worked
python-alfresco-mcp-server --help
```

**Why pipx?** pipx automatically creates isolated environments for each tool while making commands globally available - eliminates dependency conflicts while providing system-wide access.

### Option 2: pip (Traditional Package Manager)

```bash
# Recommended: Create virtual environment first
python -m venv venv
source venv/bin/activate     # Linux/macOS
# venv\Scripts\activate      # Windows

# Install python-alfresco-mcp-server
pip install python-alfresco-mcp-server

# Test that installation worked
python-alfresco-mcp-server --help
```

## 🚀 Usage

### MCP Server Startup

**With pipx (Global installation - no venv needed):**

```bash
# Run MCP server with STDIO transport (default)
python-alfresco-mcp-server

# HTTP transport for web services (matches MCP Inspector)
python-alfresco-mcp-server --transport http --host 127.0.0.1 --port 8003

# SSE transport for real-time streaming  
python-alfresco-mcp-server --transport sse --host 127.0.0.1 --port 8001
```

**With pip (Activate venv first if installed in one):**

```bash
# Activate virtual environment first (if used during installation)
source venv/bin/activate     # Linux/macOS
# venv\Scripts\activate      # Windows

# Run MCP server with STDIO transport (default)
python-alfresco-mcp-server

# HTTP transport for web services (matches MCP Inspector)
python-alfresco-mcp-server --transport http --host 127.0.0.1 --port 8003

# SSE transport for real-time streaming  
python-alfresco-mcp-server --transport sse --host 127.0.0.1 --port 8001
```

## 🔧 Claude Desktop Configuration

The Claude Desktop configuration differs based on how you installed the MCP server:

### pipx Installation (Global Tool)

```json
{
  "command": "python-alfresco-mcp-server",
  "args": ["--transport", "stdio"]
}
```

- Uses the **global command name** directly (no path needed)
- pipx makes tools globally available in your PATH
- Simplest configuration

**Sample Config Files:**
- Windows: [`claude-desktop-config-pipx-windows.json`](../claude-desktop-config-pipx-windows.json)
- macOS: [`claude-desktop-config-pipx-macos.json`](../claude-desktop-config-pipx-macos.json)

### pip Installation (Manual venv)

```json
{
  "command": "C:\\path\\to\\venv\\Scripts\\python-alfresco-mcp-server.exe",
  "args": ["--transport", "stdio"]
}
```

- Uses **direct path to executable** in your virtual environment
- Path points to `Scripts/` directory in your venv (Windows) or `bin/` (Linux/macOS)
- Replace `C:\\path\\to\\venv` with your actual venv location

## 🔍 MCP Inspector Configuration

For development and testing with MCP Inspector:

### pipx Installation

Use the sample config files:
- **stdio transport**: [`mcp-inspector-stdio-pipx-config.json`](../mcp-inspector-stdio-pipx-config.json)
- **http transport**: [`mcp-inspector-http-pipx-config.json`](../mcp-inspector-http-pipx-config.json)

```bash
# Start with stdio transport
npx @modelcontextprotocol/inspector --config mcp-inspector-stdio-pipx-config.json --server python-alfresco-mcp-server

# Start with http transport  
npx @modelcontextprotocol/inspector --config mcp-inspector-http-pipx-config.json --server python-alfresco-mcp-server
```

### pip Installation

Copy one of the pipx sample files above and modify the `"command"` field to point to your venv executable:
- Change `"python-alfresco-mcp-server"` to `"C:\\path\\to\\venv\\Scripts\\python-alfresco-mcp-server.exe"` (Windows)
- Or `"/path/to/venv/bin/python-alfresco-mcp-server"` (Linux/macOS) 
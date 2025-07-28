# Python Alfresco MCP Server v1.1 🚀

[![PyPI version](https://img.shields.io/pypi/v/python-alfresco-mcp-server)](https://pypi.org/project/python-alfresco-mcp-server/)
[![PyPI downloads](https://pepy.tech/badge/python-alfresco-mcp-server/month)](https://pepy.tech/project/python-alfresco-mcp-server)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/python-alfresco-mcp-server/)
[![License](https://img.shields.io/github/license/stevereiner/python-alfresco-mcp-server)](https://github.com/stevereiner/python-alfresco-mcp-server/blob/main/LICENSE)

**Model Context Protocol Server for Alfresco Content Services**

A full featured MCP server for Alfresco in search and content management areas. It provides the following tools: full text search (content and properties), advanced search, metadata search, CMIS SQL like search, upload, download,
checkin, checkout, cancel checkout, create folder, folder browse, delete node, and get/set properties. Also has a  tool for getting repository status/config (also a resource). Has one prompt example.
Built with [FastMCP 2.0](https://github.com/jlowin/FastMCP). 
Features complete documentation, examples, and 
config for various MCP clients (Claude Desktop, MCP Inspector, references to configuring others).

## 🌟 What's New in v1.1

### **Modular Architecture & Enhanced Testing**
- **FastMCP**: v1.0 had FastMCP 2.0 implementation that had all tools implementations in the fastmcp_server.py file
- **Code Modularization in v1.1**: Split monolithic single file into organized modular structure with separate files
- **Directory Organization**: Organized into `tools/search/`, `tools/core/`, `resources/`, `prompts/`, `utils/` directories
- **Enhanced Testing**: Complete test suite transformation - 143 tests with 100% pass rate
- **Client Configuration Files**: Added dedicated Claude Desktop and MCP Inspector configuration files
- **Live Integration Testing**: 21 Alfresco server validation tests for real-world functionality
- **Python-Alfresco-API**:  python-alfresco-mcp-server v1.1  requires the v1.1.1 python-alfresco-api package

## 📚 Complete Documentation

### **Documentation & Examples**
- **📚 Complete Documentation**: 9 guides covering setup to deployment
- **💡 Examples**: 6 practical examples from quick start to implementation patterns  
- **🔧 Configuration Management**: Environment variables, .env files, and command-line configuration
- **🏗️ Setup instruction for use with MCP client

### **Learning Resources**
- **🚀 [Quick Start Guide](./docs/quick_start_guide.md)**: 5-minute setup and first operations
- **🤖 [Claude Desktop Setup](./docs/claude_desktop_setup.md)**: Complete Claude Desktop configuration for users and developers
- **🔧 [Client Configurations](./docs/client_configurations.md)**: Setup guide for Cursor, Claude Code, and other MCP clients
- **📖 [Examples Library](./examples/README.md)**: Implementation patterns and examples

### 📖 Guides covering setup, deployment, and usage:

- **[📚 Documentation Hub](./docs/README.md)** - Complete navigation and overview
- **[🚀 Quick Start Guide](./docs/quick_start_guide.md)** - 5-minute setup and first operations
- **[🤖 Claude Desktop Setup](./docs/claude_desktop_setup.md)** - Complete Claude Desktop configuration for users and developers
- **[🔧 Client Configurations](./docs/client_configurations.md)** - Setup guide for Cursor, Claude Code, and other MCP clients
- **[🔍 MCP Inspector Setup](./docs/mcp_inspector_setup.md)** - Development and testing with MCP Inspector
- **[🔍 API Reference](./docs/api_reference.md)** - Complete tool and resource documentation
- **[⚙️ Configuration Guide](./docs/configuration_guide.md)** - Development to deployment
- **[🧪 Testing Guide](./docs/testing_guide.md)** - Quality assurance and test development
- **[🛠️ Troubleshooting Guide](./docs/troubleshooting.md)** - Problem diagnosis and resolution

## 🚀 Features

### Content Management and Search Tools
- **Search Tools**: 
  - **Full Text Search**: Basic content search with wildcard support (search_content)
  - **Advanced Search**: AFTS query language with date filters, sorting, and field targeting
  - **Metadata Search**: Property-based queries with operators (equals, contains, date ranges)
  - **CMIS Search**: SQL like queries for complex content discovery
- **Document Lifecycle**: Upload, download, check-in, checkout, cancel checkout
- **Version Management**: Create major/minor versions with comments
- **Folder Operations**: Create folders, delete folder nodes
- **Property Management**: Get and set document/folder properties and names
- **Node Operations**: Delete nodes (documents and folders) (trash or permanent)
- **Repository Info**: (Tool and Resource) Returns repository status, version and whether Community or Enterprise, and module configuration

### MCP Architecture
- **FastMCP 2.0 Framework**: Modern, high-performance MCP server implementation
- **Multiple Transports**: 
  - **STDIO** (direct MCP protocol) - Default and fastest
  - **HTTP** (RESTful API) - Web services and testing
  - **SSE** (Server-Sent Events) - Real-time streaming updates
- **Enterprise Security**: OAuth 2.1  (optional)
- **Type Safety**: Full Pydantic v2 models
- **In-Memory Testing**: Client testing with faster execution
- **Configuration**: Environment variables, .env files

### Alfresco Integration 
Works with Alfresco Community (tested) and Enterprise editions


## 📋 Requirements

- Python 3.10+
- Alfresco Content Services (Community or Enterprise)
- python-alfresco-api >= 1.1.1

## 🛠️ Installation

### Install Python

You need to have Python 3.10+ installed for the sections below. If not, download the latest 3.13.x version from:

[Python.org Downloads](https://www.python.org/downloads/)


### Option A: Install from PyPI (Recommended for Users)

The fastest way to get started - install directly from PyPI:

```bash
# First install pipx if you don't have it (one-time setup)
pip install pipx

# Option 1: pipx (Recommended) - installs in isolated environment + makes globally available
pipx install python-alfresco-mcp-server

# Option 2: pip - traditional package manager (with venv recommended)
python -m venv venv
source venv/bin/activate     # Linux/macOS
# venv\Scripts\activate      # Windows
pip install python-alfresco-mcp-server

# Option 3: UV (fastest) - Rust-based package manager (see next section for installing uv)
uv pip install python-alfresco-mcp-server

# Run immediately to test if can get help
python-alfresco-mcp-server --help
```

**Why pipx?** pipx automatically creates isolated environments for each tool while making commands globally available - eliminates dependency conflicts while providing system-wide access.

**Note**: You still need to configure your MCP client (Claude Desktop, MCP Inspector, etc.) with the appropriate configuration. See the [MCP Client Setup and Use](#mcp-client-setup-and-use) section below for client configuration details.

### Option B: Install from Source (Recommended for Development)

For development or access to latest features:

### 1. Install UV (Recommended)

UV is a modern Python package manager written in **Rust** that handles everything automatically. **Much faster than pip** due to its compiled nature and optimized dependency resolution. Choose your installation method:

```bash
# Method 1: Official installer (recommended)
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux  
curl -LsSf https://astral.sh/uv/install.sh | sh

# Method 2: pip (if you prefer)
pip install uv

# Verify installation
uv --version
```

**UV Reference Links:**
- **[UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)** - Official installation instructions and platform-specific options
- **[UV Documentation](https://docs.astral.sh/uv/)** - Complete UV documentation, guides, and advanced usage

### 2. Get the Code

```bash
# Clone the repository
git clone https://github.com/stevereiner/python-alfresco-mcp-server.git
cd python-alfresco-mcp-server
```

### 3. Install Dependencies (Choose Method)

**Option A: UV (Recommended - Automatic everything + much faster):**

```bash
# UV handles venv creation and dependency installation automatically
# Rust-based performance makes this much faster than pip
uv run python-alfresco-mcp-server --help

# Or install dependencies explicitly:
uv sync                    # Basic dependencies
uv sync --extra dev        # With development tools  
uv sync --extra test       # With testing tools
uv sync --extra all        # Everything
```

**Option B: Traditional pip (Manual venv management):**

```bash
# Create and activate virtual environment  
python -m venv venv          # Traditional Python creates 'venv'
source venv/bin/activate     # Linux/macOS
# venv\Scripts\activate      # Windows

# Note: UV creates '.venv' by default (not 'venv')

# Install MCP server
pip install -e .

# Or with development dependencies
pip install -e .[dev]

# Or with testing dependencies
pip install -e .[test]

# Or install everything
pip install -e .[all]
```

### 4. Configure Alfresco Connection

**Option 1: Environment Variables**
```bash
# Linux/Mac
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
export ALFRESCO_VERIFY_SSL="false"

# Windows PowerShell
$env:ALFRESCO_URL="http://localhost:8080"
$env:ALFRESCO_USERNAME="admin"
$env:ALFRESCO_PASSWORD="admin"
$env:ALFRESCO_VERIFY_SSL="false"

# Windows Command Prompt
set ALFRESCO_URL=http://localhost:8080
set ALFRESCO_USERNAME=admin
set ALFRESCO_PASSWORD=admin
set ALFRESCO_VERIFY_SSL=false
```

**Option 2: .env file** (recommended - cross-platform):
```bash
# Copy sample-dot-env.txt to .env and customize
# Linux/macOS
cp sample-dot-env.txt .env

# Windows
copy sample-dot-env.txt .env

# Edit .env file with your settings
ALFRESCO_URL=http://localhost:8080
ALFRESCO_USERNAME=admin
ALFRESCO_PASSWORD=admin
ALFRESCO_VERIFY_SSL=false
```
> **Note**: The `.env` file is not checked into git for security. Use `sample-dot-env.txt` as a template.

📖 **See [Configuration Guide](./docs/configuration_guide.md) for complete setup options**

## Alfresco Installation 

If you don't have an Alfresco server installed you can get a docker for the 
Community version from Github

```bash
git clone https://github.com/Alfresco/acs-deployment.git
```

**Move to Docker Compose directory**

```bash
cd acs-deployment/docker-compose
```

**Edit community-compose.yaml**
- Note: you will likely need to comment out activemq ports other than 8161

```bash   
   ports:
   - "8161:8161" # Web Console
   #- "5672:5672" # AMQP
   #- "61616:61616" # OpenWire
   #- "61613:61613" # STOMP
```      

**Start Alfresco with Docker Compose**

```bash
docker-compose -f community-compose.yaml up
```

## 🚀 Usage

### MCP Server Startup

**With UV (Recommended - Automatic venv and dependency management):**

```bash
# Run MCP server with STDIO transport (default)
uv run python-alfresco-mcp-server

# HTTP transport for web services (matches MCP Inspector)
uv run python-alfresco-mcp-server --transport http --host 127.0.0.1 --port 8003

# SSE transport for real-time streaming  
uv run python-alfresco-mcp-server --transport sse --host 127.0.0.1 --port 8001
```

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

### MCP Client Setup and Use

Python-Alfresco-MCP-Server was tested with Claude Desktop which is recommended as an end user MCP client. Python-Alfresco-MCP-Server was also tested with MCP Inspector which is recommended for developers to test tools with argument values.

#### 🤖 **Claude Desktop** for Windows (tested) and MacOS (not tested)

📖 **Complete Setup Guide**: **[Claude Desktop Setup Guide](./docs/claude_desktop_setup.md)**

**📥 Download Claude Desktop (Free and Pro versions):**
- **[Download Claude Desktop](https://claude.ai/download)** - Official Anthropic download page
- Available for **Windows** and **macOS** only (no Linux version)
- **Free tier** includes full MCP support and Claude Sonnet 4 access with limits, older Claude models
(Claude Opus 4 only in Pro)


**For Users (PyPI pipx installation):**
- Install with `pipx install python-alfresco-mcp-server`
- Use configuration files: `claude-desktop-config-user-windows.json` or `claude-desktop-config-user-macos.json`

**For Developers (using uv and source installation):**
- Clone repository and use uv
- Use configuration files: `claude-desktop-config-developer-windows.json` or `claude-desktop-config-developer-macos.json`

**🔧 Claude Desktop Path Configuration by Installation Method:**

The Claude Desktop configuration differs based on how you installed the MCP server:

**1. UV (both PyPI and source installations):**

*Option A: UV with project directory (source install or after `uv pip install`):*
```json
{
  "command": "uv",
  "args": ["run", "python-alfresco-mcp-server", "--transport", "stdio"],
  "cwd": "C:\\path\\to\\python-alfresco-mcp-server"
}
```
- Uses `uv run` with `cwd` pointing to your **project directory**
- UV automatically finds and uses the `.venv` from the project directory
- Works for both source installations and after `uv pip install` in a project

*Option B: UV global installation:*
```json
{
  "command": "C:\\Users\\{username}\\.local\\bin\\python-alfresco-mcp-server",
  "args": ["--transport", "stdio"]
}
```
- Direct path to UV's global installation directory
- Use when UV installed package globally (similar to pipx)

**2. pipx (global tool installation):**
```json
{
  "command": "python-alfresco-mcp-server",
  "args": ["--transport", "stdio"]
}
```
- Uses the **global command name** directly (no path needed)
- pipx makes tools globally available in your PATH
- Simplest configuration

**3. pip (manual venv installation):**
```json
{
  "command": "C:\\path\\to\\venv\\Scripts\\python-alfresco-mcp-server.exe",
  "args": ["--transport", "stdio"]
}
```
- Uses **direct path to executable** in your virtual environment
- Path points to `Scripts/` directory in your venv
- Replace `C:\\path\\to\\venv` with your actual venv location

**🔐 Tool-by-Tool Permission System:**
Claude Desktop will prompt you **individually for each tool** on first use. Since this MCP server has 15 tools, you may see up to 15 permission prompts if you use all features. For each tool, you can choose:
- **"Allow once"** - Approve this single tool use only
- **"Always allow"** - Approve all future uses of this specific tool automatically (recommended for regular use)

This tool-by-tool security feature ensures you maintain granular control over which external tools can be executed.

**Using the Tools:**

- **Chat naturally** about what you want to do with documents and search
- **Mention "Alfresco"** to ensure the MCP server is used (e.g., "In Alfresco...")
- **Use tool-related keywords** - mention something close to the tool name 
- **Follow-up prompts** will know the document from previous context

**Example 1: Document Management**

1. Upload a simple text document: "Please create a file called 'claude_test_doc-25 07 25 101 0 AM.txt' in the repository shared folder with this content: 'This is a test document created by Claude via MCP.' description 'Test document uploaded via Claude MCP'"
2. Update properties: "Set the description property of this document to 'my desc'"
3. Check out the document
4. Cancel checkout
5. Check out again  
6. Check in as a major version
7. Download the document
8. Upload a second document from "C:\1 sample files\cmispress.pdf"

> **Note**: Claude will figure out to use base64 encoding for the first upload on a second try

**Example 2: Search Operations**

"With Alfresco please test all 3 search methods and CMIS query:"
- Basic search for "txt" documents, return max 10
- Advanced search for documents created after 2024-01-01, return max 25
- Metadata search for documents where cm:title contains "test", limit to 50  
- CMIS search to find all txt documents, limit to 50

**More Examples: Create Folder, Browse Folders, Get Repository Info**

- "Create a folder called '25 07 25 01 18 am' in shared folder"
- "List docs and folders in shared folder" *(will use -shared-)*
- "Can you show me what's in my Alfresco home directory?" *(will use browse_repository -my-)*
- "Get info on Alfresco" *(will use repository_info tool)*

**Chat Box Buttons**

- Use **Search and tools button** (two horizontal lines with circles icon) in the chat box and choose "python-alfresco-mcp-server" - this allows you to enable/disable all tools or individual tools

- Click the **+ Button** → "Add from alfresco" for quick access to resources and prompts

**Search and Analyze Prompt:**
- Provides a form with query field for full-text search
- Analysis types: **summary**, **detailed**, **trends**, or **compliance**
- **Generates template text** to copy/paste into chat for editing

**Repository Info Resource (and Tool):**
- Provides status information in text format for viewing or copying

**Examples:**
- See [`prompts-for-claude.md`](./prompts-for-claude.md) for examples testing the tools


#### 🔍 **MCP Inspector** (Development/Testing)

> 📖 **Setup Guide**: Complete MCP Inspector setup and connection instructions in [MCP Inspector Setup Guide](./docs/mcp_inspector_setup.md)

**📥 Install MCP Inspector:**
- **Prerequisites**: Requires **Node.js 18+** - Download from **[nodejs.org](https://nodejs.org/)**
- **Install Command**: `npm install -g @modelcontextprotocol/inspector`
- **Or run directly**: `npx @modelcontextprotocol/inspector` (no global install needed)
- **Purpose**: Web-based tool for testing MCP servers and individual tools with custom parameters

**Working Method (Recommended):**

**1. Start MCP Server with HTTP transport:**

   ```bash
   # With UV (recommended)
   uv run python-alfresco-mcp-server --transport http --port 8003

   # With pipx (global)
   python-alfresco-mcp-server --transport http --port 8003

   # With pip (activate venv first if needed)
   python-alfresco-mcp-server --transport http --port 8003
   ```

**2. Start MCP Inspector with config:**

   **If using UV/source installation (config file available):**
   ```bash
   # From project directory where mcp-inspector-http-config.json exists
   npx @modelcontextprotocol/inspector --config mcp-inspector-http-config.json --server python-alfresco-mcp-server
   ```

   **If using pipx installation:**

   Copy one of the sample config files for your preferred transport:
   - **stdio transport**: [`mcp-inspector-stdio-pipx-config.json`](./mcp-inspector-stdio-pipx-config.json)
   - **http transport**: [`mcp-inspector-http-pipx-config.json`](./mcp-inspector-http-pipx-config.json)

   ```bash
   # Start with stdio transport
   npx @modelcontextprotocol/inspector --config mcp-inspector-stdio-pipx-config.json --server python-alfresco-mcp-server

   # Start with http transport  
   npx @modelcontextprotocol/inspector --config mcp-inspector-http-pipx-config.json --server python-alfresco-mcp-server
   ```

   **If using pip installation:**

   Copy one of the pipx sample files above and modify the `"command"` field to point to your venv executable:
   - Change `"python-alfresco-mcp-server"` to `"C:\\path\\to\\venv\\Scripts\\python-alfresco-mcp-server.exe"` (Windows)
   - Or `"/path/to/venv/bin/python-alfresco-mcp-server"` (Linux/macOS)

**3. Open browser with pre-filled token:**

   - Use the URL provided in the output (includes authentication token)
   - Example: `http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<token>`
   - This step applies to **all installation methods** (UV, pipx, pip)

This approach avoids proxy connection errors and provides direct authentication.


#### 🔧 **Other MCP Clients**

For Cursor, Claude Code, and other MCP clients:

📖 **Complete Setup Guide**: **[Client Configuration Guide](./docs/client_configurations.md)**


## 🛠️ Available Tools (15 Total)

### 🔍 Search Tools (4)
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_content` | Search documents and folders | `query` (str), `max_results` (int), `node_type` (str) |
| `advanced_search` | Advanced search with filters | `query` (str), `content_type` (str), `created_after` (str), etc. |
| `search_by_metadata` | Search by metadata properties | `property_name` (str), `property_value` (str), `comparison` (str) |
| `cmis_search` | CMIS SQL queries | `cmis_query` (str), `preset` (str), `max_results` (int) |

### 🛠️ Core Tools (11)
| Tool | Description | Parameters |
|------|-------------|------------|
| `browse_repository` | Browse repository folders | `node_id` (str) |
| `repository_info` | Get repository information | None |
| `upload_document` | Upload new document | `filename` (str), `content_base64` (str), `parent_id` (str), `description` (str) |
| `download_document` | Download document content | `node_id` (str), `save_to_disk` (bool) |
| `create_folder` | Create new folder | `folder_name` (str), `parent_id` (str), `description` (str) |
| `get_node_properties` | Get node metadata | `node_id` (str) |
| `update_node_properties` | Update node metadata | `node_id` (str), `name` (str), `title` (str), `description` (str), `author` (str) |
| `delete_node` | Delete document/folder | `node_id` (str), `permanent` (bool) |
| `checkout_document` | Check out for editing | `node_id` (str), `download_for_editing` (bool) |
| `checkin_document` | Check in after editing | `node_id` (str), `comment` (str), `major_version` (bool), `file_path` (str) |
| `cancel_checkout` | Cancel checkout/unlock | `node_id` (str) |

📖 **See [API Reference](./docs/api_reference.md) for detailed tool documentation**

## 📊 Available Resources

### Repository Information
| Resource | Description | Access Method |
|----------|-------------|---------------|
| `repository_info` | Get comprehensive repository information including version, edition, license details, installed modules, and system status | Available as both MCP resource and tool |

The `repository_info` resource provides:
- **Repository Details**: ID, edition (Community/Enterprise), version information
- **License Information**: Issued/expires dates, remaining days, license holder, entitlements
- **System Status**: Read-only mode, audit enabled, quick share, thumbnail generation
- **Installed Modules**: Up to 10 modules with ID, title, version, and installation state

📖 **See [API Reference](./docs/api_reference.md) for detailed resource documentation**

## 🎯 Available Prompts

### Search and Analyze Prompt
| Prompt | Description | Parameters |
|--------|-------------|------------|
| `search_and_analyze` | Interactive form for guided content search and analysis | `query` (search terms), `analysis_type` (summary/detailed/trends/compliance) |

The Search and Analyze Prompt provides:
- **Interactive Form**: User-friendly interface with query input field
- **Analysis Options**: Choose from summary, detailed analysis, trends, or compliance reporting
- **Template Generation**: Creates copyable template text for chat conversations
- **Query Assistance**: Helps users structure effective search queries
- **Multiple Search Types**: Integrates with all 4 search tools (content, advanced, metadata, CMIS)

📖 **See [API Reference](./docs/api_reference.md) for detailed prompt documentation**

## 🔧 Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ALFRESCO_URL` | `http://localhost:8080` | Alfresco server URL |
| `ALFRESCO_USERNAME` | `admin` | Username for authentication |
| `ALFRESCO_PASSWORD` | `admin` | Password for authentication |
| `ALFRESCO_VERIFY_SSL` | `false` | Verify SSL certificates |
| `ALFRESCO_TIMEOUT` | `30` | Request timeout (seconds) |
| `FASTAPI_HOST` | `localhost` | FastAPI host |
| `FASTAPI_PORT` | `8000` | FastAPI port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `100000000` | Max upload size (bytes) |

⚙️ **See [Configuration Guide](./docs/configuration_guide.md) for deployment options**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MCP Clients                       │
│  Claude Desktop │ MCP Inspector │ Cursor │ Claude   │
│     Code │ n8n │ LangFlow │ Custom MCP Client App   │
└─────────────────┬───────────────────────────────────┘
                  │ stdio/HTTP/SSE
┌─────────────────▼───────────────────────────────────┐
│             FastMCP 2.0 MCP Server                  │
│  ┌─────────────┬─────────────┬─────────────────┐    │
│  │ MCP Tools   │ MCP         │ HTTP/SSE API    │    │
│  │ (15 total)  │ Resources   │                 │    │
│  │             │ MCP Prompts │                 │    │
│  └─────────────┴─────────────┴─────────────────┘    │
└─────────────────┬───────────────────────────────────┘
                  │ python-alfresco-api
┌─────────────────▼───────────────────────────────────┐
│            Alfresco Content Services                │
│         (Community/Enterprise Edition)              │
└─────────────────────────────────────────────────────┘
```

## 🧪 Testing & Quality

### Test Suite Overview
- **143 Total Tests**: **100% passed** - Coverage of all functionality
- **122 Unit Tests**: **100% passed** - Core functionality validated with mocking (FastMCP 2.0, tools, coverage)
- **21 Integration Tests**: **100% passed** - Live server testing (search, upload, download, document lifecycle)
- **Integration Tests**: Automated end-to-end testing covering all 14 manual scenarios from prompts-for-claude.md
- **Performance Validated**: Search <1s, concurrent operations, resource access

### Coverage Report (Post-Cleanup)
- **Overall Coverage**: 51% (1,829 statements tested)
- **FastMCP 2.0 Core**: Well tested with comprehensive unit coverage
- **Configuration Module**: 93% coverage - Fully tested
- **Package Initialization**: 100% coverage (5/5 lines) - Complete
- **Overall Project**: 51% coverage of comprehensive codebase

### Run Tests

```bash
# Run full test suite
pytest

# Run with coverage report
pytest --cov=alfresco_mcp_server --cov-report=term-missing

# Run specific test categories
pytest -m "unit"           # Unit tests only
pytest -m "fastmcp"        # FastMCP 2.0 tests
pytest -m "integration"    # Integration tests (requires Alfresco)
```

🧪 **See [Testing Guide](./docs/testing_guide.md) for detailed testing strategies**

### 🧪 Test Categories and Execution

The project includes **4 levels of testing**:

1. **📋 Unit Tests** (122 tests) - Fast, mocked, isolated component testing
2. **🔗 Integration Tests** (21 tests) - Live Alfresco server testing  
3. **📝 Comprehensive Tests** - Automated prompts-for-claude.md scenarios
4. **📊 Coverage Tests** - Edge cases and error path coverage

**New Integration Tests:**
- **Automated Manual Scenarios**: All manual test scenarios from `prompts-for-claude.md` now available as automated tests

## 🧪 Development

### Setup Development Environment

```bash
git clone <repository>
cd python-alfresco-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -e .[dev]

# Install python-alfresco-api (local development)
pip install -e ../python-alfresco-api
```

## 💡 Examples

### Real-world implementation patterns from beginner to enterprise:

- **[💡 Examples Library](./examples/README.md)** - Complete navigation and learning paths
- **[🏃 Quick Start](./examples/quick_start.py)** - 5-minute introduction and basic operations
- **[📋 Document Lifecycle](./examples/document_lifecycle.py)** - Complete process demonstration
- **[🚀 Transport Examples](./examples/transport_examples.py)** - STDIO, HTTP, and SSE protocols
- **[⚡ Batch Operations](./examples/batch_operations.py)** - High-performance bulk processing
- **[🛡️ Error Handling](./examples/error_handling.py)** - Resilience patterns
- **[📊 Examples Summary](./examples/examples_summary.md)** - Overview and statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects and References

- **[Hyland Alfresco](https://www.hyland.com/en/solutions/products/alfresco-platform)** - Content management platform (Enterprise and Community editions)
- **[python-alfresco-api](https://github.com/stevereiner/python-alfresco-api)** - The underlying Alfresco API library
- **[FastMCP 2.0](https://github.com/jlowin/FastMCP)** - Modern framework for building MCP servers
- **[FastMCP Documentation](https://gofastmcp.com/)** - Complete FastMCP framework documentation and guides
- **[Model Context Protocol](https://modelcontextprotocol.io)** - Official MCP specification and documentation
- **[Playbooks.com MCP List](https://playbooks.com/mcp/stevereiner-alfresco-content-services)** - Python Alfresco MCP Server listing
- **[PulseMCP.com MCP List](https://www.pulsemcp.com/servers/stevereiner-alfresco-content-services)** - Python Alfresco MCP Server listing
- **[Glama.ai MCP List](https://glama.ai/mcp/servers?query=alfresco)** - Glama Alfresco list including Python Alfresco MCP Server listing
- **[MCPMarket.com MCP List](https://mcpmarket.com/server/alfresco)** - Python Alfresco MCP Server listing

## 🙋‍♂️ Support

- 📚 **Documentation**: Complete guides in [`./docs/`](./docs/README.md)
- 💡 **Examples**: Implementation patterns in [`./examples/`](./examples/README.md)
- 🧪 **Testing**: Quality assurance in [`./docs/testing_guide.md`](./docs/testing_guide.md)
- 🔍 **MCP Inspector**: Development testing in [`./docs/mcp_inspector_setup.md`](./docs/mcp_inspector_setup.md)
- 🛠️ **Troubleshooting**: Problem solving in [`./docs/troubleshooting.md`](./docs/troubleshooting.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/stevereiner/python-alfresco-mcp-server/issues)

---

**🚀 MCP server built with [python-alfresco-api](https://github.com/stevereiner/python-alfresco-api) and [FastMCP 2.0](https://github.com/paulinephelan/FastMCP)**

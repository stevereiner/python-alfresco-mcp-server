# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-25

### Alfresco_MCP_Server dir code changes for v1.1
- **Code Split**: Refactored from monolithic single file to modular structure with separate files
- **Directory Structure**: Reorganized from flat to hierarchical structure
  - `tools/search/` - 4 search-related tools
  - `tools/core/` - 11 core management tools
  - `resources/` - Repository information
  - `prompts/` - AI templates
  - `utils/` - Shared utilities  
- fix: implement Windows UTF-8 encoding support (emoji character encoding)
- get to work with python-alfresco-api 1.1.x
- add imports and __all__ to get files included in packaging

### UV Package Management Support
- **Rust-based Performance**: UV provides faster dependency resolution and package management
- **Automatic Environment Management**: UV handles virtual environment creation and activation
- **Simplified Installation**: One-command setup replaces multi-step manual process
- **Cross-platform Compatibility**: Consistent behavior across Windows, macOS, and Linux

### PyPI Distribution
- **Direct Installation**: Available via `pip install python-alfresco-mcp-server`
- **UV Integration**: Compatible with `uv pip install python-alfresco-mcp-server`
- **Immediate Usage**: Run server directly after installation without source code

### Update Tests for v1.1
- `test: transform test suite from 76+ failures to 143/143 passing`
- `test: add comprehensive live integration testing with 21 Alfresco tests`
- `test: implement cross-platform emoji handling for Windows compatibility`
- `test: enhance coverage reporting with HTML output`
- `test: add automated testing for all manual scenarios`
- `test: implement strip_emojis() function for Windows compatibility`
- `test: add comprehensive unit test coverage (122 tests)`
- `test: fix test import paths for modular architecture`

### MCP Clients: config files added for v1.1
-  Added Claude Desktop and MCP Inspector config files
- `config: added claude-desktop-config-developer-windows.json with UV support`
- `config: added claude-desktop-config-developer-macos.json with UV support`
- `config: added claude-desktop-config-user-windows.json`
- `config: added claude-desktop-config-user-macos.json`
- `config: added Windows UTF-8 encoding variables to windows configs`
- `config: added mcp-inspector-http-config.json for HTTP transport using uv`
- `config: added mcp-inspector-stdio-config.json for STDIO transport using uv`
- 'examples: prompts-for-claude.md has example prompt text to test tools

### Update docs for v1.1
- `docs: create comprehensive CHANGELOG.md for v1.0.0 and v1.1.0`
- `docs: update quick start guide for UV approach`
- 'docs: api_reference.md added details for all tools, etc
- `docs: added claude_desktop_setup.md, mcp_inspector_setup.md, and client_configurations.md

### Documentation Updates for v1.1
- **Installation Instructions**: Added PyPI installation methods
- **Configuration Examples**: Updated for UV approach
- **Testing Procedures**: Comprehensive test execution guidance
- **Troubleshooting**: Enhanced problem resolution guidance

### Update Readme for v1.1
- added install from PyPI 
- added how to install UV package manager
- added claude desktop and mcp inspector setup sections
- reword technical sections for accuracy
- add v1.1 list of changes, depend on python-alfresco 1.1.1, python 3.10+
- added how to install Alfresco Community from github

### Update project files and misc root dir files for v1.1
- gitignore now ignores cursor memory and memory-bank dir, keep .vscode/mcp.json
- config.yaml has changed alfresco_url to have base_url, added timeout, added
  mcp server name and version confg
- MANIFEST.in added for proper package distrubution config
- pyproject.toml change to have v1.1.0 release, pypi distrib settings, remove
  fastMCP version restriction, update to require python 3.10 or greater, add
  pypi keyword and topic, settings, project urls for pypi, configure setuptools
  for includes, excludes
- run_server.py script added
- .vscode/mcp.json  uses run_server.py for debugging mcp server
-  uv.lock add now that use uv, and uv lock --upgrade updated v0.12.5 from v0.12.4 of ruff

### Fixes for pyproject.toml  for v1.1
 - require python-alfresco-api >= 1.1.1 not 1.0.0 in dependencies
 - have python 3.10 instead of 3.8 for tool.mypy, and py310 not py38 for tool.ruff and tool.black
 
### Example Code Updates for v1.1
- `examples: update transport examples for UV approach`
- `examples: enhance document lifecycle example`
- `examples: add UV-specific installation examples`
- `examples: update batch operations for improved performance`
- `examples: refactor error handling patterns` 

### Requirements
- **Python Versions**: 3.10+ (unchanged)
- **python-alfresco-api**: >= 1.1.1 (updated requirement)
- **FastMCP**: Tested with v2.10.6

### Tested
- **Alfresco Versions**: Community 25.1 (tested), Enterprise (not tested in v1.1)
- **Operating Systems**: 
  - Windows (tested)
  - macOS (needs testing)
  - Linux (needs testing, note: no Claude Desktop support on Linux)
- **MCP Clients**: 
  - Claude Desktop (tested and validated)
  - MCP Inspector (tested and validated)
  - Cursor (configuration provided, not tested in v1.1)
  - Claude Code (configuration provided, not tested in v1.1) 

## [1.0.0] - 2024-06-24

### Added
- Initial FastMCP 2.0 server implementation
- 15 content management tools across search and core operations
- Full text search with wildcard support
- Advanced search using AFTS query language
- Metadata search with property-based queries
- CMIS SQL search capabilities
- Complete document lifecycle management (upload, download, checkout, checkin)
- Version management with major/minor version support
- Folder operations and repository browsing
- Property management for documents and folders
- Multiple transport protocols (STDIO, HTTP, SSE)
- Configuration via environment variables and .env files
- Claude Desktop integration with Windows and macOS configs
- MCP Inspector support for development testing
- Comprehensive documentation and examples
- Testing framework with unit and integration tests
- Error handling and recovery patterns
- Repository discovery and status reporting

### Technical Implementation
- python-alfresco-api integration for content services access
- Pydantic v2 models for type safety
- Async support for concurrent operations
- Connection pooling and authentication management
- Progress reporting and context logging
- Configuration validation and environment setup 
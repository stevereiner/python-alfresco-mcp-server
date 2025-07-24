# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-25

### Added
- UV package manager support with Rust-based dependency resolution
- PyPI installation option for direct package installation
- Complete test suite transformation: 143 tests with 100% pass rate
- Live integration testing with 21 Alfresco server validation tests
- CMIS search query fixes for proper standard type mapping
- Comprehensive HTML coverage reports (51% overall coverage)
- Windows UTF-8 encoding support for Claude Desktop integration
- Enhanced error handling for server unavailability scenarios
- Modular architecture with organized tools/search and tools/core directories
- Client configuration files (claude-desktop-config-windows.json, claude-desktop-config-macos.json)
- MCP Inspector configuration files for HTTP and STDIO transport

### Changed
- Package management approach from manual venv to UV automation
- Test architecture from 76+ failures to 143/143 passing tests
- CMIS search queries to use standard names (cmis:document vs cm:content)
- CallToolResult access patterns throughout test suite
- Client access patterns to use raw_client property instead of _get_raw_client()
- Search result attribute access from .list to .list_ for proper API compatibility
- JSON output formatting to remove markdown syntax for better parsing
- Documentation reworded for technical accuracy
- Architecture from monolithic single file to modular structure with separate files for tools, resources, prompts, and utilities

### Fixed
- CMIS search 500 errors by using CMIS standard type names
- Character encoding issues with emojis on Windows systems
- Search functionality returning zero results in certain scenarios
- Authentication header construction for Bearer token conflicts
- Node property access patterns for structured objects
- Content upload API compatibility with proper headers
- Discovery API error handling for disabled services

### Removed
- Legacy MCP SDK implementation files
- FastMCP version restrictions
- Markdown formatting from tool outputs

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
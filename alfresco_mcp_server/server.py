"""
Main Alfresco MCP Server implementation.

Provides comprehensive content management tools through the Model Context Protocol.
"""

import asyncio
import base64
import logging
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from .config import AlfrescoConfig, load_config

# Import python-alfresco-api (assuming it's installed)
try:
    from python_alfresco_api import ClientFactory, AuthUtil
    from python_alfresco_api.models import alfresco_core_models as core_models
    from python_alfresco_api.models import alfresco_search_models as search_models
except ImportError as e:
    logging.error(f"Failed to import python-alfresco-api: {e}")
    raise

logger = logging.getLogger(__name__)


class AlfrescoMCPServer:
    """
    Alfresco Model Context Protocol Server.
    
    Provides AI-native access to Alfresco content management operations:
    - Search documents and folders
    - Upload/download files  
    - Document lifecycle (checkin/checkout)
    - Version management
    - Property management
    - Folder operations
    """
    
    def __init__(self, config: Optional[AlfrescoConfig] = None):
        """Initialize the Alfresco MCP Server."""
        self.config = config or load_config()
        self.server = Server(self.config.server_name)
        self.alfresco_factory: Optional[ClientFactory] = None
        self.auth_util: Optional[AuthUtil] = None
        
        # Setup logging
        logging.basicConfig(level=self.config.log_level)
        
        # Register MCP handlers
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    async def _initialize_alfresco(self) -> None:
        """Initialize Alfresco API clients."""
        try:
            self.alfresco_factory = ClientFactory(
                base_url=self.config.alfresco_url,
                username=self.config.username,
                password=self.config.password,
                verify_ssl=self.config.verify_ssl,
                timeout=self.config.timeout
            )
            
            self.auth_util = AuthUtil(
                base_url=self.config.alfresco_url,
                username=self.config.username,
                password=self.config.password,
                verify_ssl=self.config.verify_ssl
            )
            
            # Test connection
            await self.auth_util.ensure_authenticated()
            logger.info(f"Successfully connected to Alfresco at {self.config.alfresco_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alfresco connection: {e}")
            raise
    
    def _register_tools(self) -> None:
        """Register all Alfresco tools with the MCP server."""
        
        # Search tools
        @self.server.call_tool()
        async def search_content(arguments: dict) -> list[types.TextContent]:
            """Search for documents and folders in Alfresco."""
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 20)
            
            if not query.strip():
                return [types.TextContent(
                    type="text",
                    text="Error: Search query cannot be empty"
                )]
            
            try:
                await self._ensure_initialized()
                search_client = self.alfresco_factory.create_search_client()
                
                # Build search query
                search_request = search_models.SearchRequest(
                    query=search_models.RequestQuery(
                        query=f"({query}) AND NOT TYPE:'cm:thumbnail'",
                        language="afts"
                    ),
                    paging=search_models.RequestPagination(
                        maxItems=max_results,
                        skipCount=0
                    ),
                    include=["properties", "path"],
                    fields=["*"]
                )
                
                # Execute search
                results = await search_client.search(search_request)
                
                if not results or not results.list or not results.list.entries:
                    return [types.TextContent(
                        type="text",
                        text=f"No results found for query: {query}"
                    )]
                
                # Format results
                response_text = f"Search Results for '{query}' ({len(results.list.entries)} items):\n\n"
                
                for entry in results.list.entries:
                    node = entry.entry
                    name = node.name or "Unknown"
                    node_type = "Folder" if node.isFolder else "Document"
                    path = getattr(node, 'path', {}).get('name', 'Unknown Path') if hasattr(node, 'path') else 'Unknown Path'
                    
                    response_text += f"📄 {name}\n"
                    response_text += f"   Type: {node_type}\n"
                    response_text += f"   ID: {node.id}\n"
                    response_text += f"   Path: {path}\n"
                    response_text += f"   Modified: {getattr(node, 'modifiedAt', 'Unknown')}\n"
                    response_text += f"   Size: {getattr(node, 'content', {}).get('sizeInBytes', 'N/A')} bytes\n\n"
                
                return [types.TextContent(type="text", text=response_text)]
                
            except Exception as e:
                logger.error(f"Search failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Search failed: {str(e)}"
                )]
        
        # Document download tool
        @self.server.call_tool()
        async def download_document(arguments: dict) -> list[types.TextContent]:
            """Download a document from Alfresco."""
            node_id = arguments.get("node_id", "")
            
            if not node_id:
                return [types.TextContent(
                    type="text", 
                    text="Error: node_id is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Get document content
                content_response = await core_client.get_node_content(node_id)
                
                if content_response:
                    # For binary content, return base64 encoded
                    content_b64 = base64.b64encode(content_response).decode('utf-8')
                    
                    # Get node info for filename
                    node_info = await core_client.get_node(node_id)
                    filename = node_info.entry.name if node_info else f"document_{node_id}"
                    
                    return [types.TextContent(
                        type="text",
                        text=f"Document downloaded: {filename}\nContent (base64): {content_b64[:200]}..."
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to download document {node_id}"
                    )]
                    
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Download failed: {str(e)}"
                )]
        
        # Document upload tool
        @self.server.call_tool()
        async def upload_document(arguments: dict) -> list[types.TextContent]:
            """Upload a document to Alfresco."""
            parent_id = arguments.get("parent_id", "-root-")
            filename = arguments.get("filename", "")
            content_b64 = arguments.get("content_base64", "")
            description = arguments.get("description", "")
            
            if not filename or not content_b64:
                return [types.TextContent(
                    type="text",
                    text="Error: filename and content_base64 are required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Decode content
                content_bytes = base64.b64decode(content_b64)
                
                # Create node
                node_body = core_models.NodeBodyCreate(
                    name=filename,
                    nodeType="cm:content",
                    properties={
                        "cm:description": description
                    } if description else None
                )
                
                # Upload file
                response = await core_client.create_node(
                    node_id=parent_id,
                    node_body_create=node_body,
                    file_data=content_bytes,
                    name=filename
                )
                
                if response and response.entry:
                    return [types.TextContent(
                        type="text",
                        text=f"Document uploaded successfully:\n"
                             f"Name: {response.entry.name}\n"
                             f"ID: {response.entry.id}\n"
                             f"Size: {len(content_bytes)} bytes"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text="Upload failed - no response from server"
                    )]
                    
            except Exception as e:
                logger.error(f"Upload failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Upload failed: {str(e)}"
                )]
        
        # Checkout document tool
        @self.server.call_tool()
        async def checkout_document(arguments: dict) -> list[types.TextContent]:
            """Check out a document for editing."""
            node_id = arguments.get("node_id", "")
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Update node to check out
                response = await core_client.update_node(
                    node_id=node_id,
                    node_body_update=core_models.NodeBodyUpdate(
                        aspectNames=["cm:workingcopy"]
                    )
                )
                
                return [types.TextContent(
                    type="text",
                    text=f"Document {node_id} checked out successfully"
                )]
                
            except Exception as e:
                logger.error(f"Checkout failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Checkout failed: {str(e)}"
                )]
        
        # Checkin document tool
        @self.server.call_tool()
        async def checkin_document(arguments: dict) -> list[types.TextContent]:
            """Check in a document after editing."""
            node_id = arguments.get("node_id", "")
            comment = arguments.get("comment", "")
            major_version = arguments.get("major_version", False)
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Create new version
                version_body = core_models.VersionBodyCreate(
                    comment=comment,
                    majorVersion=major_version
                )
                
                response = await core_client.create_version(
                    node_id=node_id,
                    version_body_create=version_body
                )
                
                return [types.TextContent(
                    type="text",
                    text=f"Document {node_id} checked in successfully\n"
                         f"Version: {response.entry.id if response else 'Unknown'}\n"
                         f"Comment: {comment}"
                )]
                
            except Exception as e:
                logger.error(f"Checkin failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Checkin failed: {str(e)}"
                )]
        
        # Create folder tool
        @self.server.call_tool()
        async def create_folder(arguments: dict) -> list[types.TextContent]:
            """Create a new folder in Alfresco."""
            parent_id = arguments.get("parent_id", "-root-")
            folder_name = arguments.get("folder_name", "")
            description = arguments.get("description", "")
            
            if not folder_name:
                return [types.TextContent(
                    type="text",
                    text="Error: folder_name is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Create folder
                folder_body = core_models.NodeBodyCreate(
                    name=folder_name,
                    nodeType="cm:folder",
                    properties={
                        "cm:description": description
                    } if description else None
                )
                
                response = await core_client.create_node(
                    node_id=parent_id,
                    node_body_create=folder_body
                )
                
                if response and response.entry:
                    return [types.TextContent(
                        type="text",
                        text=f"Folder created successfully:\n"
                             f"Name: {response.entry.name}\n"
                             f"ID: {response.entry.id}\n"
                             f"Parent: {parent_id}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text="Folder creation failed - no response from server"
                    )]
                    
            except Exception as e:
                logger.error(f"Folder creation failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Folder creation failed: {str(e)}"
                )]
        
        # Delete node tool
        @self.server.call_tool()
        async def delete_node(arguments: dict) -> list[types.TextContent]:
            """Delete a document or folder."""
            node_id = arguments.get("node_id", "")
            permanent = arguments.get("permanent", False)
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Delete node
                await core_client.delete_node(
                    node_id=node_id,
                    permanent=permanent
                )
                
                action = "permanently deleted" if permanent else "moved to trash"
                return [types.TextContent(
                    type="text",
                    text=f"Node {node_id} {action} successfully"
                )]
                
            except Exception as e:
                logger.error(f"Delete failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Delete failed: {str(e)}"
                )]
        
        # Get node properties tool
        @self.server.call_tool()
        async def get_node_properties(arguments: dict) -> list[types.TextContent]:
            """Get properties of a node."""
            node_id = arguments.get("node_id", "")
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Get node info
                response = await core_client.get_node(node_id, include=["properties"])
                
                if response and response.entry:
                    node = response.entry
                    props_text = f"Properties for '{node.name}' (ID: {node.id}):\n\n"
                    props_text += f"Type: {'Folder' if node.isFolder else 'Document'}\n"
                    props_text += f"Created: {node.createdAt}\n"
                    props_text += f"Modified: {node.modifiedAt}\n"
                    props_text += f"Created By: {node.createdByUser.displayName}\n"
                    props_text += f"Modified By: {node.modifiedByUser.displayName}\n"
                    
                    if hasattr(node, 'properties') and node.properties:
                        props_text += "\nCustom Properties:\n"
                        for key, value in node.properties.items():
                            props_text += f"  {key}: {value}\n"
                    
                    return [types.TextContent(type="text", text=props_text)]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Node {node_id} not found"
                    )]
                    
            except Exception as e:
                logger.error(f"Get properties failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Get properties failed: {str(e)}"
                )]
        
        # Update node properties tool
        @self.server.call_tool()
        async def update_node_properties(arguments: dict) -> list[types.TextContent]:
            """Update properties of a node."""
            node_id = arguments.get("node_id", "")
            properties = arguments.get("properties", {})
            new_name = arguments.get("name")
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
                await self._ensure_initialized()
                core_client = self.alfresco_factory.create_core_client()
                
                # Build update body
                update_body = core_models.NodeBodyUpdate()
                
                if new_name:
                    update_body.name = new_name
                
                if properties:
                    update_body.properties = properties
                
                # Update node
                response = await core_client.update_node(
                    node_id=node_id,
                    node_body_update=update_body
                )
                
                if response and response.entry:
                    return [types.TextContent(
                        type="text",
                        text=f"Node {node_id} updated successfully:\n"
                             f"Name: {response.entry.name}\n"
                             f"Modified: {response.entry.modifiedAt}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Update failed for node {node_id}"
                    )]
                    
            except Exception as e:
                logger.error(f"Update properties failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Update properties failed: {str(e)}"
                )]
    
    def _register_resources(self) -> None:
        """Register MCP resources."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available Alfresco resources."""
            return [
                types.Resource(
                    uri="alfresco://repository",
                    name="Alfresco Repository",
                    description="Root of the Alfresco repository",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read Alfresco resource content."""
            if uri == "alfresco://repository":
                await self._ensure_initialized()
                return '{"status": "connected", "server": "' + self.config.alfresco_url + '"}'
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    def _register_prompts(self) -> None:
        """Register MCP prompts."""
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """List available prompts."""
            return [
                types.Prompt(
                    name="search-and-summarize",
                    description="Search for documents and provide a summary",
                    arguments=[
                        types.PromptArgument(
                            name="query",
                            description="Search query",
                            required=True
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: dict[str, str] | None
        ) -> types.GetPromptResult:
            """Handle prompt requests."""
            if name == "search-and-summarize":
                query = arguments.get("query", "") if arguments else ""
                
                return types.GetPromptResult(
                    description="Search and summarize Alfresco content",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"Please search for '{query}' in Alfresco and provide a brief summary."
                            )
                        )
                    ]
                )
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    async def _ensure_initialized(self) -> None:
        """Ensure Alfresco connection is initialized."""
        if not self.alfresco_factory or not self.auth_util:
            await self._initialize_alfresco()
    
    async def run_stdio(self) -> None:
        """Run the MCP server with stdio transport."""
        await self._initialize_alfresco()
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.config.server_name,
                    server_version=self.config.server_version,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get JSON schemas for all tools (useful for documentation)."""
        return [
            {
                "name": "search_content",
                "description": "Search for documents and folders in Alfresco",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 20}
                }
            },
            {
                "name": "download_document", 
                "description": "Download a document from Alfresco",
                "parameters": {
                    "node_id": {"type": "string", "description": "Document node ID", "required": True}
                }
            },
            {
                "name": "upload_document",
                "description": "Upload a document to Alfresco", 
                "parameters": {
                    "parent_id": {"type": "string", "description": "Parent folder ID", "default": "-root-"},
                    "filename": {"type": "string", "description": "File name", "required": True},
                    "content_base64": {"type": "string", "description": "Base64 encoded content", "required": True},
                    "description": {"type": "string", "description": "File description"}
                }
            },
            {
                "name": "checkout_document",
                "description": "Check out a document for editing",
                "parameters": {
                    "node_id": {"type": "string", "description": "Document node ID", "required": True}
                }
            },
            {
                "name": "checkin_document", 
                "description": "Check in a document after editing",
                "parameters": {
                    "node_id": {"type": "string", "description": "Document node ID", "required": True},
                    "comment": {"type": "string", "description": "Check-in comment"},
                    "major_version": {"type": "boolean", "description": "Create major version", "default": False}
                }
            },
            {
                "name": "create_folder",
                "description": "Create a new folder",
                "parameters": {
                    "parent_id": {"type": "string", "description": "Parent folder ID", "default": "-root-"},
                    "folder_name": {"type": "string", "description": "Folder name", "required": True},
                    "description": {"type": "string", "description": "Folder description"}
                }
            },
            {
                "name": "delete_node",
                "description": "Delete a document or folder",
                "parameters": {
                    "node_id": {"type": "string", "description": "Node ID", "required": True},
                    "permanent": {"type": "boolean", "description": "Permanent deletion", "default": False}
                }
            },
            {
                "name": "get_node_properties",
                "description": "Get properties of a node",
                "parameters": {
                    "node_id": {"type": "string", "description": "Node ID", "required": True}
                }
            },
            {
                "name": "update_node_properties",
                "description": "Update properties of a node",
                "parameters": {
                    "node_id": {"type": "string", "description": "Node ID", "required": True},
                    "properties": {"type": "object", "description": "Properties to update"},
                    "name": {"type": "string", "description": "New name for the node"}
                }
            }
        ] 

    async def search_content(self, query: str, max_results: int = 10, **kwargs) -> str:
        """Search for content in Alfresco using the search client wrapper"""
        try:
            await self._ensure_initialized()
            
            # Import the search models
            from python_alfresco_api.models.alfresco_search_models import SearchRequest, RequestQuery, RequestPagination
            
            # Create search request
            search_request = SearchRequest(
                query=RequestQuery(query=query),
                paging=RequestPagination(max_items=max_results, skip_count=0)
            )
            
            # Use the search client wrapper's search method
            search_client = self.alfresco_factory.create_search_client()
            result = await search_client.search(search_request)
            
            if result and hasattr(result, 'list') and hasattr(result.list, 'entries'):
                entries = result.list.entries
                
                if not entries:
                    return "No content found matching your search query."
                
                # Format results
                formatted_results = []
                for entry in entries:
                    node = entry.entry
                    name = getattr(node, 'name', 'Unknown')
                    node_type = getattr(node, 'node_type', 'Unknown')
                    modified = getattr(node, 'modified_at', 'Unknown')
                    path = getattr(getattr(node, 'path', None), 'name', 'Unknown') if hasattr(node, 'path') else 'Unknown'
                    
                    formatted_results.append(
                        f"• {name} ({node_type})\n"
                        f"  Path: {path}\n"
                        f"  Modified: {modified}"
                    )
                
                return f"Found {len(entries)} results:\n\n" + "\n\n".join(formatted_results)
            else:
                return f"Search completed but returned unexpected format: {type(result)}"
                    
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search failed: {str(e)}" 
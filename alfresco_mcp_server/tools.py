"""
Additional Alfresco tools for the MCP server.
"""

import base64
import logging
from typing import List

import mcp.types as types

logger = logging.getLogger(__name__)


class AlfrescoTools:
    """Additional Alfresco MCP tools."""
    
    def __init__(self, server, alfresco_factory):
        self.server = server
        self.alfresco_factory = alfresco_factory
        self._register_additional_tools()
    
    def _register_additional_tools(self) -> None:
        """Register additional Alfresco tools."""
        
        # Document download tool
        @self.server.call_tool()
        async def download_document(arguments: dict) -> List[types.TextContent]:
            """Download a document from Alfresco."""
            node_id = arguments.get("node_id", "")
            
            if not node_id:
                return [types.TextContent(
                    type="text", 
                    text="Error: node_id is required"
                )]
            
            try:
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
        async def upload_document(arguments: dict) -> List[types.TextContent]:
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
                from python_alfresco_api.models import alfresco_core_models as core_models
                
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
        async def checkout_document(arguments: dict) -> List[types.TextContent]:
            """Check out a document for editing."""
            node_id = arguments.get("node_id", "")
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
                from python_alfresco_api.models import alfresco_core_models as core_models
                
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
        async def checkin_document(arguments: dict) -> List[types.TextContent]:
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
                from python_alfresco_api.models import alfresco_core_models as core_models
                
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
        async def create_folder(arguments: dict) -> List[types.TextContent]:
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
                from python_alfresco_api.models import alfresco_core_models as core_models
                
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
        async def delete_node(arguments: dict) -> List[types.TextContent]:
            """Delete a document or folder."""
            node_id = arguments.get("node_id", "")
            permanent = arguments.get("permanent", False)
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
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
        async def get_node_properties(arguments: dict) -> List[types.TextContent]:
            """Get properties of a node."""
            node_id = arguments.get("node_id", "")
            
            if not node_id:
                return [types.TextContent(
                    type="text",
                    text="Error: node_id is required"
                )]
            
            try:
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
        async def update_node_properties(arguments: dict) -> List[types.TextContent]:
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
                from python_alfresco_api.models import alfresco_core_models as core_models
                
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
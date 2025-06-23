#!/usr/bin/env python3
"""
Document Lifecycle Example for Alfresco MCP Server

This example demonstrates a complete document management workflow:
- Creating folders and subfolders
- Uploading documents with metadata
- Searching and retrieving documents
- Updating document properties
- Document versioning (checkout/checkin)
- Organizing and managing content

This is a practical example showing real-world usage patterns.
"""

import asyncio
import base64
import uuid
from datetime import datetime
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


class DocumentLifecycleDemo:
    """Demonstrates complete document lifecycle management."""
    
    def __init__(self):
        self.session_id = uuid.uuid4().hex[:8]
        self.created_items = []  # Track items for cleanup
        
    async def run_demo(self):
        """Run the complete document lifecycle demonstration."""
        
        print("📄 Alfresco MCP Server - Document Lifecycle Demo")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        async with Client(mcp) as client:
            try:
                # Phase 1: Setup and Organization
                await self._phase_1_setup(client)
                
                # Phase 2: Document Creation and Upload
                await self._phase_2_upload(client)
                
                # Phase 3: Document Discovery and Search
                await self._phase_3_search(client)
                
                # Phase 4: Document Management
                await self._phase_4_management(client)
                
                # Phase 5: Versioning and Collaboration
                await self._phase_5_versioning(client)
                
                # Phase 6: Analysis and Reporting
                await self._phase_6_analysis(client)
                
                print("\n✅ Document Lifecycle Demo Completed Successfully!")
                
            except Exception as e:
                print(f"\n❌ Demo failed: {e}")
                raise
    
    async def _phase_1_setup(self, client):
        """Phase 1: Create organizational structure."""
        
        print("\n" + "="*60)
        print("📁 PHASE 1: Organizational Setup")
        print("="*60)
        
        # Create main project folder
        print("\n1️⃣ Creating main project folder...")
        main_folder = await client.call_tool("create_folder", {
            "folder_name": f"Project_Alpha_{self.session_id}",
            "parent_id": "-root-",
            "description": f"Main project folder created by MCP demo {self.session_id}"
        })
        print("📁 Main folder created:")
        print(main_folder[0].text)
        
        # Create subfolders for organization
        subfolders = [
            ("Documents", "Project documents and files"),
            ("Reports", "Analysis and status reports"),
            ("Archives", "Historical and backup documents"),
            ("Drafts", "Work-in-progress documents")
        ]
        
        print("\n2️⃣ Creating organizational subfolders...")
        for folder_name, description in subfolders:
            result = await client.call_tool("create_folder", {
                "folder_name": f"{folder_name}_{self.session_id}",
                "parent_id": "-root-",  # In real scenario, use main folder ID
                "description": description
            })
            print(f"  📂 {folder_name}: Created")
        
        # Get repository status
        print("\n3️⃣ Checking repository status...")
        repo_info = await client.read_resource("alfresco://repository/stats")
        print("📊 Repository Statistics:")
        print(repo_info[0].text)
    
    async def _phase_2_upload(self, client):
        """Phase 2: Upload various document types."""
        
        print("\n" + "="*60)
        print("📤 PHASE 2: Document Upload")
        print("="*60)
        
        # Sample documents to upload
        documents = [
            {
                "name": f"project_charter_{self.session_id}.txt",
                "content": "Project Charter\n\nProject: Alpha Initiative\nObjective: Implement MCP integration\nTimeline: Q1 2024\nStakeholders: Development, QA, Operations",
                "description": "Official project charter document"
            },
            {
                "name": f"meeting_notes_{self.session_id}.md",
                "content": "# Meeting Notes - Alpha Project\n\n## Date: 2024-01-15\n\n### Attendees\n- John Doe (PM)\n- Jane Smith (Dev)\n\n### Key Decisions\n1. Use FastMCP 2.0\n2. Implement comprehensive testing\n3. Deploy by end of Q1",
                "description": "Weekly project meeting notes"
            },
            {
                "name": f"technical_spec_{self.session_id}.json",
                "content": '{\n  "project": "Alpha",\n  "version": "1.0.0",\n  "technologies": ["Python", "FastMCP", "Alfresco"],\n  "requirements": {\n    "cpu": "2 cores",\n    "memory": "4GB",\n    "storage": "10GB"\n  }\n}',
                "description": "Technical specifications in JSON format"
            }
        ]
        
        print(f"\n1️⃣ Uploading {len(documents)} documents...")
        
        for i, doc in enumerate(documents, 1):
            print(f"\n  📄 Document {i}: {doc['name']}")
            
            # Encode content to base64
            content_b64 = base64.b64encode(doc['content'].encode('utf-8')).decode('utf-8')
            
            # Upload document
            result = await client.call_tool("upload_document", {
                "filename": doc['name'],
                "content_base64": content_b64,
                "parent_id": "-root-",  # In real scenario, use appropriate folder ID
                "description": doc['description']
            })
            
            print(f"    ✅ Upload status:")
            print(f"    {result[0].text}")
            
            # Simulate processing delay
            await asyncio.sleep(0.5)
        
        print(f"\n✅ All {len(documents)} documents uploaded successfully!")
    
    async def _phase_3_search(self, client):
        """Phase 3: Search and discovery operations."""
        
        print("\n" + "="*60)
        print("🔍 PHASE 3: Document Discovery")
        print("="*60)
        
        # Different search scenarios
        searches = [
            ("Project documents", f"Project_Alpha_{self.session_id}", "Find project-related content"),
            ("Meeting notes", "meeting", "Locate meeting documentation"),
            ("Technical files", "technical", "Find technical specifications"),
            ("All session content", self.session_id, "Find all demo content")
        ]
        
        print("\n1️⃣ Performing various search operations...")
        
        for i, (search_name, query, description) in enumerate(searches, 1):
            print(f"\n  🔎 Search {i}: {search_name}")
            print(f"      Query: '{query}'")
            print(f"      Purpose: {description}")
            
            result = await client.call_tool("search_content", {
                "query": query,
                "max_results": 10
            })
            
            print(f"      Results:")
            print(f"      {result[0].text}")
            
            await asyncio.sleep(0.3)
        
        # Advanced search with analysis
        print("\n2️⃣ Advanced search with analysis...")
        prompt_result = await client.get_prompt("search_and_analyze", {
            "query": f"session {self.session_id}",
            "analysis_type": "detailed"
        })
        
        print("📊 Generated Analysis Prompt:")
        print(prompt_result.messages[0].content.text[:400] + "...")
    
    async def _phase_4_management(self, client):
        """Phase 4: Document properties and metadata management."""
        
        print("\n" + "="*60)
        print("⚙️ PHASE 4: Document Management")
        print("="*60)
        
        print("\n1️⃣ Retrieving document properties...")
        
        # Get properties of root folder (as example)
        props_result = await client.call_tool("get_node_properties", {
            "node_id": "-root-"
        })
        
        print("📋 Root folder properties:")
        print(props_result[0].text)
        
        print("\n2️⃣ Updating document metadata...")
        
        # Update properties (simulated)
        update_result = await client.call_tool("update_node_properties", {
            "node_id": "-root-",  # In real scenario, use actual document ID
            "properties": {
                "cm:title": f"Alpha Project Root - {self.session_id}",
                "cm:description": "Updated via MCP demo",
                "custom:project": "Alpha Initiative"
            }
        })
        
        print("📝 Property update result:")
        print(update_result[0].text)
        
        print("\n3️⃣ Repository health check...")
        health = await client.read_resource("alfresco://repository/health")
        print("🏥 Repository Health:")
        print(health[0].text)
    
    async def _phase_5_versioning(self, client):
        """Phase 5: Document versioning and collaboration."""
        
        print("\n" + "="*60)
        print("🔄 PHASE 5: Versioning & Collaboration")
        print("="*60)
        
        # Simulate document checkout/checkin workflow
        doc_id = f"test-doc-{self.session_id}"
        
        print("\n1️⃣ Document checkout process...")
        checkout_result = await client.call_tool("checkout_document", {
            "node_id": doc_id
        })
        
        print("🔒 Checkout result:")
        print(checkout_result[0].text)
        
        print("\n2️⃣ Document checkin with new version...")
        checkin_result = await client.call_tool("checkin_document", {
            "node_id": doc_id,
            "comment": f"Updated during MCP demo session {self.session_id}",
            "major_version": False  # Minor version increment
        })
        
        print("🔓 Checkin result:")
        print(checkin_result[0].text)
        
        print("\n3️⃣ Major version checkin...")
        major_checkin = await client.call_tool("checkin_document", {
            "node_id": doc_id,
            "comment": f"Major release - Demo session {self.session_id} complete",
            "major_version": True  # Major version increment
        })
        
        print("📈 Major version result:")
        print(major_checkin[0].text)
    
    async def _phase_6_analysis(self, client):
        """Phase 6: Analysis and reporting."""
        
        print("\n" + "="*60)
        print("📊 PHASE 6: Analysis & Reporting")
        print("="*60)
        
        print("\n1️⃣ Repository configuration analysis...")
        config = await client.read_resource("alfresco://repository/config")
        print("⚙️ Current Configuration:")
        print(config[0].text)
        
        print("\n2️⃣ Generating comprehensive analysis prompts...")
        
        analysis_types = ["summary", "detailed", "trends", "compliance"]
        
        for analysis_type in analysis_types:
            print(f"\n  📋 {analysis_type.title()} Analysis:")
            prompt = await client.get_prompt("search_and_analyze", {
                "query": f"Project Alpha {self.session_id}",
                "analysis_type": analysis_type
            })
            
            # Show first part of prompt
            content = prompt.messages[0].content.text
            preview = content.split('\n')[0:3]  # First 3 lines
            print(f"      {' '.join(preview)[:100]}...")
        
        print("\n3️⃣ Final repository status...")
        final_stats = await client.read_resource("alfresco://repository/stats")
        print("📈 Final Repository Statistics:")
        print(final_stats[0].text)
        
        print(f"\n4️⃣ Demo session summary...")
        print(f"   Session ID: {self.session_id}")
        print(f"   Duration: Demo complete")
        print(f"   Operations: Folder creation, document upload, search, versioning")
        print(f"   Status: ✅ All operations successful")


async def main():
    """Main function to run the document lifecycle demo."""
    
    print("Starting Document Lifecycle Demo...")
    
    demo = DocumentLifecycleDemo()
    
    try:
        await demo.run_demo()
        
        print("\n🎉 Document Lifecycle Demo Completed Successfully!")
        print("\n📚 What you learned:")
        print("- Complete document management workflow")
        print("- Folder organization strategies")
        print("- Document upload and metadata handling")
        print("- Search and discovery techniques")
        print("- Version control operations")
        print("- Repository monitoring and analysis")
        
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        print("Check your Alfresco connection and try again.")


if __name__ == "__main__":
    asyncio.run(main()) 
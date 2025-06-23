#!/usr/bin/env python3
"""
Batch Operations Example for Alfresco MCP Server

This example demonstrates efficient batch processing patterns:
- Bulk document uploads
- Parallel search operations
- Batch metadata updates
- Concurrent folder creation
- Performance optimization techniques

Useful for processing large numbers of documents or automating
repetitive tasks.
"""

import asyncio
import base64
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


class BatchOperationsDemo:
    """Demonstrates efficient batch processing with Alfresco MCP Server."""
    
    def __init__(self):
        self.session_id = uuid.uuid4().hex[:8]
        self.batch_size = 5  # Number of operations per batch
        
    async def run_batch_demo(self):
        """Run comprehensive batch operations demonstration."""
        
        print("📦 Alfresco MCP Server - Batch Operations Demo")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Batch Size: {self.batch_size}")
        
        async with Client(mcp) as client:
            # Demo 1: Bulk Document Upload
            await self._demo_bulk_upload(client)
            
            # Demo 2: Parallel Search Operations
            await self._demo_parallel_search(client)
            
            # Demo 3: Batch Folder Creation
            await self._demo_batch_folders(client)
            
            # Demo 4: Concurrent Property Updates
            await self._demo_batch_properties(client)
            
            # Demo 5: Performance Comparison
            await self._demo_performance_comparison(client)
            
            print("\n✅ Batch Operations Demo Complete!")
    
    async def _demo_bulk_upload(self, client):
        """Demonstrate bulk document upload with progress tracking."""
        
        print("\n" + "="*60)
        print("📤 Demo 1: Bulk Document Upload")
        print("="*60)
        
        # Generate sample documents
        documents = self._generate_sample_documents(10)
        
        print(f"\n📋 Uploading {len(documents)} documents...")
        print("   Strategy: Async batch processing with progress tracking")
        
        start_time = time.time()
        
        # Method 1: Sequential upload (for comparison)
        print("\n1️⃣ Sequential Upload:")
        sequential_start = time.time()
        
        for i, doc in enumerate(documents[:3], 1):  # Only 3 for demo
            print(f"   📄 Uploading document {i}/3: {doc['name']}")
            
            result = await client.call_tool("upload_document", {
                "filename": doc['name'],
                "content_base64": doc['content_b64'],
                "parent_id": "-root-",
                "description": doc['description']
            })
            
            if "✅" in result[0].text:
                print(f"   ✅ Document {i} uploaded successfully")
            else:
                print(f"   ❌ Document {i} failed")
        
        sequential_time = time.time() - sequential_start
        print(f"   ⏱️  Sequential time: {sequential_time:.2f}s")
        
        # Method 2: Batch upload with semaphore
        print("\n2️⃣ Concurrent Upload (with rate limiting):")
        concurrent_start = time.time()
        
        semaphore = asyncio.Semaphore(3)  # Limit concurrent uploads
        
        async def upload_with_limit(doc, index):
            async with semaphore:
                print(f"   📄 Starting upload {index}: {doc['name']}")
                
                result = await client.call_tool("upload_document", {
                    "filename": doc['name'],
                    "content_base64": doc['content_b64'],
                    "parent_id": "-root-",
                    "description": doc['description']
                })
                
                success = "✅" in result[0].text
                print(f"   {'✅' if success else '❌'} Upload {index} completed")
                return success
        
        # Upload remaining documents concurrently
        remaining_docs = documents[3:8]  # Next 5 documents
        tasks = [
            upload_with_limit(doc, i+4) 
            for i, doc in enumerate(remaining_docs)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrent_time = time.time() - concurrent_start
        successful = sum(1 for r in results if r is True)
        
        print(f"   ⏱️  Concurrent time: {concurrent_time:.2f}s")
        print(f"   📊 Success rate: {successful}/{len(remaining_docs)}")
        print(f"   🚀 Speed improvement: {sequential_time/concurrent_time:.1f}x faster")
    
    async def _demo_parallel_search(self, client):
        """Demonstrate parallel search operations."""
        
        print("\n" + "="*60)
        print("🔍 Demo 2: Parallel Search Operations")
        print("="*60)
        
        # Different search queries to run in parallel
        search_queries = [
            ("Content search", "*", 10),
            ("Session docs", self.session_id, 5),
            ("Test files", "test", 8),
            ("Documents", "document", 12),
            ("Recent items", "2024", 15)
        ]
        
        print(f"\n📋 Running {len(search_queries)} searches in parallel...")
        
        start_time = time.time()
        
        async def parallel_search(query_info):
            name, query, max_results = query_info
            print(f"   🔎 Starting: {name} ('{query}')")
            
            try:
                result = await client.call_tool("search_content", {
                    "query": query,
                    "max_results": max_results
                })
                
                # Extract result count from response
                response_text = result[0].text
                if "Found" in response_text:
                    print(f"   ✅ {name}: Completed")
                else:
                    print(f"   📝 {name}: No results")
                
                return name, True, response_text
                
            except Exception as e:
                print(f"   ❌ {name}: Failed - {e}")
                return name, False, str(e)
        
        # Execute all searches in parallel
        search_tasks = [parallel_search(query) for query in search_queries]
        search_results = await asyncio.gather(*search_tasks)
        
        parallel_time = time.time() - start_time
        
        print(f"\n📊 Parallel Search Results:")
        print(f"   ⏱️  Total time: {parallel_time:.2f}s")
        print(f"   🎯 Searches completed: {len(search_results)}")
        
        successful = sum(1 for _, success, _ in search_results if success)
        print(f"   ✅ Success rate: {successful}/{len(search_results)}")
        
        # Show estimated sequential time
        avg_search_time = 0.5  # Estimate 500ms per search
        estimated_sequential = len(search_queries) * avg_search_time
        print(f"   🚀 vs Sequential (~{estimated_sequential:.1f}s): {estimated_sequential/parallel_time:.1f}x faster")
    
    async def _demo_batch_folders(self, client):
        """Demonstrate batch folder creation with hierarchical structure."""
        
        print("\n" + "="*60)
        print("📁 Demo 3: Batch Folder Creation")
        print("="*60)
        
        # Define folder structure
        folder_structure = [
            ("Projects", "Main projects folder"),
            ("Archives", "Archived projects"),
            ("Templates", "Document templates"),
            ("Reports", "Generated reports"),
            ("Temp", "Temporary workspace")
        ]
        
        print(f"\n📋 Creating {len(folder_structure)} folders concurrently...")
        
        async def create_folder_async(folder_info, index):
            name, description = folder_info
            folder_name = f"{name}_{self.session_id}"
            
            print(f"   📂 Creating folder {index+1}: {folder_name}")
            
            try:
                result = await client.call_tool("create_folder", {
                    "folder_name": folder_name,
                    "parent_id": "-root-",
                    "description": f"{description} - Batch demo {self.session_id}"
                })
                
                success = "✅" in result[0].text
                print(f"   {'✅' if success else '❌'} Folder {index+1}: {folder_name}")
                return success
                
            except Exception as e:
                print(f"   ❌ Folder {index+1} failed: {e}")
                return False
        
        start_time = time.time()
        
        # Create all folders concurrently
        folder_tasks = [
            create_folder_async(folder, i) 
            for i, folder in enumerate(folder_structure)
        ]
        
        folder_results = await asyncio.gather(*folder_tasks, return_exceptions=True)
        
        creation_time = time.time() - start_time
        successful_folders = sum(1 for r in folder_results if r is True)
        
        print(f"\n📊 Batch Folder Creation Results:")
        print(f"   ⏱️  Creation time: {creation_time:.2f}s")
        print(f"   ✅ Folders created: {successful_folders}/{len(folder_structure)}")
        print(f"   📈 Average time per folder: {creation_time/len(folder_structure):.2f}s")
    
    async def _demo_batch_properties(self, client):
        """Demonstrate batch property updates."""
        
        print("\n" + "="*60)
        print("⚙️ Demo 4: Batch Property Updates")
        print("="*60)
        
        # Simulate updating properties on multiple nodes
        node_updates = [
            ("-root-", {"cm:title": f"Root Updated {self.session_id}", "cm:description": "Batch update demo"}),
            ("-root-", {"custom:project": "Batch Demo", "custom:session": self.session_id}),
            ("-root-", {"cm:tags": "demo,batch,mcp", "custom:timestamp": str(int(time.time()))}),
        ]
        
        print(f"\n📋 Updating properties on {len(node_updates)} nodes...")
        
        async def update_properties_async(update_info, index):
            node_id, properties = update_info
            
            print(f"   ⚙️ Updating properties {index+1}: {len(properties)} properties")
            
            try:
                result = await client.call_tool("update_node_properties", {
                    "node_id": node_id,
                    "properties": properties
                })
                
                success = "✅" in result[0].text
                print(f"   {'✅' if success else '❌'} Properties {index+1} updated")
                return success
                
            except Exception as e:
                print(f"   ❌ Properties {index+1} failed: {e}")
                return False
        
        start_time = time.time()
        
        # Update all properties concurrently
        update_tasks = [
            update_properties_async(update, i) 
            for i, update in enumerate(node_updates)
        ]
        
        update_results = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        update_time = time.time() - start_time
        successful_updates = sum(1 for r in update_results if r is True)
        
        print(f"\n📊 Batch Property Update Results:")
        print(f"   ⏱️  Update time: {update_time:.2f}s")
        print(f"   ✅ Updates completed: {successful_updates}/{len(node_updates)}")
    
    async def _demo_performance_comparison(self, client):
        """Compare sequential vs concurrent operation performance."""
        
        print("\n" + "="*60)
        print("⚡ Demo 5: Performance Comparison")
        print("="*60)
        
        # Test operations
        operations = [
            ("search", "search_content", {"query": f"test_{i}", "max_results": 3})
            for i in range(5)
        ]
        
        print(f"\n📊 Comparing sequential vs concurrent execution...")
        print(f"   Operations: {len(operations)} search operations")
        
        # Sequential execution
        print("\n1️⃣ Sequential Execution:")
        sequential_start = time.time()
        
        for i, (op_type, tool_name, params) in enumerate(operations):
            print(f"   🔄 Operation {i+1}/{len(operations)}")
            try:
                await client.call_tool(tool_name, params)
                print(f"   ✅ Operation {i+1} completed")
            except Exception as e:
                print(f"   ❌ Operation {i+1} failed: {e}")
        
        sequential_time = time.time() - sequential_start
        
        # Concurrent execution
        print("\n2️⃣ Concurrent Execution:")
        concurrent_start = time.time()
        
        async def execute_operation(op_info, index):
            op_type, tool_name, params = op_info
            print(f"   🔄 Starting operation {index+1}")
            
            try:
                await client.call_tool(tool_name, params)
                print(f"   ✅ Operation {index+1} completed")
                return True
            except Exception as e:
                print(f"   ❌ Operation {index+1} failed: {e}")
                return False
        
        concurrent_tasks = [
            execute_operation(op, i) 
            for i, op in enumerate(operations)
        ]
        
        concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        concurrent_time = time.time() - concurrent_start
        
        # Performance summary
        print(f"\n📈 Performance Comparison Results:")
        print(f"   Sequential time: {sequential_time:.2f}s")
        print(f"   Concurrent time: {concurrent_time:.2f}s")
        print(f"   Speed improvement: {sequential_time/concurrent_time:.1f}x")
        print(f"   Time saved: {sequential_time-concurrent_time:.2f}s ({(1-concurrent_time/sequential_time)*100:.1f}%)")
        
        print(f"\n💡 Batch Processing Best Practices:")
        print(f"   • Use async/await for I/O bound operations")
        print(f"   • Implement rate limiting with semaphores")
        print(f"   • Handle exceptions gracefully in batch operations")
        print(f"   • Monitor progress with appropriate logging")
        print(f"   • Consider memory usage for large batches")
    
    def _generate_sample_documents(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample documents for testing."""
        
        documents = []
        
        for i in range(count):
            content = f"""Document {i+1}
            
Session: {self.session_id}
Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
Type: Batch Demo Document
Index: {i+1} of {count}

This is a sample document created during the batch operations demo.
It contains some sample content for testing purposes.

Content sections:
- Introduction
- Main content  
- Conclusion

Document properties:
- Unique ID: {uuid.uuid4()}
- Processing batch: {self.session_id}
- Creation timestamp: {int(time.time())}
"""
            
            documents.append({
                "name": f"batch_doc_{self.session_id}_{i+1:03d}.txt",
                "content": content,
                "content_b64": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                "description": f"Batch demo document {i+1} from session {self.session_id}"
            })
        
        return documents


async def main():
    """Main function to run batch operations demo."""
    
    print("Starting Batch Operations Demo...")
    
    try:
        demo = BatchOperationsDemo()
        await demo.run_batch_demo()
        
        print("\n🎉 Batch Operations Demo Complete!")
        print("\n📚 What you learned:")
        print("• Efficient batch document upload patterns")
        print("• Parallel search operation techniques")
        print("• Concurrent folder creation strategies")
        print("• Batch property update methods")
        print("• Performance optimization approaches")
        print("• Rate limiting and error handling")
        
    except Exception as e:
        print(f"\n💥 Batch demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 
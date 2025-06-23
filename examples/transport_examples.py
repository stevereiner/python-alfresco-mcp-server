#!/usr/bin/env python3
"""
Transport Examples for Alfresco MCP Server

This example demonstrates how to connect to the Alfresco MCP Server
using different transport protocols:

1. STDIO (Standard Input/Output) - Default MCP protocol
2. HTTP - RESTful HTTP transport  
3. SSE (Server-Sent Events) - Event streaming transport

Each transport has different use cases and benefits.
"""

import asyncio
import subprocess
import time
import httpx
from fastmcp import Client, StdioServerTransport, HttpServerTransport, SseServerTransport
from alfresco_mcp_server.fastmcp_server import mcp


class TransportDemonstrator:
    """Demonstrates different MCP transport protocols."""
    
    def __init__(self):
        self.demo_query = "alfresco"
        
    async def demonstrate_all_transports(self):
        """Run demonstrations of all available transport protocols."""
        
        print("🌐 Alfresco MCP Server - Transport Protocol Examples")
        print("=" * 65)
        
        # Test each transport
        await self._demo_stdio_transport()
        await self._demo_http_transport()
        await self._demo_sse_transport()
        
        print("\n✅ All Transport Demonstrations Complete!")
        print("\n📊 Transport Comparison Summary:")
        print("┌─────────────┬───────────────┬─────────────────┬────────────────┐")
        print("│ Transport   │ Use Case      │ Pros            │ Cons           │")
        print("├─────────────┼───────────────┼─────────────────┼────────────────┤")
        print("│ STDIO       │ CLI tools     │ Simple, fast    │ Local only     │")
        print("│ HTTP        │ Web services  │ Standard, REST  │ Request/reply  │")
        print("│ SSE         │ Real-time     │ Streaming       │ Complex setup  │")
        print("└─────────────┴───────────────┴─────────────────┴────────────────┘")
    
    async def _demo_stdio_transport(self):
        """Demonstrate STDIO transport (default MCP protocol)."""
        
        print("\n" + "="*65)
        print("📟 STDIO Transport Demonstration")
        print("="*65)
        
        print("\n📋 STDIO Transport Characteristics:")
        print("   • Standard MCP protocol over stdin/stdout")
        print("   • Best for: CLI tools, scripts, local integrations")
        print("   • Connection: Direct in-process communication")
        print("   • Performance: Fastest (no network overhead)")
        
        try:
            print("\n1️⃣ Connecting via STDIO transport...")
            
            # Use the direct MCP server instance (in-process)
            async with Client(mcp) as client:
                print("✅ STDIO connection established!")
                
                # Demonstrate basic operations
                await self._run_basic_operations(client, "STDIO")
                
        except Exception as e:
            print(f"❌ STDIO demo failed: {e}")
    
    async def _demo_http_transport(self):
        """Demonstrate HTTP transport."""
        
        print("\n" + "="*65)
        print("🌐 HTTP Transport Demonstration")
        print("="*65)
        
        print("\n📋 HTTP Transport Characteristics:")
        print("   • RESTful HTTP API over TCP")
        print("   • Best for: Web services, remote clients, microservices")
        print("   • Connection: HTTP requests to server endpoint")
        print("   • Performance: Good (standard HTTP overhead)")
        
        # Start HTTP server in background
        server_process = None
        try:
            print("\n1️⃣ Starting HTTP server...")
            
            # Start the FastMCP server with HTTP transport
            server_process = subprocess.Popen([
                "python", "-m", "alfresco_mcp_server.fastmcp_server",
                "--transport", "http",
                "--host", "127.0.0.1", 
                "--port", "8002"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("⏳ Waiting for HTTP server to start...")
            await asyncio.sleep(3)
            
            # Check if server is running
            try:
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get("http://127.0.0.1:8002/health", timeout=5.0)
                    if response.status_code == 200:
                        print("✅ HTTP server is running!")
                    else:
                        print(f"⚠️  HTTP server responded with status: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Could not verify HTTP server: {e}")
            
            print("\n2️⃣ Connecting via HTTP transport...")
            
            # Connect using HTTP transport
            transport = HttpServerTransport("http://127.0.0.1:8002")
            async with Client(transport) as client:
                print("✅ HTTP connection established!")
                
                # Demonstrate basic operations
                await self._run_basic_operations(client, "HTTP")
                
        except Exception as e:
            print(f"❌ HTTP demo failed: {e}")
            print("💡 Note: HTTP transport requires server to be running on specified port")
            
        finally:
            if server_process:
                print("\n🛑 Shutting down HTTP server...")
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()
    
    async def _demo_sse_transport(self):
        """Demonstrate Server-Sent Events (SSE) transport."""
        
        print("\n" + "="*65)
        print("📡 SSE (Server-Sent Events) Transport Demonstration")
        print("="*65)
        
        print("\n📋 SSE Transport Characteristics:")
        print("   • Event streaming over HTTP")
        print("   • Best for: Real-time updates, notifications, live data")
        print("   • Connection: Persistent HTTP connection with event stream")
        print("   • Performance: Excellent for real-time scenarios")
        
        # Start SSE server in background
        server_process = None
        try:
            print("\n1️⃣ Starting SSE server...")
            
            # Start the FastMCP server with SSE transport
            server_process = subprocess.Popen([
                "python", "-m", "alfresco_mcp_server.fastmcp_server",
                "--transport", "sse",
                "--host", "127.0.0.1",
                "--port", "8003"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("⏳ Waiting for SSE server to start...")
            await asyncio.sleep(3)
            
            print("\n2️⃣ Connecting via SSE transport...")
            
            # Connect using SSE transport
            transport = SseServerTransport("http://127.0.0.1:8003")
            async with Client(transport) as client:
                print("✅ SSE connection established!")
                
                # Demonstrate basic operations with real-time feel
                await self._run_basic_operations(client, "SSE")
                
                # SSE-specific demonstration: Real-time search
                print("\n🔄 SSE-specific: Real-time search simulation...")
                for i in range(3):
                    print(f"   📡 Real-time search {i+1}/3...")
                    result = await client.call_tool("search_content", {
                        "query": f"{self.demo_query} {i+1}",
                        "max_results": 3
                    })
                    print(f"   ✅ Search {i+1} completed")
                    await asyncio.sleep(1)  # Simulate real-time updates
                
        except Exception as e:
            print(f"❌ SSE demo failed: {e}")
            print("💡 Note: SSE transport requires server to be running on specified port")
            
        finally:
            if server_process:
                print("\n🛑 Shutting down SSE server...")
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()
    
    async def _run_basic_operations(self, client, transport_name):
        """Run basic MCP operations to demonstrate transport functionality."""
        
        print(f"\n🔧 Running basic operations via {transport_name}...")
        
        # 1. List available tools
        print("   📋 Listing tools...")
        tools = await client.list_tools()
        print(f"   ✅ Found {len(tools)} tools")
        
        # 2. List available resources  
        print("   📚 Listing resources...")
        resources = await client.list_resources()
        print(f"   ✅ Found {len(resources)} resources")
        
        # 3. List available prompts
        print("   💭 Listing prompts...")
        prompts = await client.list_prompts()
        print(f"   ✅ Found {len(prompts)} prompts")
        
        # 4. Test a tool call
        print("   🔍 Testing search tool...")
        search_result = await client.call_tool("search_content", {
            "query": self.demo_query,
            "max_results": 3
        })
        print("   ✅ Search completed")
        
        # 5. Test resource access
        print("   📊 Testing resource access...")
        try:
            resource = await client.read_resource("alfresco://repository/info")
            print("   ✅ Resource access successful")
        except Exception as e:
            print(f"   ⚠️  Resource access: {e}")
        
        # 6. Test prompt generation
        print("   💡 Testing prompt generation...")
        try:
            prompt = await client.get_prompt("search_and_analyze", {
                "query": self.demo_query,
                "analysis_type": "summary"
            })
            print("   ✅ Prompt generation successful")
        except Exception as e:
            print(f"   ⚠️  Prompt generation: {e}")
        
        print(f"   🎉 {transport_name} transport demonstration complete!")


class TransportPerformanceComparison:
    """Compare performance characteristics of different transports."""
    
    async def run_performance_tests(self):
        """Run performance comparison between transports."""
        
        print("\n" + "="*65)
        print("⚡ Transport Performance Comparison")
        print("="*65)
        
        print("\n📊 Testing search performance across transports...")
        
        # Test STDIO performance
        stdio_time = await self._measure_stdio_performance()
        
        print(f"\n📈 Performance Results:")
        print(f"   STDIO: {stdio_time:.2f}s (baseline)")
        print(f"\n💡 Performance Notes:")
        print(f"   • STDIO is fastest (no network overhead)")
        print(f"   • HTTP adds network latency (~50-100ms per request)")
        print(f"   • SSE is best for real-time streaming scenarios")
        print(f"   • Choose transport based on your architecture needs")
    
    async def _measure_stdio_performance(self):
        """Measure STDIO transport performance."""
        
        start_time = time.time()
        
        try:
            async with Client(mcp) as client:
                # Perform multiple operations
                await client.list_tools()
                await client.call_tool("search_content", {
                    "query": "test",
                    "max_results": 5
                })
                await client.read_resource("alfresco://repository/info")
        except Exception:
            pass  # Ignore errors for performance testing
        
        return time.time() - start_time


async def main():
    """Main function to run transport demonstrations."""
    
    print("Starting Transport Protocol Demonstrations...")
    
    try:
        # Run transport demonstrations
        demo = TransportDemonstrator()
        await demo.demonstrate_all_transports()
        
        # Run performance comparison
        perf = TransportPerformanceComparison()
        await perf.run_performance_tests()
        
        print("\n🎉 Transport Examples Complete!")
        print("\n📚 Key Takeaways:")
        print("• STDIO: Best for local tools and scripts")
        print("• HTTP: Ideal for web services and remote access")
        print("• SSE: Perfect for real-time applications")
        print("• All transports support the same MCP functionality")
        print("• Choose based on your architecture and requirements")
        
    except Exception as e:
        print(f"\n💥 Transport demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 
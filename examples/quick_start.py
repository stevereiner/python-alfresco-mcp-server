#!/usr/bin/env python3
"""
Quick Start Example for Alfresco MCP Server

This example demonstrates:
- Basic server connection
- Making your first tool call
- Handling responses
- Simple error handling

Prerequisites:
- Alfresco MCP Server running
- Environment variables set (ALFRESCO_URL, ALFRESCO_USERNAME, ALFRESCO_PASSWORD)
"""

import asyncio
import os
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


async def quick_start_example():
    """Quick start example showing basic MCP server usage."""
    
    print("🚀 Alfresco MCP Server - Quick Start Example")
    print("=" * 50)
    
    # Check environment setup
    print("\n📋 Checking Environment Setup...")
    required_vars = ["ALFRESCO_URL", "ALFRESCO_USERNAME", "ALFRESCO_PASSWORD"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set (using defaults)")
    
    try:
        # Connect to the MCP server
        print("\n🔌 Connecting to MCP Server...")
        async with Client(mcp) as client:
            print("✅ Connected successfully!")
            
            # List available tools
            print("\n🛠️ Available Tools:")
            tools = await client.list_tools()
            for i, tool in enumerate(tools, 1):
                print(f"  {i:2d}. {tool.name} - {tool.description}")
            
            # List available resources
            print("\n📚 Available Resources:")
            resources = await client.list_resources()
            for i, resource in enumerate(resources, 1):
                print(f"  {i:2d}. {resource.uri}")
            
            # List available prompts
            print("\n💭 Available Prompts:")
            prompts = await client.list_prompts()
            for i, prompt in enumerate(prompts, 1):
                print(f"  {i:2d}. {prompt.name} - {prompt.description}")
            
            # Example 1: Simple search
            print("\n🔍 Example 1: Simple Document Search")
            print("-" * 40)
            search_result = await client.call_tool("search_content", {
                "query": "*",  # Search for all documents
                "max_results": 5
            })
            
            if search_result:
                print("Search Result:")
                print(search_result[0].text)
            
            # Example 2: Get repository info
            print("\n📊 Example 2: Repository Information")
            print("-" * 40)
            repo_info = await client.read_resource("alfresco://repository/info")
            if repo_info:
                print("Repository Info:")
                print(repo_info[0].text)
            
            # Example 3: Create a test folder
            print("\n📁 Example 3: Create Test Folder")
            print("-" * 40)
            folder_result = await client.call_tool("create_folder", {
                "folder_name": f"MCP_Test_Folder_{asyncio.current_task().get_name()}",
                "parent_id": "-root-",
                "description": "Test folder created by MCP Quick Start example"
            })
            
            if folder_result:
                print("Folder Creation Result:")
                print(folder_result[0].text)
            
            # Example 4: Get analysis prompt
            print("\n💡 Example 4: Analysis Prompt")
            print("-" * 40)
            prompt_result = await client.get_prompt("search_and_analyze", {
                "query": "financial reports",
                "analysis_type": "summary"
            })
            
            if prompt_result.messages:
                print("Generated Prompt:")
                print(prompt_result.messages[0].content.text[:300] + "...")
            
            print("\n✅ Quick Start Complete!")
            print("Next steps:")
            print("- Explore other examples in this directory")
            print("- Check the documentation in ../docs/")
            print("- Try the document lifecycle example")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Alfresco server is running")
        print("2. Check environment variables")
        print("3. Verify network connectivity")
        return False
    
    return True


def main():
    """Main function to run the quick start example."""
    print("Starting Alfresco MCP Server Quick Start Example...")
    
    # Run the async example
    success = asyncio.run(quick_start_example())
    
    if success:
        print("\n🎉 Example completed successfully!")
    else:
        print("\n💥 Example failed. Please check the error messages above.")


if __name__ == "__main__":
    main() 
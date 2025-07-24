#!/usr/bin/env python3
"""
Simple wrapper to run the Alfresco MCP Server
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from alfresco_mcp_server.fastmcp_server import mcp

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Alfresco MCP Server")
    parser.add_argument("--port", type=int, default=8003, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--transport", type=str, default="http", choices=["stdio", "http", "sse"], help="Transport method to use")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        print(">> Starting Alfresco MCP Server with stdio transport")
        mcp.run(transport="stdio")
    elif args.transport == "http":
        print(f">> Starting Alfresco MCP Server with HTTP transport on {args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        print(f">> Starting Alfresco MCP Server with SSE transport on {args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port) 
"""
Main entry point for Alfresco MCP Server.

Supports multiple transport methods:
- stdio: For direct MCP client connections
- FastAPI: For HTTP-based access and testing
"""

import asyncio
import logging
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import load_config
from .server import AlfrescoMCPServer
from .fastapi_transport import create_fastapi_app


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("alfresco_mcp_server.log")
        ]
    )


async def run_stdio_server() -> None:
    """Run the MCP server with stdio transport."""
    config = load_config()
    setup_logging(config.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Alfresco MCP Server with stdio transport")
    
    server = AlfrescoMCPServer(config)
    
    try:
        await server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def run_fastapi_server() -> None:
    """Run the MCP server with FastAPI HTTP transport."""
    config = load_config()
    setup_logging(config.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Alfresco MCP Server with FastAPI on {config.fastapi_host}:{config.fastapi_port}")
    
    # Create FastAPI app
    app = create_fastapi_app(config)
    
    # Run server
    uvicorn.run(
        app,
        host=config.fastapi_host,
        port=config.fastapi_port,
        log_level=config.log_level.lower(),
        access_log=True
    )


def main() -> None:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alfresco MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "fastapi"],
        default="stdio",
        help="Transport method (default: stdio)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        asyncio.run(run_stdio_server())
    elif args.transport == "fastapi":
        run_fastapi_server()


if __name__ == "__main__":
    main() 
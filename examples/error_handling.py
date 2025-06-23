#!/usr/bin/env python3
"""
Error Handling Example for Alfresco MCP Server

This example demonstrates robust error handling patterns:
- Connection error recovery
- Authentication failure handling
- Timeout management
- Graceful degradation
- Retry mechanisms
- Logging and monitoring

Essential patterns for production deployments.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alfresco_mcp_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RobustAlfrescoClient:
    """Production-ready Alfresco MCP client with comprehensive error handling."""
    
    def __init__(self, max_retries=3, retry_delay=1.0, timeout=30.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.last_error = None
        
    async def safe_call_tool(self, tool_name: str, parameters: Dict[str, Any], 
                           retry_count: int = 0) -> Optional[str]:
        """
        Safely call a tool with comprehensive error handling.
        
        Args:
            tool_name: Name of the MCP tool to call
            parameters: Tool parameters
            retry_count: Current retry attempt
            
        Returns:
            Tool result string or None if failed
        """
        
        try:
            logger.info(f"Calling tool '{tool_name}' with parameters: {parameters}")
            
            async with Client(mcp) as client:
                # Set timeout for the operation
                start_time = time.time()
                
                result = await asyncio.wait_for(
                    client.call_tool(tool_name, parameters),
                    timeout=self.timeout
                )
                
                duration = time.time() - start_time
                logger.info(f"Tool '{tool_name}' completed successfully in {duration:.2f}s")
                
                if result and len(result) > 0:
                    return result[0].text
                else:
                    logger.warning(f"Tool '{tool_name}' returned empty result")
                    return None
                    
        except asyncio.TimeoutError:
            error_msg = f"Tool '{tool_name}' timed out after {self.timeout}s"
            logger.error(error_msg)
            self.last_error = error_msg
            
            # Retry with exponential backoff for timeouts
            return await self._handle_retry(tool_name, parameters, retry_count, 
                                          "timeout", exponential_backoff=True)
            
        except ConnectionError as e:
            error_msg = f"Connection error calling '{tool_name}': {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            
            # Retry connection errors
            return await self._handle_retry(tool_name, parameters, retry_count, 
                                          "connection_error")
            
        except Exception as e:
            error_msg = f"Unexpected error calling '{tool_name}': {type(e).__name__}: {e}"
            logger.error(error_msg, exc_info=True)
            self.last_error = error_msg
            
            # Check if error is retryable
            if self._is_retryable_error(e):
                return await self._handle_retry(tool_name, parameters, retry_count, 
                                              "retryable_error")
            else:
                logger.error(f"Non-retryable error for '{tool_name}': {e}")
                return None
    
    async def _handle_retry(self, tool_name: str, parameters: Dict[str, Any], 
                          retry_count: int, error_type: str, 
                          exponential_backoff: bool = False) -> Optional[str]:
        """Handle retry logic with different backoff strategies."""
        
        if retry_count >= self.max_retries:
            logger.error(f"Maximum retries ({self.max_retries}) reached for '{tool_name}'")
            return None
        
        # Calculate delay (exponential backoff or linear)
        if exponential_backoff:
            delay = self.retry_delay * (2 ** retry_count)
        else:
            delay = self.retry_delay * (retry_count + 1)
        
        logger.info(f"Retrying '{tool_name}' in {delay:.1f}s (attempt {retry_count + 1}/{self.max_retries}, reason: {error_type})")
        await asyncio.sleep(delay)
        
        return await self.safe_call_tool(tool_name, parameters, retry_count + 1)
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is worth retrying."""
        
        retryable_errors = [
            "Connection reset by peer",
            "Temporary failure",
            "Service temporarily unavailable",
            "Internal server error",
            "Bad gateway",
            "Gateway timeout"
        ]
        
        error_str = str(error).lower()
        return any(retryable_error in error_str for retryable_error in retryable_errors)
    
    async def safe_search(self, query: str, max_results: int = 25) -> Optional[str]:
        """Safe search with input validation and error handling."""
        
        # Input validation
        if not query or not isinstance(query, str):
            logger.error("Invalid query: must be a non-empty string")
            return None
        
        if not isinstance(max_results, int) or max_results <= 0:
            logger.error("Invalid max_results: must be a positive integer")
            return None
        
        # Sanitize query
        query = query.strip()
        if len(query) > 1000:  # Reasonable limit
            logger.warning(f"Query truncated from {len(query)} to 1000 characters")
            query = query[:1000]
        
        return await self.safe_call_tool("search_content", {
            "query": query,
            "max_results": max_results
        })
    
    async def safe_upload(self, filename: str, content_base64: str, 
                         parent_id: str = "-root-", description: str = "") -> Optional[str]:
        """Safe upload with comprehensive validation."""
        
        # Validate filename
        if not filename or not isinstance(filename, str):
            logger.error("Invalid filename: must be a non-empty string")
            return None
        
        # Validate base64 content
        if not content_base64 or not isinstance(content_base64, str):
            logger.error("Invalid content: must be a non-empty base64 string")
            return None
        
        # Basic base64 validation
        try:
            import base64
            import re
            
            # Check base64 format
            if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', content_base64):
                logger.error("Invalid base64 format")
                return None
            
            # Test decode
            base64.b64decode(content_base64, validate=True)
            
        except Exception as e:
            logger.error(f"Base64 validation failed: {e}")
            return None
        
        # Check content size (base64 encoded)
        content_size = len(content_base64)
        max_size = 100 * 1024 * 1024  # 100MB in base64
        
        if content_size > max_size:
            logger.error(f"Content too large: {content_size} bytes (max: {max_size})")
            return None
        
        return await self.safe_call_tool("upload_document", {
            "filename": filename,
            "content_base64": content_base64,
            "parent_id": parent_id,
            "description": description
        })
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of the MCP server and Alfresco."""
        
        health_status = {
            "timestamp": time.time(),
            "overall_status": "unknown",
            "checks": {}
        }
        
        # Test 1: Tool availability
        try:
            async with Client(mcp) as client:
                tools = await asyncio.wait_for(client.list_tools(), timeout=10.0)
                health_status["checks"]["tools"] = {
                    "status": "healthy",
                    "count": len(tools),
                    "message": f"Found {len(tools)} tools"
                }
        except Exception as e:
            health_status["checks"]["tools"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "Failed to list tools"
            }
        
        # Test 2: Search functionality
        try:
            search_result = await self.safe_search("*", max_results=1)
            if search_result:
                health_status["checks"]["search"] = {
                    "status": "healthy",
                    "message": "Search working"
                }
            else:
                health_status["checks"]["search"] = {
                    "status": "degraded",
                    "message": "Search returned no results"
                }
        except Exception as e:
            health_status["checks"]["search"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "Search failed"
            }
        
        # Test 3: Repository access
        try:
            async with Client(mcp) as client:
                repo_info = await asyncio.wait_for(
                    client.read_resource("alfresco://repository/info"), 
                    timeout=10.0
                )
                health_status["checks"]["repository"] = {
                    "status": "healthy",
                    "message": "Repository accessible"
                }
        except Exception as e:
            health_status["checks"]["repository"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "Repository inaccessible"
            }
        
        # Determine overall status
        statuses = [check["status"] for check in health_status["checks"].values()]
        if all(status == "healthy" for status in statuses):
            health_status["overall_status"] = "healthy"
        elif any(status == "healthy" for status in statuses):
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "unhealthy"
        
        return health_status


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""
        
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker moving to half-open state")
            else:
                raise Exception("Circuit breaker is open - preventing call")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker closed - service recovered")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e


async def demonstrate_error_handling():
    """Demonstrate error handling scenarios."""
    
    print("🛡️  Alfresco MCP Server - Error Handling Demo")
    print("=" * 60)
    
    # Test connection errors
    print("\n1️⃣ Connection Error Handling")
    print("-" * 30)
    
    try:
        async with Client(mcp) as client:
            result = await client.call_tool("search_content", {
                "query": "test",
                "max_results": 5
            })
            print("✅ Connection successful")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Check if Alfresco server is running")
    
    # Test invalid parameters
    print("\n2️⃣ Parameter Validation")
    print("-" * 30)
    
    try:
        async with Client(mcp) as client:
            # Invalid max_results
            result = await client.call_tool("search_content", {
                "query": "test",
                "max_results": -1
            })
            print("⚠️  Invalid parameter unexpectedly succeeded")
            
    except Exception as e:
        print("✅ Invalid parameter properly rejected")
    
    print("\n✅ Error Handling Demo Complete!")


async def main():
    """Main function."""
    try:
        await demonstrate_error_handling()
    except Exception as e:
        print(f"💥 Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 
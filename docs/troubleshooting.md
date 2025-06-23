# Troubleshooting Guide

Comprehensive troubleshooting guide for the Alfresco MCP Server. This document covers common issues, diagnostic steps, and solutions to help you resolve problems quickly.

## 🚨 Quick Diagnosis

### Health Check Commands

Run these commands to quickly assess your system:

```bash
# 1. Check Alfresco connectivity
curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-

# 2. Test MCP server startup
python -m alfresco_mcp_server.fastmcp_server --help

# 3. Verify environment
python -c "import os; print('URL:', os.getenv('ALFRESCO_URL')); print('User:', os.getenv('ALFRESCO_USERNAME'))"

# 4. Run quick test
python examples/quick_start.py
```

### Common Error Patterns

| Error Pattern | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `Connection refused` | Alfresco not running | Start Alfresco server |
| `Authentication failed` | Wrong credentials | Check username/password |
| `Module not found` | Installation issue | Run `pip install -e .` |
| `Timeout` | Network/performance issue | Check connectivity, increase timeout |
| `Invalid base64` | Malformed content | Validate base64 encoding |

## 🔌 Connection Issues

### Problem: Cannot Connect to Alfresco

**Symptoms:**
```
ConnectionError: Failed to connect to Alfresco server
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Diagnosis:**
```bash
# Test Alfresco availability
curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-

# Check if service is listening
netstat -tulpn | grep 8080

# Test from different machine
telnet alfresco-server 8080
```

**Solutions:**

1. **Start Alfresco Server:**
   ```bash
   # Docker deployment
   docker-compose up -d alfresco

   # Manual startup
   ./alfresco.sh start
   ```

2. **Check URL Configuration:**
   ```bash
   # Verify correct URL
   export ALFRESCO_URL="http://localhost:8080"
   
   # For HTTPS
   export ALFRESCO_URL="https://alfresco.company.com"
   
   # For custom port
   export ALFRESCO_URL="http://localhost:8180"
   ```

3. **Network Connectivity:**
   ```bash
   # Check firewall
   sudo ufw status
   
   # Test port accessibility
   nc -zv localhost 8080
   ```

### Problem: SSL/TLS Certificate Issues

**Symptoms:**
```
SSLError: HTTPSConnectionPool(host='alfresco.company.com', port=443): Max retries exceeded
ssl.SSLCertVerificationError: certificate verify failed
```

**Solutions:**

1. **Disable SSL Verification (Development Only):**
   ```python
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   
   # In config
   alfresco:
     url: "https://alfresco.company.com"
     verify_ssl: false
   ```

2. **Add Custom Certificate:**
   ```bash
   # Add certificate to system trust store
   sudo cp company-ca.crt /usr/local/share/ca-certificates/
   sudo update-ca-certificates
   ```

## 🔐 Authentication Issues

### Problem: Authentication Failed

**Symptoms:**
```
AuthenticationError: Authentication failed
401 Unauthorized: Invalid username or password
```

**Diagnosis:**
```bash
# Test credentials manually
curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-

# Check environment variables
echo "Username: $ALFRESCO_USERNAME"
echo "Password: $ALFRESCO_PASSWORD"  # Be careful with this in scripts
```

**Solutions:**

1. **Verify Credentials:**
   ```bash
   # Check correct username/password
   export ALFRESCO_USERNAME="admin"
   export ALFRESCO_PASSWORD="admin"
   
   # For domain users
   export ALFRESCO_USERNAME="DOMAIN\\username"
   ```

2. **Use Token Authentication:**
   ```bash
   # Get token first
   TOKEN=$(curl -d "username=admin&password=admin" -X POST http://localhost:8080/alfresco/api/-default-/public/authentication/versions/1/tickets | jq -r .entry.id)
   
   export ALFRESCO_TOKEN="$TOKEN"
   ```

3. **Check User Permissions:**
   ```bash
   # Test with different user
   curl -u testuser:testpass http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-
   ```

## 📦 Installation Issues

### Problem: Module Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'alfresco_mcp_server'
ImportError: cannot import name 'mcp' from 'alfresco_mcp_server.fastmcp_server'
```

**Solutions:**

1. **Reinstall Package:**
   ```bash
   # Uninstall and reinstall
   pip uninstall alfresco-mcp-server
   pip install -e .
   
   # Force reinstall
   pip install -e . --force-reinstall
   ```

2. **Check Python Environment:**
   ```bash
   # Verify Python version
   python --version  # Should be 3.8+
   
   # Check virtual environment
   which python
   echo $VIRTUAL_ENV
   
   # Verify installation
   pip list | grep alfresco
   ```

3. **Path Issues:**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   
   # Verify package location
   python -c "import alfresco_mcp_server; print(alfresco_mcp_server.__file__)"
   ```

### Problem: Dependency Conflicts

**Symptoms:**
```
pip._internal.exceptions.ResolutionImpossible: ResolutionImpossible
ERROR: Could not find a version that satisfies the requirement
```

**Solutions:**

1. **Clean Environment:**
   ```bash
   # Create fresh virtual environment
   python -m venv venv_clean
   source venv_clean/bin/activate
   pip install -e .
   ```

2. **Update Dependencies:**
   ```bash
   # Update pip
   pip install --upgrade pip
   
   # Update dependencies
   pip install --upgrade -e .
   ```

## ⚡ Performance Issues

### Problem: Slow Operations

**Symptoms:**
- Search operations taking >30 seconds
- Upload timeouts
- General sluggishness

**Diagnosis:**
```bash
# Test search performance
time python -c "
import asyncio
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp

async def test():
    async with Client(mcp) as client:
        await client.call_tool('search_content', {'query': '*', 'max_results': 5})

asyncio.run(test())
"

# Check Alfresco performance
curl -w "%{time_total}\n" -o /dev/null -s -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-
```

**Solutions:**

1. **Optimize Search Queries:**
   ```python
   # Avoid wildcard searches
   await client.call_tool("search_content", {
       "query": "specific terms",  # Better than "*"
       "max_results": 25  # Reasonable limit
   })
   ```

2. **Increase Timeouts:**
   ```python
   # In your client code
   import httpx
   
   async with httpx.AsyncClient(timeout=60.0) as client:
       # Your operations
   ```

3. **Check Alfresco Performance:**
   ```bash
   # Monitor Alfresco logs
   tail -f alfresco.log | grep WARN
   
   # Check system resources
   top -p $(pgrep java)
   ```

### Problem: Memory Issues

**Symptoms:**
```
MemoryError: Unable to allocate memory
OutOfMemoryError: Java heap space (in Alfresco logs)
```

**Solutions:**

1. **Limit Batch Sizes:**
   ```python
   # Process in smaller batches
   async def process_batch(items, batch_size=10):
       for i in range(0, len(items), batch_size):
           batch = items[i:i + batch_size]
           # Process batch
   ```

2. **Increase Java Heap (Alfresco):**
   ```bash
   # In setenv.sh or docker-compose.yml
   export JAVA_OPTS="$JAVA_OPTS -Xmx4g -Xms2g"
   ```

## 🔧 Tool-Specific Issues

### Search Tool Problems

**Problem: No Search Results**

**Diagnosis:**
```python
# Test with simple query
result = await client.call_tool("search_content", {
    "query": "*",
    "max_results": 5
})
print(result[0].text)

# Check if repository has content
result = await client.call_tool("get_node_properties", {
    "node_id": "-root-"
})
```

**Solutions:**

1. **Verify Index Status:**
   ```bash
   # Check Solr status
   curl http://localhost:8983/solr/admin/cores?action=STATUS
   ```

2. **Reindex Content:**
   ```bash
   # Trigger reindex (Alfresco admin)
   curl -u admin:admin -X POST http://localhost:8080/alfresco/s/admin/admin-tenants
   ```

### Upload Tool Problems

**Problem: Upload Fails**

**Symptoms:**
```
❌ Error: Failed to upload document
413 Request Entity Too Large
```

**Solutions:**

1. **Check File Size Limits:**
   ```python
   # Verify base64 size
   import base64
   content = "your content"
   encoded = base64.b64encode(content.encode()).decode()
   print(f"Encoded size: {len(encoded)} bytes")
   ```

2. **Increase Upload Limits:**
   ```bash
   # In nginx (if used)
   client_max_body_size 100M;
   
   # In Tomcat server.xml
   <Connector maxPostSize="104857600" />
   ```

### Version Control Issues

**Problem: Checkout/Checkin Fails**

**Symptoms:**
```
❌ Error: Document is already checked out
❌ Error: Node does not support versioning
```

**Solutions:**

1. **Check Document Status:**
   ```python
   # Check if document is versionable
   props = await client.call_tool("get_node_properties", {
       "node_id": "your-doc-id"
   })
   ```

2. **Enable Versioning:**
   ```bash
   # Through Alfresco Share or API
   curl -u admin:admin -X POST \
     "http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/your-doc-id/aspects" \
     -d '{"aspectName": "cm:versionable"}'
   ```

## 🧪 Testing Issues

### Problem: Tests Failing

**Common Test Failures:**

1. **Integration Test Failures:**
   ```bash
   # Check Alfresco is running for tests
   curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-
   
   # Run with verbose output
   pytest tests/test_integration.py -v
   ```

2. **Coverage Test Failures:**
   ```bash
   # Run coverage tests specifically
   pytest tests/test_coverage.py --tb=short
   
   # Check what's missing
   pytest --cov-report=term-missing
   ```

3. **Import Errors in Tests:**
   ```bash
   # Reinstall in development mode
   pip install -e .
   
   # Check test environment
   python -m pytest --collect-only
   ```

## 🌐 Transport Issues

### Problem: HTTP Transport Not Working

**Symptoms:**
```
ConnectionError: Failed to connect to HTTP transport
Server not responding on port 8001
```

**Solutions:**

1. **Check Server Status:**
   ```bash
   # Verify server is running
   python -m alfresco_mcp_server.fastmcp_server --transport http --port 8001 &
   
   # Test endpoint
   curl http://localhost:8001/health
   ```

2. **Port Conflicts:**
   ```bash
   # Check if port is in use
   netstat -tulpn | grep 8001
   
   # Use different port
   python -m alfresco_mcp_server.fastmcp_server --transport http --port 8002
   ```

### Problem: SSE Transport Issues

**Symptoms:**
```
EventSource connection failed
SSE stream disconnected
```

**Solutions:**

1. **Check Browser Support:**
   ```javascript
   // Test in browser console
   const eventSource = new EventSource('http://localhost:8003/events');
   eventSource.onopen = () => console.log('Connected');
   eventSource.onerror = (e) => console.error('Error:', e);
   ```

2. **Firewall/Proxy Issues:**
   ```bash
   # Test direct connection
   curl -N -H "Accept: text/event-stream" http://localhost:8003/events
   ```

## 🔍 Debugging Techniques

### Enable Debug Logging

```bash
# Set debug environment
export ALFRESCO_DEBUG="true"
export ALFRESCO_LOG_LEVEL="DEBUG"

# Run with verbose logging
python -m alfresco_mcp_server.fastmcp_server --log-level DEBUG
```

### Network Debugging

```bash
# Monitor network traffic
sudo tcpdump -i any -A 'host localhost and port 8080'

# Test with different tools
wget --spider http://localhost:8080/alfresco/
httpie GET localhost:8080/alfresco/ username==admin password==admin
```

### Python Debugging

```python
# Add debug prints
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for interactive debugging
import pdb; pdb.set_trace()

# Add timing information
import time
start = time.time()
# Your operation
print(f"Operation took {time.time() - start:.2f}s")
```

## 📊 Monitoring and Diagnostics

### Health Monitoring Script

```python
#!/usr/bin/env python3
"""Health check script for Alfresco MCP Server."""

import asyncio
import sys
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp

async def health_check():
    """Perform comprehensive health check."""
    
    checks = []
    
    try:
        async with Client(mcp) as client:
            # Test 1: List tools
            tools = await client.list_tools()
            checks.append(f"✅ Tools available: {len(tools)}")
            
            # Test 2: Search operation
            result = await client.call_tool("search_content", {
                "query": "*", "max_results": 1
            })
            checks.append("✅ Search working")
            
            # Test 3: Repository info
            info = await client.read_resource("alfresco://repository/info")
            checks.append("✅ Repository accessible")
            
    except Exception as e:
        checks.append(f"❌ Health check failed: {e}")
        return False
    
    for check in checks:
        print(check)
    
    return all("✅" in check for check in checks)

if __name__ == "__main__":
    success = asyncio.run(health_check())
    sys.exit(0 if success else 1)
```

### Log Analysis

```bash
# Monitor MCP server logs
tail -f /var/log/alfresco-mcp-server.log

# Search for errors
grep -i error /var/log/alfresco-mcp-server.log | tail -10

# Monitor Alfresco logs
tail -f /opt/alfresco/tomcat/logs/catalina.out | grep -i mcp
```

## 🆘 Getting Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Review the [FAQ](faq.md)
3. ✅ Run the health check script above
4. ✅ Collect relevant log files
5. ✅ Document your environment details

### Information to Include

When reporting issues, include:

```bash
# System information
python --version
pip list | grep -E "(alfresco|fastmcp|mcp)"
uname -a

# Environment variables (redact passwords)
env | grep ALFRESCO | sed 's/PASSWORD=.*/PASSWORD=***/'

# Error messages (full stack trace)
python -m alfresco_mcp_server.fastmcp_server 2>&1 | head -50

# Test results
python scripts/run_tests.py unit
```

### Where to Get Help

- 📖 **Documentation**: Check [docs/](.)
- 💬 **GitHub Issues**: Report bugs and feature requests
- 🔍 **Stack Overflow**: Tag with `alfresco` and `mcp`
- 💡 **Community**: Alfresco and MCP community forums

---

**🎯 Remember**: Most issues have simple solutions. Work through this guide systematically, and you'll likely find the answer quickly! 
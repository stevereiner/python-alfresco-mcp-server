# Configuration Guide

Complete guide for configuring the Alfresco MCP Server. This document covers all configuration options, environment setup, and deployment scenarios.

## 📋 Configuration Overview

The Alfresco MCP Server supports multiple configuration methods:

1. **Environment Variables** (Primary - Always takes precedence)
2. **Default Values** (Fallback when no environment variable is set)
3. **Command Line Arguments** (Transport and server options only)

### ⚠️ Configuration Precedence Order

**Higher priority settings override lower priority settings:**

1. 🥇 **Environment Variables** (Highest Priority)
2. 🥈 **Default Values** (Fallback)

**Answer to "Which setting wins?"**
- ✅ **Environment Variables ALWAYS WIN** over any other setting
- ✅ If no environment variable is set, default values are used  
- ✅ YAML configuration files are **not currently implemented** (future enhancement)

### 🔄 Practical Example

```bash
# If you set an environment variable:
export ALFRESCO_URL="https://prod.company.com"
export ALFRESCO_USERNAME="service-account"

# And later try to override in code or config:
# config.yaml (not implemented yet, but for illustration):
# alfresco:
#   url: "http://localhost:8080"  
#   username: "admin"

# Result: Environment variables WIN!
# ✅ ALFRESCO_URL = "https://prod.company.com"  (from env var)
# ✅ ALFRESCO_USERNAME = "service-account"      (from env var)  
# ✅ ALFRESCO_PASSWORD = "admin"                (default value - no env var set)
```

**Key Takeaway:** Environment variables are the "final word" in v1.1 configuration.

## 🌍 Environment Variables

### Required Configuration

```bash
# Alfresco Server Connection (Required)
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
```

### Optional Configuration

```bash
# Authentication (Alternative to username/password)
export ALFRESCO_TOKEN="your-auth-token"

# Connection Settings
export ALFRESCO_TIMEOUT="30"              # Request timeout in seconds
export ALFRESCO_MAX_RETRIES="3"           # Maximum retry attempts
export ALFRESCO_RETRY_DELAY="1.0"         # Delay between retries

# SSL/TLS Settings
export ALFRESCO_VERIFY_SSL="true"         # Verify SSL certificates
export ALFRESCO_CA_BUNDLE="/path/to/ca"   # Custom CA bundle

# Debug and Logging
export ALFRESCO_DEBUG="false"             # Enable debug mode
export ALFRESCO_LOG_LEVEL="INFO"          # Logging level

# Performance Settings
export ALFRESCO_POOL_SIZE="10"            # Connection pool size
export ALFRESCO_MAX_CONCURRENT="5"        # Max concurrent requests
```

### Development vs Production

**Development Environment:**
```bash
# Development settings
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
export ALFRESCO_DEBUG="true"
export ALFRESCO_LOG_LEVEL="DEBUG"
export ALFRESCO_VERIFY_SSL="false"
```

**Production Environment:**
```bash
# Production settings
export ALFRESCO_URL="https://alfresco.company.com"
export ALFRESCO_USERNAME="service_account"
export ALFRESCO_PASSWORD="secure_password"
export ALFRESCO_DEBUG="false"
export ALFRESCO_LOG_LEVEL="INFO"
export ALFRESCO_VERIFY_SSL="true"
export ALFRESCO_TIMEOUT="60"
export ALFRESCO_MAX_RETRIES="5"
```

## 📄 Configuration Files (Future Enhancement)

> ⚠️ **Note**: YAML configuration files are not currently implemented in v1.1. All configuration must be done via environment variables. YAML support is planned for a future release.

### Planned YAML Configuration

Future versions will support `config.yaml` in your project root:

```yaml
# config.yaml
alfresco:
  # Connection settings
  url: "http://localhost:8080"
  username: "admin"
  password: "admin"
  
  # Optional token authentication
  # token: "your-auth-token"
  
  # Connection options
  timeout: 30
  max_retries: 3
  retry_delay: 1.0
  verify_ssl: true
  
  # Performance settings
  pool_size: 10
  max_concurrent: 5

# Server settings
server:
  host: "127.0.0.1"
  port: 8000
  transport: "stdio"  # stdio, http, sse
  
# Logging configuration
logging:
  level: "INFO"       # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "alfresco_mcp.log"
  
# Feature flags
features:
  enable_caching: true
  enable_metrics: false
  enable_tracing: false
```

### Planned Environment-Specific Configs

**Future: config.development.yaml:**
```yaml
alfresco:
  url: "http://localhost:8080"
  username: "admin"
  password: "admin"
  verify_ssl: false
  
logging:
  level: "DEBUG"
  
features:
  enable_caching: false
  enable_metrics: true
```

**config.production.yaml:**
```yaml
alfresco:
  url: "${ALFRESCO_URL}"
  username: "${ALFRESCO_USERNAME}"
  password: "${ALFRESCO_PASSWORD}"
  timeout: 60
  max_retries: 5
  verify_ssl: true
  
logging:
  level: "INFO"
  file: "/var/log/alfresco-mcp-server.log"
  
features:
  enable_caching: true
  enable_metrics: true
  enable_tracing: true
```

### Current Configuration Loading

```python
# Current v1.1 implementation - Environment variables only
from alfresco_mcp_server.config import load_config

# Load configuration (reads environment variables + defaults)
config = load_config()

# Configuration is automatically loaded from environment variables:
# ALFRESCO_URL, ALFRESCO_USERNAME, ALFRESCO_PASSWORD, etc.
```

### Planned Future Configuration Loading

```python
# Future enhancement - YAML + environment variables
from alfresco_mcp_server.config import load_config

# Load environment-specific config (planned)
config = load_config("config.production.yaml")

# Load with environment variable override (planned)
config = load_config(env_override=True)
```

## 🖥️ Command Line Arguments

### FastMCP Server Options

```bash
# Basic usage
python -m alfresco_mcp_server.fastmcp_server

# With custom transport
python -m alfresco_mcp_server.fastmcp_server --transport http --port 8001

# With logging
python -m alfresco_mcp_server.fastmcp_server --log-level DEBUG

# Full options
python -m alfresco_mcp_server.fastmcp_server \
  --transport sse \
  --host 0.0.0.0 \
  --port 8002 \
  --log-level INFO \
  --config config.production.yaml
```

### Available Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--transport` | choice | `stdio` | Transport protocol (stdio, http, sse) |
| `--host` | string | `127.0.0.1` | Server host address |
| `--port` | integer | `8000` | Server port number |
| `--log-level` | choice | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `--config` | path | `config.yaml` | Configuration file path |
| `--help` | flag | - | Show help message |





## 🔧 Development Configuration

### Development Setup

**Option A: UV (Recommended - Automatic dependency management):**

```bash
# Clone the repository
git clone https://github.com/stevereiner/python-alfresco-mcp-server.git
cd python-alfresco-mcp-server

# UV handles everything automatically - no manual venv needed!
uv sync --extra dev          # Install with development dependencies
uv run python-alfresco-mcp-server --help  # Test installation

# Set development environment variables
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
export ALFRESCO_DEBUG="true"
export ALFRESCO_LOG_LEVEL="DEBUG"
export ALFRESCO_VERIFY_SSL="false"

# Run with UV (recommended)
uv run python-alfresco-mcp-server --transport stdio
```

**Option B: Traditional Python (Manual venv management):**

```bash
# Clone the repository
git clone https://github.com/stevereiner/python-alfresco-mcp-server.git
cd python-alfresco-mcp-server

# Create development environment
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

# Install in development mode
pip install -e .[dev]

# Set development environment
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
export ALFRESCO_DEBUG="true"
export ALFRESCO_LOG_LEVEL="DEBUG"
export ALFRESCO_VERIFY_SSL="false"

# Run traditionally
python-alfresco-mcp-server --transport stdio
```

### Testing Configuration

```yaml
# config.test.yaml
alfresco:
  url: "http://localhost:8080"
  username: "admin"
  password: "admin"
  timeout: 10
  verify_ssl: false

logging:
  level: "DEBUG"
  
features:
  enable_caching: false
```

### Hot Reload Setup

```bash
# Install development dependencies
pip install watchdog

# Run with auto-reload
python -m alfresco_mcp_server.fastmcp_server --reload
```

## 🚀 Production Configuration

### Production Checklist

- ✅ Use strong passwords/tokens
- ✅ Enable SSL certificate verification
- ✅ Configure appropriate timeouts
- ✅ Set up log rotation
- ✅ Configure monitoring
- ✅ Use environment variables for secrets
- ✅ Set appropriate resource limits

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

# Configuration via environment
ENV ALFRESCO_URL=""
ENV ALFRESCO_USERNAME=""
ENV ALFRESCO_PASSWORD=""

EXPOSE 8000

CMD ["python", "-m", "alfresco_mcp_server.fastmcp_server", "--host", "0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  alfresco-mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ALFRESCO_URL=http://alfresco:8080
      - ALFRESCO_USERNAME=admin
      - ALFRESCO_PASSWORD=admin
    depends_on:
      - alfresco
    restart: unless-stopped
    
  alfresco:
    image: alfresco/alfresco-content-repository-community:latest
    ports:
      - "8080:8080"
    environment:
      - JAVA_OPTS=-Xmx2g
```

### Systemd Service

```ini
# /etc/systemd/system/alfresco-mcp-server.service
[Unit]
Description=Alfresco MCP Server
After=network.target

[Service]
Type=simple
User=alfresco-mcp
WorkingDirectory=/opt/alfresco-mcp-server
Environment=ALFRESCO_URL=https://alfresco.company.com
Environment=ALFRESCO_USERNAME=service_account
Environment=ALFRESCO_PASSWORD=secure_password
ExecStart=/opt/alfresco-mcp-server/venv/bin/python -m alfresco_mcp_server.fastmcp_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🔍 Configuration Validation

### Validation Script

```python
#!/usr/bin/env python3
"""Configuration validation script."""

import asyncio
import sys
from alfresco_mcp_server.config import load_config
from fastmcp import Client
from alfresco_mcp_server.fastmcp_server import mcp

async def validate_config():
    """Validate configuration and connectivity."""
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded successfully")
        
        # Test connectivity
        async with Client(mcp) as client:
            tools = await client.list_tools()
            print(f"✅ Connected to Alfresco, found {len(tools)} tools")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_config())
    sys.exit(0 if success else 1)
```

### Configuration Testing

```bash
# Test configuration
python validate_config.py

# Test with specific config file
python validate_config.py --config config.production.yaml

# Test connectivity
curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-
```

--- 
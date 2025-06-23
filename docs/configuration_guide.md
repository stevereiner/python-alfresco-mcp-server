# Configuration Guide

Complete guide for configuring the Alfresco MCP Server. This document covers all configuration options, environment setup, and deployment scenarios.

## 📋 Configuration Overview

The Alfresco MCP Server supports multiple configuration methods:

1. **Environment Variables** (Recommended)
2. **Configuration Files** (YAML)
3. **Command Line Arguments**
4. **Runtime Configuration**

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

## 📄 Configuration Files

### YAML Configuration

Create `config.yaml` in your project root:

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

### Environment-Specific Configs

**config.development.yaml:**
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

### Loading Configuration

```python
# Load configuration in your application
from alfresco_mcp_server.config import load_config

# Load default config
config = load_config()

# Load environment-specific config
config = load_config("config.production.yaml")

# Load with environment variable override
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



## 🔐 Authentication Configuration

### Username/Password Authentication

```bash
# Basic authentication
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"

# Domain authentication
export ALFRESCO_USERNAME="DOMAIN\\username"
export ALFRESCO_PASSWORD="password"
```

### Token Authentication

```bash
# Get authentication token
TOKEN=$(curl -d "username=admin&password=admin" \
  -X POST http://localhost:8080/alfresco/api/-default-/public/authentication/versions/1/tickets \
  | jq -r .entry.id)

# Use token
export ALFRESCO_TOKEN="$TOKEN"
```

### Service Account Setup

1. **Create Service Account in Alfresco:**
   ```bash
   # Create user via Alfresco admin console
   # Or via API
   curl -u admin:admin -X POST \
     "http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/people" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "mcp-service",
       "firstName": "MCP",
       "lastName": "Service",
       "password": "secure-password",
       "email": "mcp-service@company.com"
     }'
   ```

2. **Assign Permissions:**
   ```bash
   # Grant necessary permissions in Alfresco Share
   # Or via API calls
   ```

3. **Configure Service Account:**
   ```bash
   export ALFRESCO_USERNAME="mcp-service"
   export ALFRESCO_PASSWORD="secure-password"
   ```

## 🌐 Network Configuration

### Firewall Settings

**Required Ports:**
- **Alfresco**: 8080 (HTTP) or 443 (HTTPS)
- **MCP Server**: 8000-8003 (HTTP/SSE transports)

**Firewall Rules:**
```bash
# Allow outbound to Alfresco
sudo ufw allow out 8080
sudo ufw allow out 443

# Allow inbound for MCP server (if using HTTP/SSE)
sudo ufw allow 8000:8003/tcp
```

### Proxy Configuration

**Behind Corporate Proxy:**
```bash
# Set proxy environment variables
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Configure in Python
import os
import httpx

proxies = {
    "http://": os.getenv("HTTP_PROXY"),
    "https://": os.getenv("HTTPS_PROXY")
}
```

**Nginx Reverse Proxy:**
```nginx
# /etc/nginx/sites-available/alfresco-mcp
server {
    listen 80;
    server_name mcp.company.com;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### SSL/TLS Configuration

**Custom Certificate:**
```bash
# Add certificate to system trust store
sudo cp company-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Or specify in configuration
export ALFRESCO_CA_BUNDLE="/path/to/company-ca.crt"
```

**Disable SSL Verification (Development):**
```yaml
alfresco:
  url: "https://alfresco-dev.company.com"
  verify_ssl: false
```

## 📊 Performance Configuration

### Connection Pooling

```yaml
alfresco:
  # Connection pool settings
  pool_size: 20           # Maximum connections in pool
  pool_timeout: 30        # Timeout for getting connection
  pool_recycle: 3600      # Recycle connections after 1 hour
  
  # Request settings
  timeout: 60             # Request timeout
  max_retries: 5          # Maximum retry attempts
  retry_delay: 2.0        # Delay between retries
```

### Concurrency Limits

```yaml
server:
  # Maximum concurrent requests
  max_concurrent: 10
  
  # Request queue size
  queue_size: 100
  
  # Worker processes (for production)
  workers: 4
```

### Caching Configuration

```yaml
cache:
  # Enable response caching
  enabled: true
  
  # Cache backend
  backend: "memory"       # memory, redis, file
  
  # Cache settings
  default_ttl: 300        # 5 minutes
  max_size: 1000          # Maximum cached items
  
  # Redis settings (if using Redis backend)
  redis:
    host: "localhost"
    port: 6379
    db: 0
```

## 📝 Logging Configuration

### Basic Logging

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # File logging
  file: "/var/log/alfresco-mcp-server.log"
  max_size: "10MB"
  backup_count: 5
  
  # Console logging
  console: true
```

### Advanced Logging

```yaml
logging:
  version: 1
  disable_existing_loggers: false
  
  formatters:
    standard:
      format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    detailed:
      format: "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
  
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: standard
      stream: ext://sys.stdout
    
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: detailed
      filename: /var/log/alfresco-mcp-server.log
      maxBytes: 10485760  # 10MB
      backupCount: 5
  
  loggers:
    alfresco_mcp_server:
      level: DEBUG
      handlers: [console, file]
      propagate: false
      
  root:
    level: INFO
    handlers: [console]
```

### Structured Logging

```yaml
logging:
  # JSON logging for log aggregation
  format: "json"
  
  # Additional fields
  extra_fields:
    service: "alfresco-mcp-server"
    version: "1.0.0"
    environment: "production"
```

## 🔧 Development Configuration

### Development Setup

```bash
# Create development environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .[dev]

# Set development environment
export ALFRESCO_ENV="development"
export ALFRESCO_DEBUG="true"
export ALFRESCO_LOG_LEVEL="DEBUG"
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

**🎯 Remember**: Configuration is critical for production deployments. Always validate your configuration before going live! 
# How to Start MCP Inspector

## 🚀 Quick Start Methods

### Method 1: Using Config File (Recommended - Avoids Proxy Errors)
```bash
# 1. Start your MCP server first
python -m alfresco_mcp_server.fastmcp_server --transport http --port 8003

# 2. Start MCP Inspector with pre-configured server
npx @modelcontextprotocol/inspector --config mcp-inspector-http-config.json --server python-alfresco-mcp-server
```

**Expected Output:**
```
Starting MCP inspector...
⚙️ Proxy server listening on 127.0.0.1:6277
🔑 Session token: d7a62ab6e032eefe5d85e807c50e13b9fffcd12badbf8bbc3377659c0be4fa8d
Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=d7a62ab6e032eefe5d85e807c50e13b9fffcd12badbf8bbc3377659c0be4fa8d
```

### Method 2: Using npx (Basic)
```bash
npx @modelcontextprotocol/inspector
```

### Method 2: Using npm (if globally installed)
```bash
npm run dev
# or
npm start
```

### Method 3: Direct GitHub (if you have it locally)
```bash
# If you have the repo cloned
cd path/to/mcp-inspector
npm run dev
```

### Method 4: Using the pre-built package
```bash
npx @modelcontextprotocol/inspector@latest
```

## 📍 Expected Output
When MCP Inspector starts, you should see:
```
> Local:   http://localhost:6274
> Network: http://192.168.x.x:6274
```

## 🔗 After Starting

### 1. Open Browser
Navigate to: `http://localhost:6274`

### 2. Connect to Your Server
- **Click "Add Server"** or server connection field
- **Enter**: `http://localhost:8003`
- **Transport**: HTTP
- **Connect**

### 3. Expected URL
```
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<new-token>&server=http://localhost:8003#tools
```

## 🛠️ Troubleshooting

### If Port 6274 is Busy
```bash
# MCP Inspector will auto-find next available port
# Check what port it actually uses in the startup message
```

### If npx Fails
```bash
# Update npm/npx
npm install -g npm@latest

# Try with explicit version
npx @modelcontextprotocol/inspector@latest
```

### Check if Already Running
```bash
netstat -an | findstr :6274
# or check other common ports
netstat -an | findstr ":3000\|:5173\|:6274"
```

## 🎯 Quick Test Command
```bash
# This should start MCP Inspector on port 6274
npx @modelcontextprotocol/inspector
```

Then open `http://localhost:6274` and connect to your server at `http://localhost:8003`! 
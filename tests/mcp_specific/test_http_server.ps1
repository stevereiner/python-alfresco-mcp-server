# Test script for Python Alfresco MCP Server HTTP transport
Write-Host "🌐 Testing Python Alfresco MCP Server - HTTP Transport" -ForegroundColor Green
Write-Host "=" * 60

$baseUrl = "http://127.0.0.1:8001"

# Wait for server to start
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    # Test 1: Server health/info
    Write-Host "`n🏥 Testing Server Health..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -TimeoutSec 10
        Write-Host "✅ Server is responding" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
    }
    catch {
        Write-Host "ℹ️  Root endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # Test 2: List tools (if available)
    Write-Host "`n🔧 Testing Tools Endpoint..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/tools" -Method GET -TimeoutSec 10
        Write-Host "✅ Tools endpoint accessible" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "   Tools found: $($content.tools.Count)" -ForegroundColor Gray
    }
    catch {
        Write-Host "ℹ️  Tools endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # Test 3: List resources (if available)
    Write-Host "`n📦 Testing Resources Endpoint..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/resources" -Method GET -TimeoutSec 10
        Write-Host "✅ Resources endpoint accessible" -ForegroundColor Green
    }
    catch {
        Write-Host "ℹ️  Resources endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # Test 4: Call a tool (if supported)
    Write-Host "`n🔍 Testing Tool Call..." -ForegroundColor Cyan
    try {
        $body = @{
            query = "test"
            max_results = 5
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "$baseUrl/tools/search_content" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        Write-Host "✅ Tool call successful" -ForegroundColor Green
        Write-Host "   Response length: $($response.Content.Length) chars" -ForegroundColor Gray
    }
    catch {
        Write-Host "ℹ️  Tool call: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host "`n🎉 HTTP testing completed!" -ForegroundColor Green

}
catch {
    Write-Host "❌ HTTP testing failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📖 Next steps:" -ForegroundColor Cyan
Write-Host "1. Try MCP Inspector: npx @modelcontextprotocol/inspector" -ForegroundColor Gray
Write-Host "2. Test STDIO transport: python test_with_mcp_client.py" -ForegroundColor Gray
Write-Host "3. Run existing test suite: python -m pytest tests/" -ForegroundColor Gray 
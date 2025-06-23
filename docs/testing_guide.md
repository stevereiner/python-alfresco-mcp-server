# Testing Guide

Comprehensive guide for running, maintaining, and extending the Alfresco MCP Server test suite. This document covers unit tests, integration tests, coverage analysis, and best practices.

## 📋 Test Suite Overview

The test suite includes:
- ✅ **58 Total Tests** (23 unit + 18 integration + 17 coverage)
- ✅ **84% Code Coverage** on main implementation
- ✅ **Mocked Unit Tests** for fast feedback
- ✅ **Live Integration Tests** with real Alfresco
- ✅ **Edge Case Coverage** for production readiness

## 🚀 Quick Start

### Run All Tests
```bash
# Run complete test suite
python scripts/run_tests.py all

# Run with coverage report
python scripts/run_tests.py coverage
```

### Run Specific Test Types
```bash
# Unit tests only (fast)
python scripts/run_tests.py unit

# Integration tests (requires Alfresco)
python scripts/run_tests.py integration

# Performance benchmarks
python scripts/run_tests.py performance

# Code quality checks
python scripts/run_tests.py lint
```

## 🏗️ Test Structure

### Test Categories

| Test Type | Purpose | Count | Duration | Prerequisites |
|-----------|---------|-------|----------|---------------|
| **Unit** | Fast feedback, mocked dependencies | 23 | ~5s | None |
| **Integration** | Real Alfresco server testing | 18 | ~30s | Live Alfresco |
| **Coverage** | Edge cases and error paths | 17 | ~10s | None |

### Test Files

```
tests/
├── conftest.py              # Shared fixtures and configuration

├── test_integration.py      # Live Alfresco integration tests
└── test_coverage.py         # Edge cases and coverage tests
```

## 🔧 Environment Setup

### Prerequisites
```bash
# Install test dependencies
pip install -e .[test]

# Or install all dev dependencies
pip install -e .[all]
```

### Alfresco Configuration

For integration tests, configure your Alfresco connection:

```bash
# Environment variables (recommended)
export ALFRESCO_URL="http://localhost:8080"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"

# Or set in config.yaml
alfresco:
  url: "http://localhost:8080"
  username: "admin"
  password: "admin"
```

### Test Configuration

Pytest configuration is in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=alfresco_mcp_server
    --cov-report=html
    --cov-report=xml
    --cov-report=term
    --cov-branch
    --cov-fail-under=85
markers =
    unit: Unit tests with mocked dependencies
    integration: Integration tests requiring live Alfresco
    slow: Tests that take longer than usual
    performance: Performance and benchmark tests
```

## 🧪 Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run integration tests with live server
pytest tests/test_integration.py

# Run specific test function  
pytest tests/test_fastmcp.py::test_search_content_tool

# Run tests with specific markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Advanced Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run in parallel (faster)
pytest -n auto

# Show coverage in terminal
pytest --cov-report=term-missing

# Generate HTML coverage report
pytest --cov-report=html
```

### Using the Test Runner

The `scripts/run_tests.py` provides convenient test execution:

```bash
# Show help
python scripts/run_tests.py --help

# Run unit tests only
python scripts/run_tests.py unit

# Run with custom pytest args
python scripts/run_tests.py unit --verbose --stop-on-failure

# Run integration tests with timeout
python scripts/run_tests.py integration --timeout 60

# Skip Alfresco availability check
python scripts/run_tests.py integration --skip-alfresco-check
```

## 🔍 Test Details

### Unit Tests (23 tests)

Fast tests with mocked Alfresco dependencies:

```python
# Example unit test structure
async def test_search_content_tool():
    """Test search tool with mocked Alfresco client."""
    
    # Arrange: Set up mock
    mock_alfresco = Mock()
    mock_search_results = create_mock_search_results(3)
    mock_alfresco.search_content.return_value = mock_search_results
    
    # Act: Execute tool
    result = await search_tool.execute(mock_alfresco, {
        "query": "test query",
        "max_results": 10
    })
    
    # Assert: Verify behavior
    assert "Found 3 results" in result
    mock_alfresco.search_content.assert_called_once()
```

**Covers:**
- ✅ All 9 MCP tools with success scenarios
- ✅ Error handling and edge cases
- ✅ Parameter validation
- ✅ Response formatting
- ✅ Tool availability and schemas

### Integration Tests (18 tests)

Real Alfresco server integration:

```python
# Example integration test
async def test_live_search_integration(alfresco_client):
    """Test search against live Alfresco server."""
    
    # Execute search on live server
    async with Client(mcp) as client:
        result = await client.call_tool("search_content", {
            "query": "*",
            "max_results": 5
        })
    
    # Verify real response structure
    assert result is not None
    assert len(result) > 0
```

**Covers:**
- ✅ Live server connectivity
- ✅ Tool functionality with real data
- ✅ End-to-end workflows
- ✅ Resource access
- ✅ Prompt generation
- ✅ Performance benchmarks

### Coverage Tests (17 tests)

Edge cases and error paths:

```python
# Example coverage test
async def test_invalid_base64_handling():
    """Test handling of malformed base64 content."""
    
    # Test with clearly invalid base64
    invalid_content = "not-valid-base64!!!"
    
    result = await upload_tool.execute(mock_client, {
        "filename": "test.txt",
        "content_base64": invalid_content,
        "parent_id": "-root-"
    })
    
    assert "❌ Error: Invalid base64 content" in result
```

**Covers:**
- ✅ Invalid inputs and malformed data
- ✅ Connection failures and timeouts
- ✅ Authentication errors
- ✅ Edge case parameter values
- ✅ Error message formatting

## 📊 Coverage Analysis

### Viewing Coverage Reports

```bash
# Generate HTML report
pytest --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov-report=term-missing

# XML report for CI/CD
pytest --cov-report=xml
```

### Coverage Targets

| Module | Target | Current |
|--------|---------|---------|
| `fastmcp_server.py` | 85% | 84% |
| `config.py` | 90% | 96% |
| **Overall** | 80% | 82% |

### Improving Coverage

To improve test coverage:

1. **Identify uncovered lines:**
   ```bash
   pytest --cov-report=term-missing | grep "TOTAL"
   ```

2. **Add tests for missing paths:**
   - Error conditions
   - Edge cases
   - Exception handling

3. **Run coverage-specific tests:**
   ```bash
   pytest tests/test_coverage.py -v
   ```

## ⚡ Performance Testing

### Benchmark Tests

Performance tests validate response times:

```python
# Example performance test
async def test_search_performance():
    """Verify search performance under 10 seconds."""
    
    start_time = time.time()
    
    async with Client(mcp) as client:
        await client.call_tool("search_content", {
            "query": "*",
            "max_results": 10
        })
    
    duration = time.time() - start_time
    assert duration < 10.0, f"Search took {duration:.2f}s, expected <10s"
```

### Performance Targets

| Operation | Target | Typical |
|-----------|---------|---------|
| Search | <10s | 2-5s |
| Upload | <30s | 5-15s |
| Download | <15s | 3-8s |
| Properties | <5s | 1-3s |
| Concurrent (5x) | <15s | 8-12s |

### Running Performance Tests

```bash
# Run performance suite
python scripts/run_tests.py performance

# Run with timing details
pytest -m performance --duration=10
```

## 🔨 Test Development

### Adding New Tests

1. **Choose the right test type:**
   - Unit: Fast feedback, mocked dependencies
   - Integration: Real server interaction
   - Coverage: Edge cases and errors

2. **Follow naming conventions:**
   ```python
   # Unit tests
   async def test_tool_name_success():
   async def test_tool_name_error_case():
   
   # Integration tests  
   async def test_live_tool_integration():
   
   # Coverage tests
   async def test_edge_case_handling():
   ```

3. **Use appropriate fixtures:**
   ```python
   # Mock fixtures for unit tests
   def test_with_mock_client(mock_alfresco_client):
       pass
   
   # Real client for integration
   def test_with_real_client(alfresco_client):
       pass
   ```

### Test Patterns

**Arrange-Act-Assert Pattern:**
```python
async def test_example():
    # Arrange: Set up test data
    mock_client = create_mock_client()
    test_params = {"query": "test"}
    
    # Act: Execute the function
    result = await tool.execute(mock_client, test_params)
    
    # Assert: Verify the outcome
    assert "expected result" in result
    mock_client.method.assert_called_once()
```

**Error Testing Pattern:**
```python
async def test_error_handling():
    # Arrange: Set up error condition
    mock_client = Mock()
    mock_client.method.side_effect = ConnectionError("Network error")
    
    # Act & Assert: Verify error handling
    result = await tool.execute(mock_client, {})
    assert "❌ Error:" in result
    assert "Network error" in result
```

### Mocking Best Practices

```python
# Good: Mock at the right level
@patch('alfresco_mcp_server.fastmcp_server.ClientFactory')
async def test_with_proper_mock(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.search.return_value = test_data
    
    # Test uses mocked instance
    result = await search_tool.execute(mock_instance, params)

# Good: Use realistic test data
def create_mock_search_results(count=3):
    return [
        {
            "entry": {
                "id": f"test-id-{i}",
                "name": f"test-doc-{i}.txt",
                "nodeType": "cm:content",
                "properties": {
                    "cm:title": f"Test Document {i}",
                    "cm:created": "2024-01-15T10:30:00.000Z"
                }
            }
        }
        for i in range(count)
    ]
```

## 🚨 Troubleshooting Tests

### Common Issues

**Test Failures:**

1. **Connection Errors in Integration Tests:**
   ```bash
   # Check Alfresco is running
   curl -u admin:admin http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-
   
   # Verify environment variables
   echo $ALFRESCO_URL
   echo $ALFRESCO_USERNAME
   ```

2. **Import Errors:**
   ```bash
   # Reinstall in development mode
   pip install -e .
   
   # Check Python path
   python -c "import alfresco_mcp_server; print(alfresco_mcp_server.__file__)"
   ```

3. **Coverage Too Low:**
   ```bash
   # Run coverage tests specifically
   pytest tests/test_coverage.py
   
   # Check what's missing
   pytest --cov-report=term-missing
   ```

**Performance Issues:**

1. **Slow Tests:**
   ```bash
   # Profile test execution time
   pytest --duration=10
   
   # Run only fast tests
   pytest -m "not slow"
   ```

2. **Timeout Errors:**
   ```bash
   # Increase timeout for integration tests
   pytest --timeout=60 tests/test_integration.py
   ```

### Debugging Tests

```bash
# Run with pdb debugger
pytest --pdb tests/test_file.py::test_function

# Show full output (don't capture)
pytest -s tests/test_file.py

# Show local variables on failure
pytest --tb=long

# Run single test with maximum verbosity
pytest -vvv tests/test_file.py::test_function
```

## 🔄 Continuous Integration

### GitHub Actions Integration

Example CI configuration:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: |
          pip install -e .[test]
      
      - name: Run unit tests
        run: |
          python scripts/run_tests.py unit
      
      - name: Run coverage tests
        run: |
          python scripts/run_tests.py coverage
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v1
        with:
          file: ./coverage.xml
```

### Local Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 Test Metrics

### Success Criteria

- ✅ **All tests passing**: 58/58 (100%)
- ✅ **Coverage target**: >85% on main modules
- ✅ **Performance targets**: All benchmarks within limits
- ✅ **No linting errors**: Clean code quality

### Monitoring

```bash
# Daily test run
python scripts/run_tests.py all > test_results.log 2>&1

# Coverage tracking
pytest --cov-report=json
# Parse coverage.json for metrics

# Performance monitoring
python scripts/run_tests.py performance | grep "Duration:"
```

---

**🎯 Remember**: Good tests are your safety net for refactoring and new features. Keep them fast, reliable, and comprehensive! 
#!/usr/bin/env python3
"""
Comprehensive test runner for Alfresco MCP Server.
Provides different test modes: unit, integration, coverage, performance.
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}" if description else f"Running: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def install_dependencies():
    """Install test dependencies."""
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-xdist>=3.0.0",  # For parallel test execution
        "pytest-mock>=3.10.0",
        "coverage>=7.0.0",
        "httpx>=0.24.0",
    ]
    
    print("📦 Installing test dependencies...")
    for dep in dependencies:
        cmd = [sys.executable, "-m", "pip", "install", dep]
        if not run_command(cmd, f"Installing {dep}"):
            return False
    return True


def run_unit_tests():
    """Run unit tests with mocking."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_coverage.py",
        "tests/test_fastmcp_2_0.py",
        "tests/test_unit_tools.py",
        "-v",
        "--tb=short",
        "-m", "unit",
        "--cov=alfresco_mcp_server",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-branch"
    ]
    
    return run_command(cmd, "Running Unit Tests (Fast, Mocked)")


def run_integration_tests():
    """Run integration tests with live Alfresco."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_integration.py",
        "-v",
        "--tb=short",
        "-m", "integration",
        "--integration"
    ]
    
    return run_command(cmd, "Running Integration Tests (Requires Live Alfresco)")


def run_performance_tests():
    """Run performance benchmarks."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_integration.py",
        "-v",
        "--tb=short",
        "-m", "performance",
        "--integration",
        "--performance"
    ]
    
    return run_command(cmd, "Running Performance Tests")


def run_all_tests():
    """Run all tests with comprehensive coverage."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=alfresco_mcp_server",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-branch",
        "--cov-fail-under=85",
        "-x"  # Stop on first failure
    ]
    
    return run_command(cmd, "Running All Tests with Coverage")


def run_coverage_only():
    """Run coverage analysis only."""
    # First run tests to generate coverage data
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_coverage.py",
        "tests/test_fastmcp_2_0.py", 
        "tests/test_unit_tools.py",
        "--cov=alfresco_mcp_server",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--cov-branch",
        "-q"  # Quiet mode
    ]
    
    if not run_command(cmd, "Generating Coverage Data"):
        return False
    
    # Generate coverage report
    cmd = [sys.executable, "-m", "coverage", "report", "--show-missing"]
    return run_command(cmd, "Coverage Report")


def check_alfresco_availability():
    """Check if Alfresco server is available."""
    try:
        import httpx
        response = httpx.get("http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/probes/-ready-", timeout=5.0)
        if response.status_code == 200:
            print("✅ Alfresco server is available at localhost:8080")
            return True
    except Exception as e:
        print(f"⚠️ Alfresco server not available: {e}")
        print("Integration tests will be skipped")
    return False


def lint_code():
    """Run code linting."""
    print("🔍 Running code quality checks...")
    
    # Try to install and run linting tools
    linting_commands = [
        ([sys.executable, "-m", "pip", "install", "black", "ruff", "mypy"], "Installing linting tools"),
        ([sys.executable, "-m", "black", "--check", "alfresco_mcp_server/"], "Black formatting check"),
        ([sys.executable, "-m", "ruff", "check", "alfresco_mcp_server/"], "Ruff linting"),
    ]
    
    success = True
    for cmd, desc in linting_commands:
        if not run_command(cmd, desc):
            success = False
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Comprehensive test runner for Alfresco MCP Server")
    parser.add_argument("--mode", choices=["unit", "integration", "performance", "coverage", "all", "lint"], 
                       default="unit", help="Test mode to run")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--check-alfresco", action="store_true", help="Check Alfresco availability")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"🧪 Alfresco MCP Server Test Runner")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🎯 Test mode: {args.mode}")
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Check Alfresco availability if requested
    if args.check_alfresco:
        check_alfresco_availability()
    
    # Run tests based on mode
    success = True
    
    if args.mode == "unit":
        success = run_unit_tests()
    elif args.mode == "integration":
        if not check_alfresco_availability():
            print("❌ Alfresco server required for integration tests")
            sys.exit(1)
        success = run_integration_tests()
    elif args.mode == "performance":
        if not check_alfresco_availability():
            print("❌ Alfresco server required for performance tests")
            sys.exit(1)
        success = run_performance_tests()
    elif args.mode == "coverage":
        success = run_coverage_only()
    elif args.mode == "all":
        alfresco_available = check_alfresco_availability()
        success = run_all_tests()
        if success and alfresco_available:
            print("\n🔄 Running integration tests...")
            success = run_integration_tests()
    elif args.mode == "lint":
        success = lint_code()
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests completed successfully!")
        print("\n📊 Coverage report available at: htmlcov/index.html")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
    print('='*60)


if __name__ == "__main__":
    main() 
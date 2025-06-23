@echo off
REM Windows batch script for running Alfresco MCP Server tests

echo ================================
echo  Alfresco MCP Server Test Suite
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Set environment variables for Alfresco
set ALFRESCO_URL=http://localhost:8080
set ALFRESCO_USERNAME=admin
set ALFRESCO_PASSWORD=admin
set ALFRESCO_VERIFY_SSL=false

REM Parse command line arguments
set MODE=unit
set INSTALL_DEPS=false

:parse_args
if "%1"=="--help" goto :show_help
if "%1"=="--unit" set MODE=unit
if "%1"=="--integration" set MODE=integration
if "%1"=="--performance" set MODE=performance
if "%1"=="--coverage" set MODE=coverage
if "%1"=="--all" set MODE=all
if "%1"=="--lint" set MODE=lint
if "%1"=="--install-deps" set INSTALL_DEPS=true
shift
if not "%1"=="" goto :parse_args

REM Install dependencies if requested
if "%INSTALL_DEPS%"=="true" (
    echo Installing test dependencies...
    python -m pip install pytest pytest-asyncio pytest-cov pytest-mock coverage httpx
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        exit /b 1
    )
)

REM Run the test runner
echo Running tests in %MODE% mode...
python scripts/run_tests.py --mode %MODE%

if %errorlevel% neq 0 (
    echo Tests failed!
    exit /b 1
)

echo.
echo ================================
echo  Tests completed successfully!
echo ================================
echo Coverage report: htmlcov/index.html
exit /b 0

:show_help
echo Usage: test.bat [OPTIONS]
echo.
echo Options:
echo   --unit          Run unit tests (default)
echo   --integration   Run integration tests (requires Alfresco)
echo   --performance   Run performance tests
echo   --coverage      Run coverage analysis
echo   --all           Run all tests
echo   --lint          Run code linting
echo   --install-deps  Install test dependencies
echo   --help          Show this help
exit /b 0 
# Autonomous Diligence Cloud - Startup Script for PowerShell
# This script sets up and starts the server

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Autonomous Diligence Cloud" -ForegroundColor Cyan
Write-Host "  AI-Powered Document Intelligence" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9 or higher from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install/upgrade dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create necessary directories
if (-not (Test-Path "backend\uploads")) {
    New-Item -ItemType Directory -Path "backend\uploads" -Force | Out-Null
}
if (-not (Test-Path "data\vector_db")) {
    New-Item -ItemType Directory -Path "data\vector_db" -Force | Out-Null
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "  WARNING: .env file not found!" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Yellow
    Write-Host "1. Rename 'env_template.txt' to '.env'" -ForegroundColor Yellow
    Write-Host "2. Open .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Get your API key from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the server
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Starting server..." -ForegroundColor Green
Write-Host "  Access at: http://localhost:8002" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location backend
python main.py

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Server exited with an error" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}


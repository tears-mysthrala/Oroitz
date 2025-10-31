# Oroitz Build System for Windows
# Run with: .\build.ps1 <command>

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "help"
)

function Write-Help {
    Write-Host "Oroitz Build System for Windows" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\build.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  install       Install all dependencies"
    Write-Host "  install-min   Install minimal dependencies (no GUI)"
    Write-Host "  build         Build PyInstaller executables"
    Write-Host "  test          Run all tests"
    Write-Host "  test-core     Run core tests only"
    Write-Host "  test-ui       Run UI tests only"
    Write-Host "  lint          Run linting"
    Write-Host "  format        Format code"
    Write-Host "  fix           Auto-fix linting issues"
    Write-Host "  benchmark     Run benchmark"
    Write-Host "  clean         Clean build artifacts"
    Write-Host "  dist          Build and create distribution archives"
    Write-Host "  release       Full release build"
    Write-Host "  help          Show this help message"
}

function Invoke-Poetry {
    param([string]$Args)
    & poetry $Args.Split()
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Poetry command failed: poetry $Args"
        exit 1
    }
}

switch ($Command) {
    "help" {
        Write-Help
    }
    "install" {
        Write-Host "Installing all dependencies..." -ForegroundColor Green
        Invoke-Poetry "install --with dev"
        Write-Host "Fetching Volatility community plugins..." -ForegroundColor Green
        Invoke-Poetry "run python scripts/setup_volatility_plugins.py --dest vendor/volatility_plugins --update-env"
    }
    "install-min" {
        Write-Host "Installing minimal dependencies..." -ForegroundColor Green
        Invoke-Poetry "install"
        Write-Host "Fetching Volatility community plugins..." -ForegroundColor Green
        Invoke-Poetry "run python scripts/setup_volatility_plugins.py --dest vendor/volatility_plugins --update-env"
    }
    "build" {
        Write-Host "Building PyInstaller executables..." -ForegroundColor Green
        Invoke-Poetry "run python scripts/build_installers.py"
    }
    "test" {
        Write-Host "Running all tests..." -ForegroundColor Green
        Invoke-Poetry "run pytest tests/"
    }
    "test-core" {
        Write-Host "Running core tests only..." -ForegroundColor Green
        Invoke-Poetry "run pytest tests/core/ tests/cli/"
    }
    "test-ui" {
        Write-Host "Running UI tests only..." -ForegroundColor Green
        Invoke-Poetry "run pytest tests/ui/"
    }
    "lint" {
        Write-Host "Running linting..." -ForegroundColor Green
        Invoke-Poetry "run ruff check ."
    }
    "format" {
        Write-Host "Formatting code..." -ForegroundColor Green
        Invoke-Poetry "run black ."
    }
    "fix" {
        Write-Host "Auto-fixing linting issues..." -ForegroundColor Green
        Invoke-Poetry "run ruff check . --fix"
    }
    "benchmark" {
        Write-Host "Running benchmark..." -ForegroundColor Green
        Invoke-Poetry "run python tools/benchmark.py"
    }
    "clean" {
        Write-Host "Cleaning build artifacts..." -ForegroundColor Green
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist/, build/
        Get-ChildItem -Recurse -Include "*.spec" | Remove-Item -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Recurse -Include "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Recurse -Include "__pycache__" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
    "dist" {
        Write-Host "Building and creating distribution archives..." -ForegroundColor Green
        # First build
        Invoke-Poetry "run python scripts/build_installers.py"

        # Create archives
        Push-Location dist
        Get-ChildItem *.exe | ForEach-Object {
            $baseName = $_.BaseName
            $archiveName = "$baseName.tar.gz"
            & tar -czf $archiveName $_.Name
            Write-Host "Created $archiveName" -ForegroundColor Green
        }
        Pop-Location
    }
    "release" {
        Write-Host "Running full release build..." -ForegroundColor Green
        & $PSCommandPath -Command clean
        & $PSCommandPath -Command install
        & $PSCommandPath -Command test
        & $PSCommandPath -Command lint
        & $PSCommandPath -Command build
        & $PSCommandPath -Command dist
        Write-Host "Release build complete!" -ForegroundColor Green
        Write-Host "Executables and archives are in dist/" -ForegroundColor Cyan
    }
    default {
        Write-Error "Unknown command: $Command"
        Write-Host ""
        Write-Help
        exit 1
    }
}
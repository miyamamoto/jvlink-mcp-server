<#
.SYNOPSIS
    JVLink MCP Server の .mcpb バンドルをビルドするスクリプト

.DESCRIPTION
    Python依存関係をバンドルし、.mcpb ファイルを作成します。
    事前に npm install -g @anthropic-ai/mcpb が必要です。

.EXAMPLE
    .\build-bundle.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "=== JVLink MCP Server Bundle Builder ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check prerequisites
Write-Host "[1/5] Checking prerequisites..." -ForegroundColor Yellow

# Check npm/mcpb
$mcpbPath = Get-Command mcpb -ErrorAction SilentlyContinue
if (-not $mcpbPath) {
    Write-Host "  mcpb not found. Installing..." -ForegroundColor Gray
    npm install -g @anthropic-ai/mcpb
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install mcpb. Please install Node.js and run: npm install -g @anthropic-ai/mcpb"
        exit 1
    }
}
Write-Host "  mcpb: OK" -ForegroundColor Green

# Check Python
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Error "Python not found. Please install Python 3.11 or later."
    exit 1
}
Write-Host "  Python: OK" -ForegroundColor Green

# 2. Clean previous build
Write-Host ""
Write-Host "[2/5] Cleaning previous build..." -ForegroundColor Yellow

$libDir = Join-Path $PSScriptRoot "lib"
if (Test-Path $libDir) {
    Remove-Item -Recurse -Force $libDir
    Write-Host "  Removed old lib directory" -ForegroundColor Gray
}

$mcpbFiles = Get-ChildItem -Path $PSScriptRoot -Filter "*.mcpb" -ErrorAction SilentlyContinue
foreach ($file in $mcpbFiles) {
    Remove-Item -Force $file.FullName
    Write-Host "  Removed old $($file.Name)" -ForegroundColor Gray
}

Write-Host "  Clean: OK" -ForegroundColor Green

# 3. Install dependencies to lib directory
Write-Host ""
Write-Host "[3/5] Installing Python dependencies to lib/..." -ForegroundColor Yellow

New-Item -ItemType Directory -Path $libDir -Force | Out-Null

# Install dependencies
python -m pip install --target $libDir `
    "duckdb>=1.4.1" `
    "mcp[cli]>=1.21.0" `
    "pandas>=2.3.3" `
    "python-dotenv>=1.0.0" `
    --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    exit 1
}

# Remove unnecessary files from lib to reduce size
Write-Host "  Cleaning up unnecessary files..." -ForegroundColor Gray
Get-ChildItem -Path $libDir -Recurse -Include "__pycache__", "*.pyc", "*.pyo", "tests", "test" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $libDir -Recurse -Include "*.dist-info" -Directory | ForEach-Object {
    # Keep only METADATA and top_level.txt
    Get-ChildItem -Path $_.FullName -Exclude "METADATA", "top_level.txt", "RECORD" | Remove-Item -Force -ErrorAction SilentlyContinue
}

$libSize = (Get-ChildItem -Path $libDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  Dependencies installed: $([math]::Round($libSize, 2)) MB" -ForegroundColor Green

# 4. Update manifest.json with lib path
Write-Host ""
Write-Host "[4/5] Updating manifest.json..." -ForegroundColor Yellow

$manifestPath = Join-Path $PSScriptRoot "manifest.json"
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

# Update PYTHONPATH to include lib directory
$manifest.server.mcp_config.env.PYTHONPATH = "`${__dirname}/lib;`${__dirname}/src"

$manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath -Encoding UTF8
Write-Host "  Manifest updated: OK" -ForegroundColor Green

# 5. Create .mcpb bundle
Write-Host ""
Write-Host "[5/5] Creating .mcpb bundle..." -ForegroundColor Yellow

mcpb pack $PSScriptRoot

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create .mcpb bundle"
    exit 1
}

# Find the created bundle
$bundle = Get-ChildItem -Path $PSScriptRoot -Filter "*.mcpb" | Select-Object -First 1
if ($bundle) {
    $bundleSize = $bundle.Length / 1MB
    Write-Host ""
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Bundle: $($bundle.Name)" -ForegroundColor Cyan
    Write-Host "Size: $([math]::Round($bundleSize, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation:" -ForegroundColor Yellow
    Write-Host "  Double-click the .mcpb file to install in Claude Desktop" -ForegroundColor Gray
    Write-Host "  Or drag and drop to Claude Desktop window" -ForegroundColor Gray
} else {
    Write-Warning "Bundle file not found. Check mcpb output above."
}

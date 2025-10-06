#!/usr/bin/env powershell
<#
.SYNOPSIS
University Application Document Generator - PowerShell Script

.DESCRIPTION
Generates customized CV and SOP documents for university applications

.PARAMETER Action
The action to perform: list, all, or a specific school_id

.EXAMPLE
.\generate.ps1 list
.\generate.ps1 all
.\generate.ps1 taltech

.NOTES
Author: Pei-Chen Lee
Version: 1.0.0
#>

param(
    [Parameter(Mandatory=$false, Position=0)]
    [string]$Action = ""
)

# Get script directory and navigate to build_scripts
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "build_scripts")

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Using Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
try {
    python -c "import yaml" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Installing Python dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
} catch {
    Write-Host "❌ Error: Failed to check or install dependencies" -ForegroundColor Red
    exit 1
}

# Handle different actions
switch ($Action) {
    "" {
        Write-Host "🎓 University Application Document Generator" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor White
        Write-Host "  .\generate.ps1 list          - List all available schools" -ForegroundColor Gray
        Write-Host "  .\generate.ps1 all           - Generate documents for all active schools" -ForegroundColor Gray
        Write-Host "  .\generate.ps1 taltech       - Generate documents for TalTech" -ForegroundColor Gray
        Write-Host "  .\generate.ps1 aalto         - Generate documents for Aalto University" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Available Schools:" -ForegroundColor White
        python generate_docs.py --list
    }
    "list" {
        python generate_docs.py --list
    }
    "all" {
        Write-Host "🚀 Generating documents for all active schools..." -ForegroundColor Cyan
        python generate_docs.py --all
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Document generation completed successfully!" -ForegroundColor Green
            Write-Host "📁 Check the 'final_applications' directory for generated files." -ForegroundColor Yellow
        }
    }
    default {
        Write-Host "🎯 Generating documents for school: $Action" -ForegroundColor Cyan
        python generate_docs.py --school $Action
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Document generation completed for $Action!" -ForegroundColor Green
            Write-Host "📁 Check the 'final_applications\$Action' directory for generated files." -ForegroundColor Yellow
        } else {
            Write-Host "❌ Error: Failed to generate documents for $Action" -ForegroundColor Red
            Write-Host "💡 Use '.\generate.ps1 list' to see available schools" -ForegroundColor Yellow
        }
    }
}

# Return to original directory
Set-Location $ScriptDir
